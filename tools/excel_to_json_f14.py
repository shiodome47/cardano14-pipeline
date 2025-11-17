import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
XLSX_FILE = DATA_DIR / "f14_results.xlsx"
OUTPUT_FILE = DATA_DIR / "f14_results_raw.json"

# ここは「集計用のタブ名」など、もしあれば除外しておく
EXCLUDE_SHEETS = [
    "TEMPLATE",  # 実際のテンプレートタブ名に合わせて
    "Template",  # 要らないタブ名をここに列挙
]


def main():
    if not XLSX_FILE.exists():
        raise FileNotFoundError(f"Excel ファイルが見つかりません: {XLSX_FILE}")

    xls = pd.ExcelFile(XLSX_FILE)

    all_rows = []

    for sheet_name in xls.sheet_names:
        if sheet_name in EXCLUDE_SHEETS:
            continue

        df = xls.parse(sheet_name)

        # 空行をざっくり除外
        df = df.dropna(how="all")
        if df.empty:
            continue

        # 行ごとに dict にして追加
        for _, row in df.iterrows():
            rec = row.to_dict()

            # どのタブのデータかを埋めておく
            rec["Challenge"] = sheet_name

            all_rows.append(rec)

    OUTPUT_FILE.write_text(
        json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✅ {len(all_rows)} 件を {OUTPUT_FILE} に書き出しました")


if __name__ == "__main__":
    main()
