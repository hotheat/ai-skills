#!/usr/bin/env python3
"""Download a Tencent Meeting signed media URL with optional Chrome cookies."""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import MozillaCookieJar
from pathlib import Path


def read_url(args: argparse.Namespace) -> str:
    if args.url:
        return args.url.strip()
    if args.url_file:
        return Path(args.url_file).read_text(encoding="utf-8").strip()
    raise SystemExit("Provide --url or --url-file.")


def safe_url_label(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def build_opener(cookies: str | None) -> urllib.request.OpenerDirector:
    if not cookies:
        return urllib.request.build_opener()
    jar = MozillaCookieJar(cookies)
    jar.load(ignore_discard=True, ignore_expires=True)
    print(f"cookies_loaded={len(jar)}")
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a signed Tencent Meeting media URL without logging tokens.")
    parser.add_argument("--url", help="Signed media URL. Prefer --url-file to avoid shell history.")
    parser.add_argument("--url-file", help="File containing the signed media URL.")
    parser.add_argument("--cookies", help="Netscape cookie jar exported from Chrome.")
    parser.add_argument("--output", default="recording.mp4")
    parser.add_argument("--referer", default="https://meeting.tencent.com/")
    parser.add_argument(
        "--user-agent",
        default=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        ),
    )
    parser.add_argument("--no-resume", action="store_true", help="Overwrite instead of resuming partial output.")
    parser.add_argument("--progress-seconds", type=int, default=10)
    args = parser.parse_args()

    url = read_url(args)
    output = Path(args.output)
    start = 0 if args.no_resume or not output.exists() else output.stat().st_size
    mode = "wb" if start == 0 else "ab"

    headers = {
        "User-Agent": args.user_agent,
        "Referer": args.referer,
        "Accept": "*/*",
        "Accept-Encoding": "identity;q=1, *;q=0",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Sec-Fetch-Dest": "video",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "Range": f"bytes={start}-",
    }

    print(f"media={safe_url_label(url)}")
    print(f"output={output} resume_from={start}")

    request = urllib.request.Request(url, headers=headers)
    opener = build_opener(args.cookies)
    try:
        with opener.open(request, timeout=120) as response:
            status = getattr(response, "status", "?")
            length = response.headers.get("Content-Length")
            total = int(length) + start if length and length.isdigit() else None
            print(f"http_status={status} content_length={length or 'unknown'}")
            downloaded = start
            last_report = time.time()
            with output.open(mode) as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
                    downloaded += len(chunk)
                    now = time.time()
                    if now - last_report >= args.progress_seconds:
                        if total:
                            print(f"downloaded={downloaded}/{total} ({downloaded / total:.1%})", flush=True)
                        else:
                            print(f"downloaded={downloaded}", flush=True)
                        last_report = now
    except urllib.error.HTTPError as error:
        print(f"download_failed status={error.code} media={safe_url_label(url)}", file=sys.stderr)
        raise SystemExit(error.code) from None
    except urllib.error.URLError as error:
        print(f"download_failed reason={error.reason} media={safe_url_label(url)}", file=sys.stderr)
        raise SystemExit(1) from None

    print(f"done output={output} size={output.stat().st_size}")


if __name__ == "__main__":
    main()
