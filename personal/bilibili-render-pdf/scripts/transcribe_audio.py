#!/usr/bin/env python3
"""Transcribe audio for bilibili-render-pdf with remote-ASR fallback.

Workflow:
1. Load `.env` from current working directory when present.
2. If `ASR_SERVICE_URL` is set, call remote ASR with `curl` using multipart upload.
3. Parse JSON response and persist transcript text.
4. If an SRT file is still needed for timestamped frame search, or remote ASR is not configured,
   fall back to local Whisper to generate timestamped subtitles.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def run_checked(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def resolve_asr_service_url() -> str:
    return os.environ.get("ASR_SERVICE_URL", "").strip()


def build_remote_url(asr_service_url: str, language: str, output_format: str, word_timestamps: bool = False) -> str:
    url = f"{asr_service_url}?language={language}&output={output_format}"
    if word_timestamps:
        url += "&word_timestamps=true"
    return url


def write_srt_from_segments(segments: list[dict], srt_path: Path) -> None:
    def fmt(seconds: float) -> str:
        total_ms = round(seconds * 1000)
        hours = total_ms // 3_600_000
        remainder = total_ms % 3_600_000
        minutes = remainder // 60_000
        remainder %= 60_000
        secs = remainder // 1000
        millis = remainder % 1000
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    with srt_path.open("w", encoding="utf-8") as f:
        for index, segment in enumerate(segments, start=1):
            text = str(segment.get("text", "")).strip().replace("-->", "->")
            start = float(segment["start"])
            end = float(segment["end"])
            f.write(f"{index}\n{fmt(start)} --> {fmt(end)}\n{text}\n\n")


def extract_text_from_srt_content(srt_content: str) -> str:
    lines: list[str] = []
    for raw_line in srt_content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if "-->" in line:
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def has_valid_srt_content(srt_content: str) -> bool:
    return "-->" in srt_content and bool(extract_text_from_srt_content(srt_content))


def has_valid_segments(segments: list[dict]) -> bool:
    if not segments:
        return False

    prev_end = -1.0
    for segment in segments:
        if "start" not in segment or "end" not in segment:
            return False
        start = float(segment["start"])
        end = float(segment["end"])
        text = str(segment.get("text", "")).strip()
        if end <= start or not text:
            return False
        if start < prev_end:
            return False
        prev_end = end
    return True


def remote_asr_json(
    audio_path: Path,
    language: str,
    transcript_path: Path,
    srt_path: Path,
    word_timestamps: bool,
) -> tuple[bool, str]:
    asr_service_url = resolve_asr_service_url()
    if not asr_service_url:
        return False, ""

    cmd = [
        "curl",
        "--silent",
        "--show-error",
        "--fail",
        "--max-time",
        os.environ.get("ASR_HTTP_TIMEOUT", "900"),
        "--request",
        "POST",
        "--form",
        f"audio_file=@{audio_path}",
        build_remote_url(
            asr_service_url=asr_service_url,
            language=language,
            output_format="json",
            word_timestamps=word_timestamps,
        ),
    ]

    result = run_checked(cmd)
    payload = json.loads(result.stdout)
    transcript_text = payload.get("text", "")
    segments = payload.get("segments") or []
    if not transcript_text or not has_valid_segments(segments):
        raise ValueError("Remote ASR JSON response did not contain usable transcript text and segments")

    transcript_path.write_text(transcript_text, encoding="utf-8")
    if segments:
        write_srt_from_segments(segments, srt_path)
    return True, transcript_text


def remote_asr_srt(audio_path: Path, language: str, srt_path: Path, transcript_path: Path) -> tuple[bool, str]:
    asr_service_url = resolve_asr_service_url()
    if not asr_service_url:
        return False, ""

    cmd = [
        "curl",
        "--silent",
        "--show-error",
        "--fail",
        "--max-time",
        os.environ.get("ASR_HTTP_TIMEOUT", "900"),
        "--request",
        "POST",
        "--form",
        f"audio_file=@{audio_path}",
        build_remote_url(
            asr_service_url=asr_service_url,
            language=language,
            output_format="srt",
        ),
    ]
    result = run_checked(cmd)
    srt_content = result.stdout
    if not has_valid_srt_content(srt_content):
        raise ValueError("Remote ASR SRT response was empty or malformed")

    srt_path.write_text(srt_content, encoding="utf-8")
    transcript_text = extract_text_from_srt_content(srt_content)
    transcript_path.write_text(transcript_text, encoding="utf-8")
    return True, transcript_text


def local_whisper(audio_path: Path, language: str, model: str, output_dir: Path) -> Path:
    cmd = [
        "whisper",
        str(audio_path),
        "--model",
        model,
        "--language",
        language,
        "--output_format",
        "srt",
        "--output_dir",
        str(output_dir),
    ]
    run_checked(cmd)
    return output_dir / f"{audio_path.stem}.srt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio for bilibili-render-pdf")
    parser.add_argument("audio", help="Path to audio file")
    parser.add_argument("--language", default="zh", help="ASR language parameter")
    parser.add_argument(
        "--remote-mode",
        default="auto",
        choices=("auto", "srt", "json"),
        help="Prefer remote SRT, remote JSON segments, or auto-try both",
    )
    parser.add_argument("--whisper-model", default="medium", help="Local Whisper model")
    parser.add_argument(
        "--word-timestamps",
        action="store_true",
        help="Request word timestamps when remote JSON mode is used",
    )
    parser.add_argument(
        "--transcript-path",
        default=None,
        help="Plain-text transcript output path",
    )
    parser.add_argument(
        "--srt-path",
        default=None,
        help="Expected SRT path; when missing after remote ASR, local Whisper will generate it",
    )
    parser.add_argument(
        "--skip-local-whisper",
        action="store_true",
        help="Do not run local Whisper even when SRT is unavailable",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path.cwd()
    load_dotenv(cwd / ".env")
    # If ASR_SERVICE_URL is still not set, walk up to find .env in ancestor dirs
    # (e.g. cwd is BVxxxx/ but .env lives in bilibili-render-pdf/)
    if not os.environ.get("ASR_SERVICE_URL", "").strip():
        for parent in cwd.parents:
            candidate = parent / ".env"
            if candidate.exists():
                load_dotenv(candidate)
                if os.environ.get("ASR_SERVICE_URL", "").strip():
                    break

    audio_path = Path(args.audio).expanduser().resolve()
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}", file=sys.stderr)
        return 1

    transcript_path = Path(args.transcript_path).expanduser().resolve() if args.transcript_path else audio_path.with_suffix(".txt")
    srt_path = Path(args.srt_path).expanduser().resolve() if args.srt_path else audio_path.with_suffix(".srt")

    used_remote = False
    transcript_text = ""
    remote_timecoded = False

    try:
        if args.remote_mode in ("auto", "srt"):
            try:
                remote_timecoded, transcript_text = remote_asr_srt(
                    audio_path=audio_path,
                    language=args.language,
                    srt_path=srt_path,
                    transcript_path=transcript_path,
                )
                used_remote = remote_timecoded
            except (subprocess.CalledProcessError, ValueError):
                if args.remote_mode == "srt":
                    raise

        if args.remote_mode in ("auto", "json") and not transcript_path.exists():
            used_remote, transcript_text = remote_asr_json(
                audio_path=audio_path,
                language=args.language,
                transcript_path=transcript_path,
                srt_path=srt_path,
                word_timestamps=args.word_timestamps,
            )
            remote_timecoded = remote_timecoded or srt_path.exists()
        elif transcript_path.exists():
            used_remote = True
            transcript_text = transcript_path.read_text(encoding="utf-8")
    except subprocess.CalledProcessError as exc:
        print(exc.stderr, file=sys.stderr)
        if args.skip_local_whisper:
            return exc.returncode or 1
    except json.JSONDecodeError as exc:
        print(f"Failed to parse ASR JSON response: {exc}", file=sys.stderr)
        if args.skip_local_whisper:
            return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        if args.skip_local_whisper:
            return 1

    need_local_srt = not srt_path.exists()
    if need_local_srt and not args.skip_local_whisper:
        generated_srt = local_whisper(
            audio_path=audio_path,
            language=args.language,
            model=args.whisper_model,
            output_dir=srt_path.parent,
        )
        if generated_srt != srt_path:
            generated_srt.replace(srt_path)

    result = {
        "audio_path": str(audio_path),
        "transcript_path": str(transcript_path),
        "srt_path": str(srt_path) if srt_path.exists() else None,
        "used_remote_asr": used_remote,
        "remote_timecoded": remote_timecoded,
        "asr_service_url": resolve_asr_service_url() if used_remote else None,
        "transcript_text_length": len(transcript_text) if transcript_text else transcript_path.stat().st_size if transcript_path.exists() else 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
