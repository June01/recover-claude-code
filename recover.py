#!/usr/bin/env python3
"""
recover.py — Restore Claude Code source from its npm source map.

The @anthropic-ai/claude-code npm package (v2.1.88) was published with its
source map (cli.js.map) intact and with sourcesContent populated.  That single
file is enough to reconstruct every TypeScript source file that was compiled
into the final bundle.

Usage
-----
  # Step 1 – download the tarball straight from the npm registry
  curl -L https://registry.npmjs.org/@anthropic-ai/claude-code/-/claude-code-2.1.88.tgz \
       -o claude-code-2.1.88.tgz

  # Step 2 – run this script
  python3 recover.py                          # extract everything
  python3 recover.py --only-anthropic         # extract only src/ files (Anthropic's own code)
  python3 recover.py --tarball my.tgz         # use a custom tarball path
  python3 recover.py --mapfile cli.js.map     # use an already-extracted map file
"""

import argparse
import json
import os
import sys
import tarfile


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Recover Claude Code source from its npm source map")
    p.add_argument(
        "--tarball",
        default="claude-code-2.1.88.tgz",
        help="Path to the downloaded npm tarball (default: claude-code-2.1.88.tgz)",
    )
    p.add_argument(
        "--mapfile",
        default=None,
        help="Path to an already-extracted cli.js.map (skips tarball extraction)",
    )
    p.add_argument(
        "--outdir",
        default="recovered",
        help="Output directory for restored source files (default: recovered/)",
    )
    p.add_argument(
        "--only-anthropic",
        action="store_true",
        help="Only restore files under src/ (Anthropic's own TypeScript, not node_modules)",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Tarball → source map
# ---------------------------------------------------------------------------

def extract_map_from_tarball(tarball_path: str) -> dict:
    """Open the npm tarball and parse cli.js.map without fully unpacking."""
    if not os.path.exists(tarball_path):
        sys.exit(
            f"[error] Tarball not found: {tarball_path}\n"
            "Download it first:\n"
            "  curl -L https://registry.npmjs.org/@anthropic-ai/claude-code/-/claude-code-2.1.88.tgz"
            " -o claude-code-2.1.88.tgz"
        )
    print(f"[*] Opening tarball: {tarball_path}")
    with tarfile.open(tarball_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name.endswith("cli.js.map"):
                print(f"[*] Found source map: {member.name}")
                f = tar.extractfile(member)
                return json.load(f)
    sys.exit("[error] cli.js.map not found inside the tarball.")


def load_map_from_file(path: str) -> dict:
    print(f"[*] Loading source map: {path}")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Source-map → files
# ---------------------------------------------------------------------------

def restore_sources(smap: dict, outdir: str, only_anthropic: bool) -> None:
    sources = smap.get("sources", [])
    contents = smap.get("sourcesContent", [])

    total = len(sources)
    written = 0
    skipped = 0

    for path, code in zip(sources, contents):
        if code is None:
            skipped += 1
            continue

        # Normalise webpack/bundler path prefixes
        clean = (
            path.replace("webpack:///", "")
                .replace("webpack://", "")
                .lstrip("/")
        )
        # Remove leading ../ traversal produced by the bundler
        while clean.startswith("../"):
            clean = clean[3:]

        if only_anthropic and not clean.startswith("src/"):
            skipped += 1
            continue

        out_path = os.path.join(outdir, clean)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(code)
        written += 1

    print(f"[+] Restored {written} files → {outdir}/  (skipped {skipped})")


# ---------------------------------------------------------------------------
# Stats helper
# ---------------------------------------------------------------------------

def print_stats(smap: dict) -> None:
    sources = smap.get("sources", [])
    contents = smap.get("sourcesContent", [])
    non_null = sum(1 for c in contents if c is not None)
    own = [s for s in sources if "node_modules" not in s]
    print(f"[*] Source map v{smap.get('version', '?')}: "
          f"{len(sources)} entries, {non_null} with content, "
          f"{len(own)} Anthropic-owned files")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    if args.mapfile:
        smap = load_map_from_file(args.mapfile)
    else:
        smap = extract_map_from_tarball(args.tarball)

    print_stats(smap)
    restore_sources(smap, args.outdir, args.only_anthropic)


if __name__ == "__main__":
    main()
