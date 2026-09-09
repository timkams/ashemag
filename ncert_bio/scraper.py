"""
NCERT Biology PDF Text Scraper.
Extracts structured chapter content, section hierarchies, key terms, definitions, and clean markdown/JSON.
Built with PyMuPDF (fitz) and fallback to pdfplumber.
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import fitz  # PyMuPDF
import pdfplumber

from ncert_bio.catalog import NCERT_CHAPTERS, get_chapter

DEFAULT_RAW_DIR = Path(__file__).parent / "data" / "raw_pdf"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "data" / "scraped_corpus"

# Regex patterns for NCERT sections and headings
SECTION_HEADER_RE = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s+(.+)$")
CHAPTER_HEADER_RE = re.compile(r"^(?:CHAPTER|Chapter)\s+(\d+)\s*$", re.IGNORECASE)
RUNNING_HEADER_RE = re.compile(r"^(BIOLOGY|SCIENCE|Rationalised\s+\d{4}-\d{2}|Reprint\s+\d{4}|\d{1,3}\s+BIOLOGY|BIOLOGY\s+\d{1,3}|\d{1,3}\s+SCIENCE|SCIENCE\s+\d{1,3})$", re.IGNORECASE)


class NCERTTextScraper:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_running_header_or_footer(self, text: str, page_num: int, total_pages: int, rect: fitz.Rect, page_height: float) -> bool:
        """Filter out running headers, footers, and solitary page numbers."""
        clean = text.strip()
        if not clean:
            return True
        # Check if it's purely a page number
        if clean.isdigit() and len(clean) <= 3:
            return True
        # Check running header text regex
        if RUNNING_HEADER_RE.match(clean):
            return True
        # Position-based filtering (top 5% or bottom 5% of page)
        if rect.y1 < page_height * 0.05 or rect.y0 > page_height * 0.95:
            if len(clean) < 60:
                return True
        return False

    def extract_chapter_structure(self, pdf_path: Path, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract structured sections, paragraphs, and terms from an NCERT PDF."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        pages_data = []
        raw_sections = []
        current_section = {
            "section_num": "Overview",
            "title": metadata.get("title", "Chapter Introduction") if metadata else "Chapter Introduction",
            "page_start": 1,
            "page_end": 1,
            "paragraphs": [],
            "key_terms": set()
        }

        chapter_num = metadata.get("chapter_num", "") if metadata else ""
        chapter_title = metadata.get("title", "") if metadata else ""
        grade = metadata.get("grade", 0) if metadata else 0

        # Pass 1: Extract block text with font sizes to identify headings
        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1
            page_rect = page.rect
            page_height = page_rect.height

            # Extract structured blocks
            blocks = page.get_text("dict")["blocks"]
            page_paragraphs = []

            for block in blocks:
                if block.get("type") == 0:  # Text block
                    block_rect = fitz.Rect(block.get("bbox", [0, 0, 0, 0]))
                    
                    # Accumulate block lines
                    block_text_lines = []
                    max_font_size = 0.0
                    is_bold = False

                    for line in block.get("lines", []):
                        line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                        for span in line.get("spans", []):
                            size = span.get("size", 10.0)
                            if size > max_font_size:
                                max_font_size = size
                            flags = span.get("flags", 0)
                            if flags & 2 != 0 or "Bold" in span.get("font", ""):
                                is_bold = True
                        block_text_lines.append(line_text)

                    full_block_text = " ".join(" ".join(block_text_lines).split()).strip()

                    if not full_block_text:
                        continue

                    # Check running headers/footers
                    if self.is_running_header_or_footer(full_block_text, page_num, total_pages, block_rect, page_height):
                        continue

                    # Check if this block is a section header (e.g., "18.1 BLOOD" or "5.2 WHAT IS A CELL MADE UP OF?")
                    match = SECTION_HEADER_RE.match(full_block_text)
                    is_heading = False
                    sec_num = ""
                    sec_title = ""

                    if match and (max_font_size >= 10.5 or is_bold):
                        is_heading = True
                        sec_num = match.group(1).strip()
                        sec_title = match.group(2).strip()
                    elif full_block_text.upper() in ["SUMMARY", "EXERCISES", "POINTS TO PONDER"]:
                        is_heading = True
                        sec_num = full_block_text.capitalize()
                        sec_title = full_block_text.capitalize()

                    if is_heading:
                        # Flush current section
                        if current_section["paragraphs"]:
                            current_section["key_terms"] = list(current_section["key_terms"])
                            raw_sections.append(current_section)
                        # Start new section
                        current_section = {
                            "section_num": sec_num,
                            "title": sec_title,
                            "page_start": page_num,
                            "page_end": page_num,
                            "paragraphs": [],
                            "key_terms": set()
                        }
                    else:
                        # Append paragraph to current section
                        current_section["paragraphs"].append(full_block_text)
                        current_section["page_end"] = page_num
                        page_paragraphs.append(full_block_text)

                        # Extract potential biology key terms (words in bold or capitalized technical terms)
                        words = full_block_text.split()
                        for w in words:
                            clean_w = re.sub(r"[^\w]", "", w)
                            if len(clean_w) > 4 and clean_w.islower() and clean_w in [
                                "erythrocyte", "leukocyte", "platelet", "plasma", "haemoglobin", "lymph",
                                "pericardium", "atrium", "ventricle", "systole", "diastole", "hypertension",
                                "nephron", "glomerulus", "bowman", "loop", "henle", "dialysis", "neuron",
                                "synapse", "cerebrum", "cerebellum", "hormone", "pituitary", "thyroid",
                                "mitochondria", "ribosome", "chloroplast", "vacuole", "endoplasmic", "reticulum",
                                "meiosis", "mitosis", "photosynthesis", "chlorophyll", "enzyme", "substrate"
                            ]:
                                current_section["key_terms"].add(clean_w)

            pages_data.append({
                "page_num": page_num,
                "text": "\n\n".join(page_paragraphs)
            })

        # Close final section
        if current_section["paragraphs"]:
            current_section["key_terms"] = list(current_section["key_terms"])
            raw_sections.append(current_section)

        doc.close()

        # Fallback with pdfplumber if PyMuPDF extracted very little text
        total_extracted_words = sum(len(" ".join(s["paragraphs"]).split()) for s in raw_sections)
        if total_extracted_words < 50:
            raw_sections = self._fallback_pdfplumber(pdf_path, metadata)

        # Build clean markdown
        markdown_lines = [
            f"# Class {grade} {metadata.get('subject', 'Biology')}: Chapter {chapter_num} - {chapter_title}",
            f"**Unit:** {metadata.get('unit', '')}  ",
            f"**Total Pages:** {total_pages}\n",
            "---\n"
        ]

        for sec in raw_sections:
            markdown_lines.append(f"## {sec['section_num']} {sec['title']}")
            markdown_lines.append(f"*Pages: {sec['page_start']} - {sec['page_end']}*\n")
            for para in sec["paragraphs"]:
                markdown_lines.append(f"{para}\n")
            markdown_lines.append("")

        clean_markdown = "\n".join(markdown_lines)

        return {
            "grade": grade,
            "subject": metadata.get("subject", "Biology") if metadata else "Biology",
            "chapter_num": chapter_num,
            "chapter_title": chapter_title,
            "unit": metadata.get("unit", "") if metadata else "",
            "total_pages": total_pages,
            "total_sections": len(raw_sections),
            "word_count": sum(len(" ".join(s["paragraphs"]).split()) for s in raw_sections),
            "sections": raw_sections,
            "markdown": clean_markdown
        }

    def _fallback_pdfplumber(self, pdf_path: Path, metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sections = []
        with pdfplumber.open(pdf_path) as pdf:
            paragraphs = []
            for idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                clean = text.strip()
                if clean:
                    paragraphs.append(clean)
            sections.append({
                "section_num": "Full Chapter",
                "title": metadata.get("title", "Chapter Content") if metadata else "Chapter Content",
                "page_start": 1,
                "page_end": len(pdf.pages),
                "paragraphs": paragraphs,
                "key_terms": []
            })
        return sections

    def scrape_chapter(self, pdf_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Scrapes a single chapter PDF and saves JSON and Markdown artifacts."""
        data = self.extract_chapter_structure(pdf_path, metadata)
        
        grade = metadata["grade"]
        ch_num = metadata["chapter_num"]
        grade_dir = self.output_dir / f"class_{grade}"
        grade_dir.mkdir(parents=True, exist_ok=True)

        json_path = grade_dir / f"chapter_{ch_num:02d}.json"
        md_path = grade_dir / f"chapter_{ch_num:02d}.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(data["markdown"])

        return {
            "grade": grade,
            "chapter_num": ch_num,
            "title": data["chapter_title"],
            "sections_count": data["total_sections"],
            "word_count": data["word_count"],
            "json_path": str(json_path),
            "md_path": str(md_path)
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NCERT Biology PDF Text Scraper")
    parser.add_argument("--grade", type=int, choices=[9, 10, 11, 12], help="Scrape chapters for a specific grade")
    parser.add_argument("--chapter", type=int, help="Scrape a specific chapter number (requires --grade)")
    parser.add_argument("--all", action="store_true", help="Scrape all downloaded chapters")

    args = parser.parse_args()
    scraper = NCERTTextScraper()
    raw_dir = DEFAULT_RAW_DIR

    if args.grade and args.chapter:
        ch_meta = get_chapter(args.grade, args.chapter)
        if not ch_meta:
            print(f"Error: Chapter {args.chapter} not found in catalog for grade {args.grade}")
            return
        pdf_file = raw_dir / f"class_{args.grade}" / ch_meta["filename"]
        if not pdf_file.exists():
            print(f"PDF file does not exist: {pdf_file}. Run collector first.")
            return
        print(f"Scraping Class {args.grade} Ch {args.chapter}: {ch_meta['title']}...")
        result = scraper.scrape_chapter(pdf_file, ch_meta)
        print("Success! Scraped:", result)
    else:
        # Batch scrape all existing raw PDFs
        count = 0
        for ch in NCERT_CHAPTERS:
            if args.grade and ch["grade"] != args.grade:
                continue
            pdf_path = raw_dir / f"class_{ch['grade']}" / ch["filename"]
            if pdf_path.exists():
                print(f"Scraping Class {ch['grade']} Ch {ch['chapter_num']}: {ch['title']}...")
                res = scraper.scrape_chapter(pdf_path, ch)
                print(f"  -> {res['sections_count']} sections, {res['word_count']} words.")
                count += 1
        print(f"Batch scrape finished. Processed {count} chapters.")


if __name__ == "__main__":
    main()
