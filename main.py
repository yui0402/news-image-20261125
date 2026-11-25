#!/usr/bin/env python3
"""news-image-20261125 entry program: deliver entry.png as the output.

The Vice City front page is drawn by generate_image.py at build time;
this program only copies the finished PNG to the output directory,
using nothing outside the Python standard library.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
SOURCE = HERE / "entry.png"

TARGET.mkdir(parents=True, exist_ok=True)
assert SOURCE.is_file(), "entry.png missing beside main.py"
shutil.copyfile(SOURCE, TARGET / "entry.png")
print("entry.png ->", TARGET / "entry.png")
