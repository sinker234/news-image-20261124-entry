#!/usr/bin/env python3
"""Ship the rendered poster into /output.

Finds entry.png next to this file, copies it to /output/entry.png, and
checks the copy landed at the same size before reporting success.
"""

import hashlib
import os
import shutil
import sys


def _digest(path):
    """SHA-256 of a file, read in 1 MiB chunks."""
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print("missing poster: %s (run draw.py first)" % source,
              file=sys.stderr)
        return 1
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    src_bytes = os.path.getsize(source)
    dst_bytes = os.path.getsize(target)
    if src_bytes != dst_bytes:
        print("size mismatch after copy: %d vs %d" % (src_bytes, dst_bytes),
              file=sys.stderr)
        return 1
    if _digest(source) != _digest(target):
        print("hash mismatch after copy: %s != %s" % (source, target),
              file=sys.stderr)
        return 1
    print("shipped %s -> %s (%d bytes, sha256 %s)"
          % (source, target, dst_bytes, _digest(target)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
