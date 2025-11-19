# tools/format_about_with_llm.py

import json
import time
from pathlib import Path

from openai import OpenAI  # pip install openai>=1.0.0

client = OpenAI()  # API key は環境変数から読む

DATA_DIR = Path("data")
INPUT_FILE = DATA_DIR / "f14_proposals_en.json"
BACKUP_FILE = DATA_DIR / "f14_proposals_en.before_structured.json"

# 一度に新しく整形する最大件数
MAX_PROPOSALS = 3

SYSTEM_PROMPT = """You are an assistant that restructures long, messy proposal form text
from Project Catalyst into a clean, readable Markdown document.
You MUST keep the meaning accurate, but improve structure and readability.
"""

USER_PROMPT_PREFIX = """
以下の英語テキストは、Project Catalyst の提案フォームから抜き出した内容です。
意味は変えずに、見やすい要約ドキュメントに整形してください。

出力フォーマットのルールは次の通りです：

最初に「## 📌 Proposal Overview」セクションを作り、

- Category
- Title
- Requested Budget
- Duration
- Original Language
- Open Source (License)

を箇条書きでまとめる。

次に、以下の見出しを順番に作る：

## 1. Problem Statement
## 2. Proposed Solution
## 3. Collaborations & Team
## 4. Expected Impact
## 5. Key Performance Metrics (KPIs)
## 6. Milestones (Summary Table)
## 7. Budget Breakdown
## 8. Value for Money

内容は要約＋整理を優先し、箇条書きや短い段落にまとめる。
Milestones は Markdown 表形式にする。

では次のテキストを整えてください：
"""


def build_wall_text(item: dict) -> str:
    """
    proposal の各 *_en フィールドから '壁テキスト' を組み立てる。

    - title_en / summary_en / about_structured_en は除外
    - 残りの *_en をまとめて LLM に投げる
    """
    parts: list[str] = []

    # 末尾が _en のキーを総ざらい（メタっぽいものは除外）
    ignore_keys = {"title_en", "summary_en", "about_structured_en"}
    en_keys: list[str] = []

    for key, value in item.items():
        if not isinstance(value, str):
            continue
        if not key.endswith("_en"):
            continue
        if key in ignore_keys:
            continue
        if not value.strip():
            continue
        en_keys.append(key)

    if not en_keys:
        return ""

    # 安定のため、ソートしてから結合
    for key in sorted(en_keys):
        label_base = key[:-3]  # "_en" を取る
        # 例: "problem_statement" → "Problem Statement"
        label = label_base.replace("_", " ").title()
        val = item[key].strip()
        parts.append(f"{label}:\n{val}\n")

    return "\n".join(parts).strip()


def call_llm(wall_text: str) -> str:
    """LLM で整形された Markdown を生成する."""
    prompt = USER_PROMPT_PREFIX + "\n" + wall_text

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    return resp.choices[0].message.content.strip()


def main():
    print("[format_about] START")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    # JSON 読み込み
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # 初回のみバックアップ
    if not BACKUP_FILE.exists():
        with BACKUP_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[format_about] Backup created: {BACKUP_FILE}")

    updated = 0

    for item in data:
        pid = item.get("proposal_id")

        # すでに structured があるならスキップ（再実行に備えた設計）
        if item.get("about_structured_en"):
            print(f"- {pid}: already has about_structured_en, skip")
            continue

        wall_text = build_wall_text(item)

        # 入力になるテキストが何もなければスキップ
        if not wall_text:
            print(f"- {pid}: no usable *_en fields, skip")
            continue

        print(f"- {pid}: calling LLM...")

        try:
            formatted = call_llm(wall_text)
        except Exception as e:
            print(f"  ❌ error: {e}")
            continue

        item["about_structured_en"] = formatted
        updated += 1

        time.sleep(1)

        if updated >= MAX_PROPOSALS:
            print(f"[format_about] Reached MAX_PROPOSALS={MAX_PROPOSALS}, stopping.")
            break

    # JSON 書き戻し
    with INPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[format_about] Done. Updated {updated} proposals.")


if __name__ == "__main__":
    main()
