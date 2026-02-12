"""
Parse "This Is the Ultimate Fake Book Third Edition - Index.pdf"
from scanned images via OCR (tesseract) into a CSV file.

The PDF contains 8 scanned pages. Page 1 is mostly single-column,
pages 2-8 are 3-column layout. Each page image is split into 3
vertical columns and OCR'd separately for clean results.

Usage: python parse-titufb.py
Output: titufb-raw.csv  (page,"title")
"""

import re
import subprocess
import tempfile
import os
from typing import NamedTuple, List, Optional

from pdf2image import convert_from_path

PDF_FILE = "This Is the Ultimate Fake Book Third Edition - Index.pdf"
OUTPUT_FILE = "titufb-raw.csv"
DPI = 300
NUM_COLUMNS = 3

# --- OCR helpers ---


def ocr_image(img, dpi: int = DPI, psm: int = 6) -> str:
    """Run tesseract OCR on a PIL image."""
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    img.save(tmp.name)
    result = subprocess.run(
        ["tesseract", tmp.name, "stdout", "--dpi", str(dpi), "--psm", str(psm)],
        capture_output=True,
        text=True,
    )
    os.unlink(tmp.name)
    return result.stdout


def ocr_pdf(pdf_path: str, dpi: int = DPI) -> str:
    """
    Convert each page of a PDF to an image, split into columns,
    and run tesseract OCR on each column separately.
    """
    images = convert_from_path(pdf_path, dpi=dpi)
    full_text = ""
    for i, img in enumerate(images):
        w, h = img.size
        page_text = ""
        # Split into columns and OCR each
        col_width = w // NUM_COLUMNS
        for col in range(NUM_COLUMNS):
            left = col * col_width
            right = (col + 1) * col_width if col < NUM_COLUMNS - 1 else w
            col_img = img.crop((left, 0, right, h))
            col_text = ocr_image(col_img, dpi, psm=6)
            page_text += col_text + "\n"
        lines = page_text.splitlines()
        print(f"  Page {i + 1}: {len(lines)} lines ({NUM_COLUMNS} columns)")
        full_text += page_text + "\n"
    return full_text


# --- Text cleaning ---


def fix_ocr_artifacts(text: str) -> str:
    """Fix common OCR misreads."""
    # Fix | -> I in common patterns
    # e.g. "What Am | Living For" -> "What Am I Living For"
    text = re.sub(r" \| ", " I ", text)
    # Fix leading | at start of words
    text = re.sub(r"\|(?=[A-Za-z])", "I", text)
    # Fix trailing | at end of words
    text = re.sub(r"(?<=[A-Za-z])\|", "I", text)
    # Fix standalone |
    text = re.sub(r"(?<=\s)\|(?=\s)", "I", text)
    # Fix | at start of line (common in "I ..." song titles)
    text = re.sub(r"^\| ", "I ", text, flags=re.MULTILINE)
    # Fix |' at start of line -> I' (e.g. "|'ll" -> "I'll")
    text = re.sub(r"^\|'", "I'", text, flags=re.MULTILINE)
    # Fix remaining | that should be I (within song title context)
    text = re.sub(r"\|", "I", text)
    # Fix J at start of line followed by space and digit (OCR misread of line noise)
    text = re.sub(r"^J\s+(\d)", r"\1", text, flags=re.MULTILINE)
    # Fix tn -> in (common OCR misread)
    text = re.sub(r"\btn\b", "in", text)
    # Fix 51° -> 51 (degree sign noise)
    text = re.sub(r"(\d)°", r"\1", text)
    # Fix period/comma right after number: "212." -> "212"
    text = re.sub(r"^(\d+)[.,]\s", r"\1 ", text, flags=re.MULTILINE)
    # Fix "." or "J" prefix before page numbers at line start
    text = re.sub(r"^[.J]\s*(\d{2,3}\s)", r"\1", text, flags=re.MULTILINE)
    # Fix /rving -> Irving
    text = text.replace("/rving", "Irving")
    # Fix "Asif" -> "As If"
    text = text.replace("Asif ", "As If ")
    # Fix "AmI" -> "Am I"
    text = re.sub(r"AmI\b", "Am I", text)
    # Fix "AllI" -> "All I"
    text = re.sub(r"AllI\b", "All I", text)
    # Fix " OF " -> " Of " (OCR caps)
    text = text.replace(" OF ", " Of ")
    # Fix "Hove" -> "Have" when preceded by I/to
    text = re.sub(r"\bHove\b", "Have", text)
    # Fix "BeA" -> "Be A"
    text = re.sub(r"\bBeA\b", "Be A", text)
    # Fix "Block" -> "Black" in "Block Magic"
    text = text.replace("Block Magic", "Black Magic")
    # Fix "I'mAMon" -> "I'm A Man" (missing spaces)
    text = text.replace("I'mAMon", "I'm A Man")
    # Fix common space-collapsed words
    text = re.sub(r"\bI'mA\b", "I'm A", text)
    return text


# --- Parsing ---


class IndexEntry(NamedTuple):
    page: int
    song: str


def is_header_or_noise(line: str) -> bool:
    """Filter out non-index lines."""
    stripped = line.strip()
    noise_patterns = [
        r"^\s*$",  # blank lines
        r"^Classified Song Listing",
        r"^Chord Chart",
        r"^ALPHABETICAL LISTING",
        r"^INDEX",
        r"^\d+\s+Classified",
        r"^\d+\s+Chord Chart",
        r"^\d{1,2}$",  # standalone single/double digit (page number of the PDF itself)
    ]
    for pat in noise_patterns:
        if re.match(pat, stripped, re.IGNORECASE):
            return True
    return False


def parse_index_line(line: str):
    """
    Parse a line from the index. Lines are typically:
      "18 Abraham, Martin And John"
      "18  Abraham, Martin And John"
    Returns (page_number, title) or None if not a valid index line.
    """
    # Match: page_number followed by spaces and title
    m = re.match(r"^\s*(\d+)\s{1,4}(.+)$", line)
    if m:
        page = int(m.group(1))
        title = m.group(2).strip()
        # Sanity check: page numbers in this book are roughly 10-770
        if 1 <= page <= 800 and len(title) > 1:
            return page, title
    return None


def parse_ocr_text(raw_text: str) -> List[IndexEntry]:
    """Parse the full OCR text into index entries."""
    entries: List[IndexEntry] = []
    lines = raw_text.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if is_header_or_noise(line):
            i += 1
            continue

        parsed = parse_index_line(line)
        if parsed:
            page, title = parsed
            # Check for continuation lines (no page number, indented text)
            while i + 1 < len(lines):
                next_line = lines[i + 1].rstrip()
                # Continuation: no leading page number, has text
                # Typically wrapped titles like:
                #   "36 Almost Paradise (Love Theme From"
                #   "   Footloose)"
                if next_line.strip() and not parse_index_line(next_line) and not is_header_or_noise(next_line):
                    # Check it's not a standalone page number block
                    if not re.match(r"^\s*\d+\s*$", next_line):
                        title += " " + next_line.strip()
                        i += 1
                        continue
                break
            entries.append(IndexEntry(page, title))
        else:
            # Line with just page numbers (column overflow) - skip
            # These appear when OCR reads the left column of page numbers
            # separately from the right column of titles
            pass

        i += 1

    return entries


def clean_title(title: str) -> str:
    """Clean up a song title."""
    # Remove leading/trailing punctuation noise (dashes, dots, underscores, tildes)
    title = re.sub(r"^[—–\-~_.]+\s*", "", title)
    title = title.strip(" .-_~")
    # Collapse multiple spaces
    title = re.sub(r"\s+", " ", title)
    # Fix quotes
    title = title.replace("\u201c", '"').replace("\u201d", '"')
    title = title.replace("\u2018", "'").replace("\u2019", "'")
    # Remove trailing em-dash
    title = re.sub(r"\s*[—–\-]+\s*$", "", title)
    return title


def write_csv(entries: List[IndexEntry], output_file: str):
    """Write entries to CSV in format: page,"title" """
    with open(output_file, "w") as f:
        for entry in entries:
            title = clean_title(entry.song)
            # Escape quotes in title
            title = title.replace('"', '""')
            f.write(f'{entry.page},"{title}"\n')


# --- Main ---


def main():
    print(f"OCR-ing {PDF_FILE} at {DPI} DPI...")
    raw_text = ocr_pdf(PDF_FILE, DPI)

    # Save raw OCR text for debugging
    with open("titufb-ocr-raw.txt", "w") as f:
        f.write(raw_text)
    print(f"Raw OCR text saved to titufb-ocr-raw.txt ({len(raw_text)} chars)")

    print("Cleaning OCR artifacts...")
    cleaned_text = fix_ocr_artifacts(raw_text)

    print("Parsing index entries...")
    entries = parse_ocr_text(cleaned_text)
    print(f"Found {len(entries)} entries")

    # Sort by page number for consistency
    entries.sort(key=lambda e: (e.page, e.song))

    # Remove duplicates (same page + very similar title)
    unique_entries: List[IndexEntry] = []
    seen = set()
    for entry in entries:
        key = (entry.page, entry.song.lower())
        if key not in seen:
            seen.add(key)
            unique_entries.append(entry)

    print(f"After dedup: {len(unique_entries)} entries")

    write_csv(unique_entries, OUTPUT_FILE)
    print(f"Written to {OUTPUT_FILE}")

    # Print first/last few entries for verification
    print("\nFirst 10 entries:")
    for e in unique_entries[:10]:
        print(f"  {e.page:>4}  {e.song}")
    print("\nLast 10 entries:")
    for e in unique_entries[-10:]:
        print(f"  {e.page:>4}  {e.song}")


if __name__ == "__main__":
    main()
