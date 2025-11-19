#!/usr/bin/env python
import json
from pathlib import Path

path = Path("data/f14_proposals_ja.json")
data = json.loads(path.read_text(encoding="utf-8"))

# { "proposals": [...] } 形式にも対応
if isinstance(data, dict) and "proposals" in data:
    proposals = data["proposals"]
else:
    proposals = data

print(f"Total proposals: {len(proposals)}")

# 最初の1件だけ中身を見る
p = proposals[0]
print("Keys:", sorted(p.keys()))
print("\nSample values:")
for k, v in p.items():
    if isinstance(v, str) and len(v) > 120:
        print(f"\n--- {k} (len={len(v)}) ---")
        print(v[:400], "...\n")
