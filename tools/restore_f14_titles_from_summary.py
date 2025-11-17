import json
from pathlib import Path

PATH = Path("data/f14_proposals_ja.json")


def main():
    # バックアップ作成（念のため）
    backup = PATH.with_suffix(".before_title_fix.json")
    backup.write_text(PATH.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"📦 Backup created: {backup}")

    data = json.loads(PATH.read_text(encoding="utf-8"))

    fixed_count = 0

    for p in data:
        t = (p.get("title_ja") or "").strip()
        s = (p.get("summary_ja") or "").strip()

        # title_ja が 空 or --- のときだけ対象にする
        if t in ("", "---", "—") and s:
            # summary_ja を行ごとに分解
            lines = [line.strip() for line in s.splitlines()]
            # 空行を除く
            non_empty = [line for line in lines if line]

            if not non_empty:
                continue

            # 最初の非空行をタイトル候補に
            new_title = non_empty[0]

            # 残りの行をサマリーとして再構成
            rest_lines = non_empty[1:]
            if rest_lines:
                new_summary = "\n".join(rest_lines)
            else:
                new_summary = ""

            print(f"Fixing {p.get('proposal_id')}:")
            print("  OLD title_ja:", repr(t))
            print("  NEW title_ja:", repr(new_title))

            p["title_ja"] = new_title
            p["summary_ja"] = new_summary

            fixed_count += 1

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 修正完了: {fixed_count} 件の title_ja を summary_ja から復元しました")


if __name__ == "__main__":
    main()
