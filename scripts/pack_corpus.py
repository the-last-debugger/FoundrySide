"""Archive the corpus and report what compression actually buys.

The corpus is the largest thing in the workspace and it grows with every season. Storing it as one
gzipped tar makes the footprint visible and portable; reading it back is verified rather than assumed.

    python scripts/pack_corpus.py                 # write var/corpus.tar.gz
    python scripts/pack_corpus.py --check         # verify the archive reads back
    python scripts/pack_corpus.py --out X.tar.gz
"""

from __future__ import annotations

import argparse
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research" / "data"
OUT = ROOT / "var" / "corpus.tar.gz"


def pack(out: Path) -> dict:
    files = sorted(DATA.glob("*.csv"))
    if not files:
        raise SystemExit(f"no CSV files in {DATA}")
    raw = sum(f.stat().st_size for f in files)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out, "w:gz", compresslevel=9) as archive:
        for path in files:
            archive.add(path, arcname=f"data/{path.name}")
    packed = out.stat().st_size
    return {"files": len(files), "raw": raw, "packed": packed,
            "ratio": packed / raw if raw else 0.0}


def check(archive_path: Path) -> dict:
    with tarfile.open(archive_path, "r:gz") as archive:
        members = [m for m in archive.getmembers() if m.name.endswith(".csv")]
        if not members:
            raise SystemExit("archive contains no CSV files")
        first = members[0]
        handle = archive.extractfile(first)
        head = handle.read(200).decode("latin-1") if handle else ""
    return {"members": len(members), "first": first.name, "header_lines": head.count("\n")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive the corpus")
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--check", action="store_true", help="verify an existing archive")
    args = parser.parse_args()
    out = Path(args.out)

    if args.check:
        if not out.exists():
            raise SystemExit(f"no archive at {out}")
        info = check(out)
        print(f"{out.name}: {info['members']} CSV members, first {info['first']}")
        return 0

    info = pack(out)
    shown = out.relative_to(ROOT) if out.is_relative_to(ROOT) else out
    print(f"wrote {shown}: {info['files']} files, "
          f"{info['raw'] / 1024 / 1024:.1f} MB -> {info['packed'] / 1024 / 1024:.1f} MB "
          f"({info['ratio']:.1%} of original)")
    verified = check(out)
    print(f"verified: {verified['members']} members readable, first {verified['first']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
