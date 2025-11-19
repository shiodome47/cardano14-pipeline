# tools/scrape_one_f14.py
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("data")
JSON_FILE = DATA_DIR / "f14_proposals_en.json"


def fetch_section(soup, title: str) -> str:
    """
    h2 見出しから「同じレベルの兄弟」だけを拾って、
    ・次の h2 が来たら終了
    ・空行は捨てる
    ・全く同じ文は 1 回だけ

    ついでに、投票サマリーやフッターのような
    「Total to date…」「Follow us…」などは除外する。
    """
    h2 = soup.find("h2", string=lambda x: x and title.lower() in x.lower())
    if not h2:
        return ""

    # ゴミとして弾きたいテキストのプレフィックス
    unwanted_prefixes = (
        "Total to date",  # 投票カード
        "View current challenges",  # フッター
        "Sign up to receive news",  # フッター
        "We collect personal data",  # フッター
        "Follow us",  # フッター
    )

    parts = []
    seen = set()

    # 同じ階層の next_siblings だけを見る
    for sib in h2.next_siblings:
        name = getattr(sib, "name", None)

        # 次の h2 が来たらこのセクションは終わり
        if name == "h2":
            break

        if name in {"p", "div"}:
            text = sib.get_text(" ", strip=True)
            if not text:
                continue
            if any(text.startswith(pref) for pref in unwanted_prefixes):
                continue
            if text in seen:
                continue
            seen.add(text)
            parts.append(text)

    return "\n\n".join(parts)


def scrape_full_text(soup: BeautifulSoup) -> str:
    """
    フォーム全体を「壁テキスト」として1本にまとめる。

    - data-testid="question-answer" ブロックがあれば優先して使う
    - なければ main 全体 → ページ全体の順でフォールバック
    - フッターやニュース購読などの不要テキストは除外
    - 同じ行は 1 回だけ
    """
    blocks = []

    # 1) Catalyst の Q&A ブロックっぽいところを探す
    qa_blocks = soup.find_all(attrs={"data-testid": "question-answer"})

    if qa_blocks:
        for block in qa_blocks:
            # 質問タイトル (h2/h3/h4)
            q_el = block.find(["h2", "h3", "h4"])
            # 回答部分（data-testid="answer" があればそこ、なければブロック全体）
            a_el = block.find(attrs={"data-testid": "answer"}) or block

            q_text = q_el.get_text(" ", strip=True) if q_el else ""
            a_text = a_el.get_text("\n", strip=True)

            if not a_text:
                continue

            if q_text:
                blocks.append(f"## {q_text}")
            blocks.append(a_text)

        raw_text = "\n\n".join(blocks)
    else:
        # 2) フォールバック：main → ページ全体
        main = soup.find("main")
        if main:
            raw_text = main.get_text("\n", strip=True)
        else:
            raw_text = soup.get_text("\n", strip=True)

    # 3) フッターなどを掃除しつつ、重複行を削除
    unwanted_starts = (
        "View current challenges",
        "Sign up to receive news",
        "We collect personal data",
        "Follow us",
        "Thank you for subscribing",
    )

    lines = []
    seen_lines = set()

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(line.startswith(pref) for pref in unwanted_starts):
            continue
        if line in seen_lines:
            continue
        seen_lines.add(line)
        lines.append(line)

    return "\n\n".join(lines)


def scrape(url: str) -> dict:
    print(f"Fetching: {url}")
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    problem = fetch_section(soup, "Problem")
    solution = fetch_section(soup, "Solution")
    about = fetch_section(soup, "About this idea")
    team = fetch_section(soup, "Team")
    full_text = scrape_full_text(soup)

    return {
        "problem_en": problem,
        "solution_en": solution,
        "about_en": about,
        "team_en": team,
        "full_text_en": full_text,  # ★ LLM 用の壁テキスト
    }


def main():
    target_id = "F14-0001"  # ←まず1件でテスト（後で全件対応）
    url = input("原文URLを入力してください: ").strip()

    scraped = scrape(url)

    print(
        "\nScraped result:\n", json.dumps(scraped, indent=2, ensure_ascii=False), "\n"
    )

    # 既存JSON読み込み
    with JSON_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # 対象 proposal を更新
    for item in data:
        if item["proposal_id"] == target_id:
            item.update(scraped)
            break
    else:
        print("❌ proposal_id が見つかりません:", target_id)
        return

    # 書き戻し
    with JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ updated {target_id} → {JSON_FILE}")


if __name__ == "__main__":
    main()
