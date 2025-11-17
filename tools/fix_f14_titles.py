import json
from pathlib import Path

path = Path("data/f14_proposals_ja.json")

# バックアップ推奨
backup = path.with_suffix(".backup.json")
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
print(f"📦 Backup created: {backup}")

data = json.loads(path.read_text(encoding="utf-8"))

for p in data:
    title_ja = p.get("title_ja", "")
    if "\n" in title_ja:
        first, rest = title_ja.split("\n", 1)
        first = first.strip()
        rest = rest.strip()

        print(f"Fixing {p.get('proposal_id')}:")
        print("  OLD title_ja:", repr(title_ja))
        print("  NEW title_ja:", repr(first))

        # 1行目だけを title_ja に残す
        p["title_ja"] = first

        # 2行目以降を summary_ja に逃がす
        if rest:
            if p.get("summary_ja"):
                p["summary_ja"] = rest + "\n\n" + p["summary_ja"]
            else:
                p["summary_ja"] = rest

path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ 修正完了: data/f14_proposals_ja.json を更新しました")
