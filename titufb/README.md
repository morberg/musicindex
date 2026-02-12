# titufb index OCR

This folder contains the OCR workflow for the Ultimate Fake Book 3rd Edition index PDF.
The PDF is image-based (no selectable text), so the parser renders each page to an image,
splits it into three columns, runs tesseract OCR per column, and parses lines in the
format "page title" into a CSV.

## Inputs and outputs
- Input PDF: [This%20Is%20the%20Ultimate%20Fake%20Book%20Third%20Edition%20-%20Index.pdf](This%20Is%20the%20Ultimate%20Fake%20Book%20Third%20Edition%20-%20Index.pdf)
- Script: [parse-titufb.py](parse-titufb.py)
- Raw OCR text: [titufb-ocr-raw.txt](titufb-ocr-raw.txt)
- Parsed CSV: [titufb-raw.csv](titufb-raw.csv) in page,"title" format

## Reproduce on another machine (macOS + Homebrew)
1) Install system dependencies:
```
brew install poppler tesseract
```

2) Create a Python venv and install Python packages:
```
python3 -m venv .venv
. .venv/bin/activate
pip install pdf2image
```

3) Run the parser from this folder:
```
cd titufb
python parse-titufb.py
```

## Manual final step
Copy [titufb-raw.csv](titufb-raw.csv) to titufb.csv and fix any remaining OCR errors by hand.

## Notes
- The parser splits each PDF page into three vertical columns before OCR. This avoids
  multi-column text being merged into a single line.
- OCR cleanup fixes common misreads (for example, | -> I, and a few known word fixes).
- The output is intentionally raw. Manual review is required before import into ForScore.
