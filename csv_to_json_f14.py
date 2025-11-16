import csv
import json
from pathlib import Path

# data ディレクトリの中の CSV を読む前提
DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "f14_results.csv"  # ← ここに実際のファイル名を合わせてね
OUTPUT_FILE = DATA_DIR / "f14_results_raw.json"  # 生のJSON出力先


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV が見つかりません: {CSV_FILE}")

    print(f"📥 読み込み: {CSV_FILE}")

    rows = []
    # utf-8-sig にしておくと先頭のBOM問題を避けやすい
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # row は {"column_name": "value", ...} という dict
            rows.append(row)

    print(f"✅ {len(rows)} 件の行を読み込みました。")

    # そのまま JSON に書き出し
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    print(f"💾 JSON に保存しました: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
