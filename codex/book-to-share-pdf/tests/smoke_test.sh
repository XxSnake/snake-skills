#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python scripts/build_booklet_pdf.py examples/sample_狂人日记.md -o tests/sample_狂人日记.pdf
python scripts/verify_pdf.py tests/sample_狂人日记.pdf --render --out-dir tests/renders
