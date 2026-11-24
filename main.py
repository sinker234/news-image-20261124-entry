#!/usr/bin/env python3
"""Ship the finished poster.

Takes the ``entry.png`` rendered beside this script and places an
identical copy at ``/output/entry.png``. Standard library only, so it
runs anywhere Python 3 does.
"""

import os
import shutil
import sys

POSTER_NAME = "entry.png"
DEST_DIR = "/output"


def ship_poster():
    """Copy the poster to the output folder and confirm the copy matches."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(script_dir, POSTER_NAME)
    if not os.path.isfile(source):
        print("missing poster: %s (run draw.py first)" % source,
              file=sys.stderr)
        return 1
    os.makedirs(DEST_DIR, exist_ok=True)
    destination = os.path.join(DEST_DIR, POSTER_NAME)
    shutil.copyfile(source, destination)
    src_bytes = os.path.getsize(source)
    dst_bytes = os.path.getsize(destination)
    if src_bytes != dst_bytes:
        print("copy mismatch: %d bytes in, %d bytes out"
              % (src_bytes, dst_bytes), file=sys.stderr)
        return 1
    print("shipped %s -> %s (%d bytes)" % (source, destination, dst_bytes))
    return 0


if __name__ == "__main__":
    sys.exit(ship_poster())
