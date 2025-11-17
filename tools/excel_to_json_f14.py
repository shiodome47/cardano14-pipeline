# excel_to_json_f14.py

import json
from pathlib import Path

from openpyxl import load_workbook

DATA_DIR = Path("data")

# ❗ここを実際のファイル名に合わせてください
# 例: f14_results.xlsx / fund14_results.xlsx など
EXCEL_FILE = DATA_DIR / "f14_results.xlsx"

OUTPUT_FILE = DATA_DIR / "f14_results_raw.json"

# テンプレートタブなど、読み飛ばしたいシート名
SKIP_SHEETS = {"Template", "テンプレート"}


def cell_text(value):
    """Excelセルの値をJSON向けに安全に文字列/数値として返す."""
    # openpyxlなら NaN は基本出てこないが、念のため
    if value is None:
        return None
    return value


def sheet_to_rows(ws):
    """1つのシートを [{'col': value, ...}, ...] に変換する."""
    rows = list(ws.rows)
    if not rows:
        return []

    # 1行目をヘッダとして扱う
    headers = [str(c.value).strip() if c.value is not None else "" for c in rows[0]]

    # Proposal 列のインデックスを特定（ハイパーリンク用）
    try:
        proposal_col_idx = headers.index("Proposal")  # 0-based
    except ValueError:
        proposal_col_idx = None

    data_rows = []
    for r_idx, row in enumerate(rows[1:], start=2):  # 2行目以降がデータ
        row_dict = {}
        empty_row = True

        for c_idx, cell in enumerate(row):
            key = headers[c_idx]
            if not key:
                continue

            value = cell_text(cell.value)
            if value is not None and value != "":
                empty_row = False

            row_dict[key] = value

        if empty_row:
            continue

        # シート名を Challenge として追加（後で prepare_f14 側で使う）
        row_dict["Challenge"] = ws.title

        # Proposal のハイパーリンクを拾う
        if proposal_col_idx is not None:
            cell = row[proposal_col_idx]
            url = ""
            if cell.hyperlink is not None and cell.hyperlink.target:
                url = cell.hyperlink.target
            row_dict["Proposal URL"] = url

        data_rows.append(row_dict)

    return data_rows


def main():
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"Excel ファイルが見つかりません: {EXCEL_FILE}")

    print(f"[excel_to_json_f14] loading: {EXCEL_FILE}")
    wb = load_workbook(EXCEL_FILE, data_only=True)

    all_rows = []
    for ws in wb.worksheets:
        if ws.title in SKIP_SHEETS:
            print(f"[excel_to_json_f14] skip sheet: {ws.title}")
            continue

        print(f"[excel_to_json_f14] reading sheet: {ws.title}")
        rows = sheet_to_rows(ws)
        print(f"[excel_to_json_f14]  -> {len(rows)} rows")
        all_rows.extend(rows)

    print(f"[excel_to_json_f14] total rows: {len(all_rows)}")

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=2)

    print(f"✅ Excel → JSON 変換完了: {len(all_rows)} 件 → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
