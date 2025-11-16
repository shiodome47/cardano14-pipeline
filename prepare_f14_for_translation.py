import json
from pathlib import Path

DATA_DIR = Path("data")

RAW_FILE = DATA_DIR / "f14_results_raw.json"
OUTPUT_FILE = DATA_DIR / "f14_proposals_en.json"

# ❗ CSV由来のタイトル列の名前（実際のCSVに合わせて書き換える）
# 例： "Title" / "Proposal Title" / "Challenge Name"
TITLE_COL = "Proposal"  # ← 今の raw JSON を見て、ここを合わせればOK
CHALLENGE_COL = None  # challenge列があれば使う。なければ "" にする。
REQUESTED_COL = "Requested Ada"  # なければ空欄にしてOK


def main():
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"raw JSON が見つかりません: {RAW_FILE}")

    with RAW_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    proposals = []
    for i, row in enumerate(raw):
        # タイトル
        title = row.get(TITLE_COL, "").strip()
        if not title:
            # タイトルが空なら無視（合計行など）
            continue

        # チャレンジ名（今回はCSVに列がないので常に空文字）
        if CHALLENGE_COL:
            challenge = row.get(CHALLENGE_COL, "").strip()
        else:
            challenge = ""

        # 要求額（"₳739,000" のような文字列のまま残しておく）
        if REQUESTED_COL:
            requested = row.get(REQUESTED_COL, "").strip()
        else:
            requested = ""

        proposals.append(
            {
                "proposal_id": f"F14-{i+1:04d}",
                "fund": 14,
                "challenge": challenge,
                "title_en": title,
                "summary_en": "",
                "requested_ada": requested,
            }
        )
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(proposals, f, ensure_ascii=False, indent=2)

    print(f"✅ 整形完了: {len(proposals)} 件 → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
