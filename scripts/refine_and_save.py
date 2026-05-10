#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def simple_refine(source_text: str) -> str:
    body = normalize_text(source_text)
    lines = [ln.strip("-• ") for ln in body.splitlines() if ln.strip()]
    summary = lines[:5]
    summary_md = "\n".join([f"- {s}" for s in summary]) if summary else "- (요약 생성 실패)"
    narration = body
    return f"## 핵심 요약\n\n{summary_md}\n\n## 오디오북용 스크립트\n\n{narration}"


def build_markdown(title: str, source_text: str, refined: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = normalize_text(source_text)
    return f"""# {title}

- created_at: {now}
- source: mobile/web quick capture
- engine: edge-tts

## 원문

{body}

{refined}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Save captured text as audiobook-ready markdown")
    parser.add_argument("--title", required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--out", default="content")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    safe = re.sub(r"[^a-zA-Z0-9가-힣_-]+", "-", args.title).strip("-").lower()
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{safe or 'note'}.md"

    refined = simple_refine(args.text)

    out_path = out_dir / filename
    out_path.write_text(build_markdown(args.title, args.text, refined), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
