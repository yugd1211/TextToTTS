#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import re
from typing import Iterable

import edge_tts


def extract_tts_section(text: str) -> str:
    marker = "## 오디오북용 스크립트"
    idx = text.find(marker)
    if idx == -1:
        return text
    section = text[idx + len(marker):].strip()
    return section or text


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"^#.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\- .*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 6000) -> Iterable[str]:
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
        else:
            if chunk:
                yield chunk
            if len(p) <= max_chars:
                chunk = p
            else:
                for i in range(0, len(p), max_chars):
                    yield p[i:i+max_chars]
                chunk = ""
    if chunk:
        yield chunk


async def tts_to_file(text: str, out_file: Path, voice: str, rate: str, pitch: str) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(out_file))


def safe_folder_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9가-힣._-]+", "-", name).strip("-.")
    return cleaned or "untitled"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TTS audio from markdown/text file using Edge TTS")
    parser.add_argument("input_file")
    parser.add_argument("--voice", default=os.getenv("EDGE_TTS_VOICE", "ko-KR-SunHiNeural"))
    parser.add_argument("--rate", default=os.getenv("EDGE_TTS_RATE", "+0%"))
    parser.add_argument("--pitch", default=os.getenv("EDGE_TTS_PITCH", "+0Hz"))
    parser.add_argument("--format", default="mp3")
    parser.add_argument("--output-dir", default="audio")
    args = parser.parse_args()

    source = Path(args.input_file)
    raw_text = source.read_text(encoding="utf-8")
    focused = extract_tts_section(raw_text)
    text = strip_markdown(focused)

    base_out_dir = Path(args.output_dir)
    out_dir = base_out_dir / safe_folder_name(source.stem)
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks = list(chunk_text(text))
    if len(chunks) == 1:
        out_file = out_dir / f"full.{args.format}"
        asyncio.run(tts_to_file(chunks[0], out_file, args.voice, args.rate, args.pitch))
        print(out_file)
        return

    for idx, chunk in enumerate(chunks, start=1):
        out_file = out_dir / f"part{idx:02d}.{args.format}"
        asyncio.run(tts_to_file(chunk, out_file, args.voice, args.rate, args.pitch))
        print(out_file)


if __name__ == "__main__":
    main()
