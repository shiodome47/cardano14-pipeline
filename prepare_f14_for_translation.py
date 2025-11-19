import json
from pathlib import Path

DATA_DIR = Path("data")

RAW_FILE = DATA_DIR / "f14_results_raw.json"
OUTPUT_FILE = DATA_DIR / "f14_proposals_en.json"

# ❗ 元データ由来の列名（実際のExcel/JSONに合わせて書き換える）
# 例: "Title" / "Proposal Title" / "Challenge Name"
TITLE_COL = "Proposal"  # 各タブ共通の Proposal 列
CHALLENGE_COL = "Challenge"  # excel_to_json_f14.py でシート名から付けた列
REQUESTED_COL = "Requested Ada"  # 要求額

STATUS_COL = "Status"  # FUNDED / NOT FUNDED など
VOTES_CAST_COL = "Votes cast"  # 投票数
YES_COL = "Yes"  # Yes 票総量（ADA）
ABSTAIN_COL = "Abstain"  # 棄権票総量（ADA）
APPROVAL_COL = "Meets approval threshold"  # YES / NO
FUND_DEPLETION_COL = "Fund depletion"  # 残り予算など
NOT_FUNDED_REASON_COL = "Reason for not funded status"  # 不採択理由
# これをシート側に追加しておくと、Proposal のリンクURLも拾える
URL_COL = "Proposal URL"  # ← Excel にこの列を作る運用


def norm_text(value) -> str:
    """
    Excel 由来の値を安全にテキスト化する:
    - None → ""
    - NaN（float でも文字列でも）→ ""
    - それ以外は str() して strip() したものを返す
    """
    if value is None:
        return ""
    s = str(value).strip()
    if s.lower() == "nan":
        return ""
    return s


def norm_int(value) -> str:
    """整数系（投票数やADA量）を '585' や '256,533,420' 形式に整える。"""
    if value is None:
        return ""

    # 数値ならそのまま整形
    if isinstance(value, (int, float)):
        return f"{int(value):,}"

    # 文字列など
    s = str(value).strip()
    if not s or s.lower() == "nan":
        return ""
    try:
        num = int(float(s))
        return f"{num:,}"
    except ValueError:
        return s


def norm_ada(value) -> str:
    """ADA 金額を '₳739,000' のような書式に整える."""
    if value is None:
        return ""
    s = str(value).strip()
    if s.lower() == "nan" or s == "":
        return ""
    # すでに "₳" 付きならそのまま返す
    if s.startswith("₳"):
        return s
    try:
        num = float(s)
        return f"₳{int(num):,}"
    except ValueError:
        # 数字に変換できない場合はそのまま返す
        return s


def main():
    print("[prepare_f14] START")
    print(f"[prepare_f14] RAW_FILE = {RAW_FILE}")
    print(f"[prepare_f14] RAW_FILE.exists() = {RAW_FILE.exists()}")

    if not RAW_FILE.exists():
        raise FileNotFoundError(f"raw JSON が見つかりません: {RAW_FILE}")

    with RAW_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    print(f"[prepare_f14] loaded raw len = {len(raw)}")

    proposals = []
    for i, row in enumerate(raw):
        # タイトル
        title = norm_text(row.get(TITLE_COL, ""))
        if not title:
            # タイトルが空なら無視（合計行など）
            continue

        # チャレンジ名（シート名を入れておいた列）
        challenge = norm_text(row.get(CHALLENGE_COL, "")) if CHALLENGE_COL else ""

        # 要求額（"₳739,000" のような文字列に整形）
        requested = norm_ada(row.get(REQUESTED_COL, "")) if REQUESTED_COL else ""

        # 追加メタデータ
        status = norm_text(row.get(STATUS_COL, "")) if STATUS_COL else ""
        votes_cast = norm_int(row.get(VOTES_CAST_COL, "")) if VOTES_CAST_COL else ""
        yes_amount = norm_int(row.get(YES_COL, "")) if YES_COL else ""
        abstain_amount = norm_int(row.get(ABSTAIN_COL, "")) if ABSTAIN_COL else ""
        meets_approval_threshold = (
            norm_text(row.get(APPROVAL_COL, "")) if APPROVAL_COL else ""
        )
        fund_depletion = (
            norm_int(row.get(FUND_DEPLETION_COL, "")) if FUND_DEPLETION_COL else ""
        )
        not_funded_reason = (
            norm_text(row.get(NOT_FUNDED_REASON_COL, ""))
            if NOT_FUNDED_REASON_COL
            else ""
        )
        proposal_url = norm_text(row.get(URL_COL, "")) if URL_COL else ""

        proposals.append(
            {
                "proposal_id": f"F14-{i+1:04d}",
                "fund": 14,
                "challenge": challenge,
                "title_en": title,
                "summary_en": "",
                "full_text_en": "",
                "requested_ada": requested,
                "status": status,
                "votes_cast": votes_cast,
                "yes_amount": yes_amount,
                "abstain_amount": abstain_amount,
                "meets_approval_threshold": meets_approval_threshold,
                "fund_depletion": fund_depletion,
                "not_funded_reason": not_funded_reason,
                "proposal_url": proposal_url,
            }
        )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(proposals, f, ensure_ascii=False, indent=2)

    print(f"✅ 整形完了: {len(proposals)} 件 → {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        traceback.print_exc()
