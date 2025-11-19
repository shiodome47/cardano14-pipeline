# tools/generate_multilang_about.py

import json
import time
from pathlib import Path
from openai import OpenAI

# OPENAI_API_KEY は環境変数で設定しておくこと
client = OpenAI()

SRC = Path("data/f14_proposals_en.json")
DST = Path("data/f14_proposals_multi.json")

# ★テスト用：何件まで処理するか（Noneなら全件）
MAX_ITEMS = 3


def build_prompt(about_en: str) -> str:
    """about_structured_en から、多言語 about_* を生成するためのプロンプト"""
    return f"""
You are a translator and simplifier.

Input is MARKDOWN in English that explains a Cardano Catalyst proposal
under the key `about_structured_en`.

Please:

1. Translate it into natural Japanese for adults.
2. Create an Easy Japanese version (やさしい日本語, ELP style):
   - short sentences
   - simple words
   - keep headings
   - briefly explain difficult words
3. Create an Easy Spanish version (Español fácil, ELP style):
   - short sentences
   - simple words
   - keep headings
   - briefly explain difficult words

Return JSON with this exact shape:

{{
  "ja": "MARKDOWN in Japanese",
  "ja_elp": "MARKDOWN in Easy Japanese",
  "es_elp": "MARKDOWN in Easy Spanish"
}}

Do NOT include any keys other than ja, ja_elp, es_elp.
Do NOT wrap the JSON in code fences.
Do NOT explain the JSON, just output raw JSON.

Here is `about_structured_en` in Markdown.
The content is between the markers [ABOUT_START] and [ABOUT_END].

[ABOUT_START]
{about_en}
[ABOUT_END]
"""


def translate_about(about_en: str) -> dict:
    """OpenAI API (chat.completions) を使って、多言語版 about_* を JSON で返す"""
    prompt = build_prompt(about_en)

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = resp.choices[0].message.content.strip()
    # build_prompt 側で「生の JSON だけ返して」と指示しているのでそのままパース
    return json.loads(content)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")

    data = json.loads(SRC.read_text(encoding="utf-8"))

    total = len(data)
    print(f"Loaded {total} proposals from {SRC}")

    for i, proposal in enumerate(data):
        about_en = (proposal.get("about_structured_en") or "").strip()
        if not about_en:
            # 英語版がないものはスキップ
            continue

        # すでに3つそろっていたらスキップ（再実行に備えて）
        if (
            proposal.get("about_structured_ja")
            and proposal.get("about_structured_ja_elp")
            and proposal.get("about_structured_es_elp")
        ):
            continue

        pid = proposal.get("proposal_id") or f"index:{i}"
        print(f"[{i+1}/{total}] {pid} → translating...")

        try:
            tr = translate_about(about_en)
        except Exception as e:
            print(f"  !! error on {pid}: {e}")
            # エラーになったものは後から手で見られるようにしておく
            proposal.setdefault("_multilang_error", str(e))
            continue

        proposal["about_structured_ja"] = tr.get("ja", "").strip()
        proposal["about_structured_ja_elp"] = tr.get("ja_elp", "").strip()
        proposal["about_structured_es_elp"] = tr.get("es_elp", "").strip()

        # 10件ごとに途中保存（長時間バッチ対策）
        if (i + 1) % 10 == 0:
            DST.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  saved checkpoint → {DST}")

        # レート制御（必要に応じて調整）
        time.sleep(0.5)

        # ★テスト件数に達したら終了
        if MAX_ITEMS is not None and (i + 1) >= MAX_ITEMS:
            print(f"Reached MAX_ITEMS={MAX_ITEMS}, stopping early for test.")
            break

    # 最終保存
    DST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("All done →", DST)


if __name__ == "__main__":
    main()
