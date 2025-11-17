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
    # 1) Load input JSON
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        proposals = json.load(f)

    translated = []
    for p in proposals:
        title_en = p.get("title_en", "")
        summary_en = p.get("summary_en", "")

        print(f"Translating: {p.get('proposal_id')} - {title_en}")

        # タイトルは「タイトル専用プロンプト」で1行だけ
        title_ja = translate_title(title_en) if title_en else ""

        # summary_en は今は空なので "" のままでOK
        summary_ja = translate_summary(summary_en) if summary_en else ""

        new_p = {
            **p,
            "title_ja": title_ja,
            "summary_ja": summary_ja,
        }
        translated.append(new_p)

    # 3) Save output JSON
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)

    print(f"✅ Done. Saved {len(translated)} proposals to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
