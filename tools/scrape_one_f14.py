# tools/scrape_one_f14.py
import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("data")
JSON_FILE = DATA_DIR / "f14_proposals_en.json"

# 一度にスクレイプする最大件数（テスト用）
MAX_ITEMS = 1200


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

    unwanted_prefixes = (
        "Total to date",
        "View current challenges",
        "Sign up to receive news",
        "We collect personal data",
        "Follow us",
    )

    parts = []
    seen = set()

    for sib in h2.next_siblings:
        name = getattr(sib, "name", None)

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
    """
    blocks = []

    qa_blocks = soup.find_all(attrs={"data-testid": "question-answer"})

    if qa_blocks:
        for block in qa_blocks:
            q_el = block.find(["h2", "h3", "h4"])
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
        main = soup.find("main")
        if main:
            raw_text = main.get_text("\n", strip=True)
        else:
            raw_text = soup.get_text("\n", strip=True)

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
    print(f"  Fetching: {url}")
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
        "full_text_en": full_text,
    }


def main():
    print("[scrape_f14] START")

    if not JSON_FILE.exists():
        raise FileNotFoundError(JSON_FILE)

    with JSON_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0

    for item in data:
        pid = item.get("proposal_id")
        url = item.get("proposal_url")

        # 過去にスクレイプエラーを記録していたらスキップ
        if item.get("_scrape_error"):
            print(f"- {pid}: has _scrape_error, skip")
            continue

        if not url:
            print(f"- {pid}: no proposal_url, skip")
            continue

        # すでに full_text_en があればスキップ（再実行に備えた設計）
        if item.get("full_text_en"):
            print(f"- {pid}: already has full_text_en, skip")
            continue

        print(f"- {pid}: scraping...")
        try:
            scraped = scrape(url)
        except Exception as e:
            print(f"  ❌ error while scraping {pid}: {e}")
            # 次回以降は自動スキップできるようメモ
            item["_scrape_error"] = str(e)
            continue

        item.update(scraped)
        updated += 1

        # サイトへの負荷を下げるため、少し待つ
        time.sleep(1)

        if updated >= MAX_ITEMS:
            print(f"[scrape_f14] Reached MAX_ITEMS={MAX_ITEMS}, stopping.")
            break

    with JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[scrape_f14] Done. Updated {updated} proposals.")


if __name__ == "__main__":
    main()
