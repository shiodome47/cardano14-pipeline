import json
from pathlib import Path

INPUT = Path("data/f14_proposals_ja.json")
OUTPUT = Path("data/f14_proposals_ja_clean.json")


def clean_text(s: str) -> str:
    if not isinstance(s, str):
        return s
    # 全角スペース（U+3000）を削除
    return s.replace("\u3000", "")


def main():
    with INPUT.open("r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []
    for p in data:
        p["title_ja"] = clean_text(p.get("title_ja", ""))
        p["summary_ja"] = clean_text(p.get("summary_ja", ""))
        cleaned.append(p)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"✨ Cleaned JSON saved → {OUTPUT}")


if __name__ == "__main__":
    main()
