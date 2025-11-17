import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

DATA_DIR = Path("data")
JSON_FILE = DATA_DIR / "f14_proposals_en.json"


def fetch_section(soup, title):
    h2 = soup.find("h2", string=lambda x: x and title.lower() in x.lower())
    if not h2:
        return ""
    # 次の兄弟 <div>
    content = []
    for tag in h2.find_all_next():
        if tag.name == "h2":  # 次のセクションに来たら終わり
            break
        if tag.name in ["p", "div"]:
            text = tag.get_text(strip=True)
            if text:
                content.append(text)
    return "\n\n".join(content)


def scrape(url):
    print(f"Fetching: {url}")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    problem = fetch_section(soup, "Problem")
    solution = fetch_section(soup, "Solution")
    about = fetch_section(soup, "About this idea")
    team = fetch_section(soup, "Team")

    return {
        "problem_en": problem,
        "solution_en": solution,
        "about_en": about,
        "team_en": team,
    }


def main():
    target_id = "F14-0001"  # ←まず1件でテスト（後で全件対応）
    url = input("原文URLを入力してください: ").strip()

    scraped = scrape(url)

    print("\nScraped result:\n", scraped, "\n")

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
