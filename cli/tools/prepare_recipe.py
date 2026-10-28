"""Generate a Bioconda submission recipe from an immutable release archive.

Input: local sdist path, public HTTPS URL for those exact bytes, output path.
Output: meta.yaml with a real SHA-256 (local preparation recipe is retained).
The URL must become publicly downloadable before submission.
"""

import argparse
import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if urlsplit(args.url).scheme != "https" or not urlsplit(args.url).netloc:
        parser.error("--url must be a public HTTPS release archive URL")
    if not args.archive.is_file():
        parser.error("source archive is missing")
    if args.output.exists():
        parser.error("output already exists; choose a new output path")
    digest = hashlib.sha256(args.archive.read_bytes()).hexdigest()
    template = Path(__file__).resolve().parents[1] / "recipes/bileactome/meta.yaml"
    text = template.read_text(encoding="utf-8")
    version = re.search(r'{% set version = "([^"]+)" %}', text).group(1)
    # Keep immutable release bytes but use the Bioconda Jinja version template.
    url = args.url.replace(f"cli-v{version}/bileactome-{version}.tar.gz",
                           "cli-v{{ version }}/bileactome-{{ version }}.tar.gz")
    # HTTPS URL is quoted to avoid YAML metacharacter interpretation.
    import json

    source = f"source:\n  url: {json.dumps(url)}\n  sha256: {digest}\n\n"
    text, replacements = re.subn(r"source:\n.*?\n(?=build:)", source, text, flags=re.S)
    if replacements != 1:
        raise RuntimeError("expected exactly one source section")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"Recipe: {args.output}\nArchive SHA-256: {digest}")


if __name__ == "__main__":
    main()
