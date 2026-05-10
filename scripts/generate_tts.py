#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
from typing import Iterable

from openai import OpenAI


def strip_markdown(text: str) -> str:
    text = re.sub(r"^#.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\- .*", "", text, flags=re.MULTILINE)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 3500) -> Iterable[str]:
    text = text.strip()
    if len(text) <= max_chars:
        yield text
        return

    paragraphs = text.split("\n\n")
    chunk = ""
    for p in paragraphs:
        candidate = f"{chunk}\n\n{p}".strip() if chunk else p
        if len(candidate) <= max_chars:
            chunk = candidate
            continue
        if chunk:
            yield chunk
        if len(p) <= max_chars:
            chunk = p
        else:
            for i in range(0, len(p), max_chars):
                yield p[i : i + max_chars]
            chunk = ""
    if chunk:
        yield chunk


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TTS audio from markdown/text file")
    parser.add_argument("input_file")
    parser.add_argument("--voice", default=os.getenv("OPENAI_TTS_VOICE", "coral"))
    parser.add_argument("--model", default=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"))
    parser.add_argument("--format", default=os.getenv("OPENAI_TTS_FORMAT", "mp3"))
    parser.add_argument("--output-dir", default="audio")
    parser.add_argument("--instructions", default="차분하고 명료한 한국어 오디오북 톤으로 읽어줘.")
    args = parser.parse_args()

    source = Path(args.input_file)
    raw_text = source.read_text(encoding="utf-8")
    text = strip_markdown(raw_text)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = OpenAI()

    # 단일 출력 + 분할 출력(긴 텍스트) 모두 지원
    chunks = list(chunk_text(text))
    if len(chunks) == 1:
        out_file = out_dir / f"{source.stem}.{args.format}"
        with client.audio.speech.with_streaming_response.create(
            model=args.model,
            voice=args.voice,
            input=chunks[0],
            format=args.format,
            instructions=args.instructions,
        ) as response:
            response.stream_to_file(out_file)
        print(out_file)
        return

    for idx, chunk in enumerate(chunks, start=1):
        out_file = out_dir / f"{source.stem}.part{idx:02d}.{args.format}"
        with client.audio.speech.with_streaming_response.create(
            model=args.model,
            voice=args.voice,
            input=chunk,
            format=args.format,
            instructions=args.instructions,
        ) as response:
            response.stream_to_file(out_file)
        print(out_file)


if __name__ == "__main__":
    main()
