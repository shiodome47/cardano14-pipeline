import json
from pathlib import Path
import os

from openai import OpenAI

# OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY が環境変数に設定されていません。export してください。"
    )

client = OpenAI(api_key=api_key)

DATA_DIR = Path("data")
INPUT_FILE = DATA_DIR / "f14_proposals_en.json"
OUTPUT_FILE = DATA_DIR / "f14_proposals_ja.json"


def translate_title(text: str) -> str:
    """Translate a proposal TITLE into concise Japanese (1行だけ)."""
    prompt = (
        "You are translating a Project Catalyst proposal TITLE into Japanese.\n"
        "Return ONLY one concise Japanese title.\n"
        "Do NOT add any greeting, explanation, or extra sentences.\n"
        "Output must be a single line title only.\n\n"
        f"TITLE:\n{text}\n"
    )

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return res.choices[0].message.content.strip()


def translate_summary(text: str) -> str:
    """Translate proposal summary/description into Japanese."""
    prompt = (
        "You are a translator for the Cardano community in Japan.\n"
        "Translate the following Project Catalyst proposal summary into natural Japanese.\n"
        "Target readers are Cardano holders and community members.\n"
        "Keep it clear and respectful. You MAY be slightly explanatory, but avoid being too long.\n\n"
        f"---\n{text}\n---"
    )

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return res.choices[0].message.content.strip()


def main():
    # 1) Load input JSON（英語側）
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        proposals = json.load(f)

    # 2) 既存の日本語JSONがあれば読み込んで再利用
    existing_by_id: dict[str, dict] = {}
    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open("r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
                for item in existing:
                    pid = item.get("proposal_id")
                    if pid:
                        existing_by_id[pid] = item
            except Exception:
                # 壊れていても無視して新規生成
                existing_by_id = {}

    translated = []
    for p in proposals:
        pid = p.get("proposal_id")
        title_en = p.get("title_en", "")
        summary_en = p.get("summary_en", "")

        # すでに翻訳済みならそれを使う
        old = existing_by_id.get(pid) if pid else None
        if old and old.get("title_ja"):
            title_ja = old.get("title_ja", "")
            # summary_en が空なら古い summary_ja をそのまま使う
            if summary_en:
                summary_ja = old.get("summary_ja", "")
            else:
                summary_ja = old.get("summary_ja", "")
            print(f"Reuse translation: {pid} - {title_en}")
        else:
            print(f"Translating: {pid} - {title_en}")
            title_ja = translate_text(title_en) if title_en else ""
            summary_ja = translate_text(summary_en) if summary_en else ""

        new_p = {
            **p,  # 英語側の最新メタデータを優先
            "title_ja": title_ja,
            "summary_ja": summary_ja,
        }
        translated.append(new_p)

    # 3) Save output JSON（日本語側を上書き）
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
    print(f"✅ Done. Saved {len(translated)} proposals to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
