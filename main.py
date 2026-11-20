#!/usr/bin/env python3
"""news-image-20261120 entry: copy the pre-rendered front page to the output dir.

The image is a fixed, deterministic PNG (1024x1024, under 1 MiB) rendered at
build time by build_image.py; this program only copies it, so two runs
produce byte-identical output. Standard library only, no network.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(OUT_DIR, "entry.png"))


if __name__ == "__main__":
    main()
