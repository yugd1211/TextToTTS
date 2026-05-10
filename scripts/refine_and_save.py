#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re

from openai import OpenAI


SYSTEM_PROMPT = """당신은 사용자의 메모를 '걷거나 뛸 때 듣는 오디오북 스크립트' 형태로 정리하는 편집자입니다.
출력 형식:
1) 5줄 이내 핵심 요약
2) 자연스러운 한국어 오디오 스크립트(너무 딱딱하지 않게)
사실 왜곡 금지, 불필요한 장식 금지.
"""


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def refine_text(source_text: str, model: str) -> str:
    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": normalize_text(source_text)},
        ],
    )
    return response.output_text.strip()


def build_markdown(title: str, source_text: str, refined: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = normalize_text(source_text)
    return f"""# {title}

- created_at: {now}
- source: mobile/web quick capture

## 원문

{body}

## 오디오북용 정리본

{refined}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Save captured text as audiobook-ready markdown")
    parser.add_argument("--title", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--out", default="content")
    parser.add_argument("--refine-model", default="gpt-4.1-mini")
    parser.add_argument("--no-refine", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe = re.sub(r"[^a-zA-Z0-9가-힣_-]+", "-", args.title).strip("-").lower()
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{safe or 'note'}.md"

    refined = normalize_text(args.text) if args.no_refine else refine_text(args.text, args.refine_model)

    out_path = out_dir / filename
    out_path.write_text(build_markdown(args.title, args.text, refined), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
