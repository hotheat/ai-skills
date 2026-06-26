#!/usr/bin/env python3
"""Import a Claude Design export zip into a repo docs/design directory."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def resolve_repo_path(repo: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = repo / path
    return path.resolve()


def safe_extract(zip_path: Path, destination: Path) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        destination_root = destination.resolve()
        for info in archive.infolist():
            target = (destination / info.filename).resolve()
            if destination_root != target and destination_root not in target.parents:
                raise SystemExit(f"unsafe zip entry: {info.filename}")
        archive.extractall(destination)


def visible_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if "__MACOSX" in parts or path.name.startswith("."):
            continue
        files.append(path)
    return files


def choose_html(files: list[Path]) -> Path | None:
    html_files = [path for path in files if path.suffix.lower() in {".html", ".htm"}]
    if not html_files:
        return None
    for path in html_files:
        if path.name.lower() == "index.html":
            return path
    return max(html_files, key=lambda path: path.stat().st_size)


def choose_png(files: list[Path]) -> Path | None:
    png_files = [path for path in files if path.suffix.lower() == ".png"]
    if not png_files:
        return None
    return max(png_files, key=lambda path: path.stat().st_size)


def choose_other_image(files: list[Path]) -> Path | None:
    images = [path for path in files if path.suffix.lower() in IMAGE_EXTENSIONS]
    if not images:
        return None
    return max(images, key=lambda path: path.stat().st_size)


def append_section_once(path: Path, heading: str, content: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if heading in existing:
        return
    separator = "\n\n" if existing.strip() else ""
    path.write_text(existing.rstrip() + separator + content.rstrip() + "\n", encoding="utf-8")


def ensure_brief(out_dir: Path, name: str) -> None:
    brief = out_dir / "brief.md"
    if brief.exists():
        append_section_once(
            brief,
            "## Imported Claude Design Artifacts",
            """## Imported Claude Design Artifacts

- `design.html`: imported Claude Design HTML reference.
- `design.png`: imported Claude Design visual reference when present.
""",
        )
        return
    brief.write_text(
        f"""# {name}

## Source

- Component: Unknown
- Page: Unknown

## Goal

Imported Claude Design artifact.

## Constraints

- Preserve existing props and API/data contracts.
- Do not copy `design.html` directly into `src/`.

## Design Artifacts

- `design.html`: imported Claude Design HTML reference.
- `design.png`: imported Claude Design visual reference when present.
""",
        encoding="utf-8",
    )


def update_notes(out_dir: Path, zip_path: Path, html_imported: bool, png_imported: bool, image_name: str | None) -> None:
    details = [
        "## Claude Design Import",
        "",
        f"- Source zip: `{zip_path}`",
        f"- HTML imported: {'yes' if html_imported else 'no'}",
        f"- PNG imported: {'yes' if png_imported else 'no'}",
    ]
    if image_name:
        details.append(f"- Other image imported: `{image_name}`")
    details.extend(
        [
            "",
            "Implementation contract:",
            "",
            "- Use `design.png` for visual target when present.",
            "- Use `design.html` to understand layout and interaction intent.",
            "- Do not copy Claude Design HTML directly into production React source.",
        ]
    )
    append_section_once(out_dir / "implementation-notes.md", "## Claude Design Import", "\n".join(details))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Frontend repository root. Defaults to current directory.")
    parser.add_argument("--zip", required=True, help="Claude Design exported zip.")
    parser.add_argument("--name", help="Design directory name under docs/design.")
    parser.add_argument("--design-dir", help="Explicit design directory path, relative to repo or absolute.")
    parser.add_argument("--out-root", default="docs/design", help="Output root relative to repo when --name is used.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing design.html/design.png.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"repo not found: {repo}")

    zip_path = Path(args.zip).expanduser().resolve()
    if not zip_path.exists() or not zip_path.is_file():
        raise SystemExit(f"zip not found: {zip_path}")

    if args.design_dir:
        out_dir = resolve_repo_path(repo, args.design_dir)
        name = out_dir.name
    elif args.name:
        out_dir = resolve_repo_path(repo, args.out_root) / args.name
        name = args.name
    else:
        raise SystemExit("provide --name or --design-dir")

    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="claude-design-export-") as tmp:
        tmp_path = Path(tmp)
        safe_extract(zip_path, tmp_path)
        files = visible_files(tmp_path)

        html = choose_html(files)
        if html is None:
            raise SystemExit("no HTML file found in Claude Design export")

        design_html = out_dir / "design.html"
        if design_html.exists() and not args.force:
            raise SystemExit(f"{design_html} already exists (use --force to overwrite)")
        shutil.copy2(html, design_html)

        png = choose_png(files)
        png_imported = False
        image_name: str | None = None
        if png:
            design_png = out_dir / "design.png"
            if design_png.exists() and not args.force:
                raise SystemExit(f"{design_png} already exists (use --force to overwrite)")
            shutil.copy2(png, design_png)
            png_imported = True
        else:
            other_image = choose_other_image(files)
            if other_image:
                image_name = f"design{other_image.suffix.lower()}"
                target = out_dir / image_name
                if target.exists() and not args.force:
                    raise SystemExit(f"{target} already exists (use --force to overwrite)")
                shutil.copy2(other_image, target)

    ensure_brief(out_dir, name)
    update_notes(out_dir, zip_path, html_imported=True, png_imported=png_imported, image_name=image_name)

    print(f"imported Claude Design export into {out_dir}")
    if not png_imported:
        print("warning: no PNG found; save a Claude Design screenshot as design.png before implementation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
