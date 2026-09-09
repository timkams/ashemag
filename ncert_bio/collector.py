"""
NCERT Textbook PDF Collector.
Downloads chapter PDFs for Class 9-12 from verified high-speed mirrors with concurrent execution and retry logic.
"""
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from ncert_bio.catalog import NCERT_CHAPTERS, get_chapters_by_grade, get_chapter

DEFAULT_STORAGE_DIR = Path(__file__).parent / "data" / "raw_pdf"

# Mirror templates
ARCHIVE_URL_TEMPLATE = "https://archive.org/download/ncert-{book_code}/{filename}"
BACKUP_ARCHIVE_URL_TEMPLATE = "https://ia801306.us.archive.org/items/ncert-{book_code}/{filename}"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class NCERTCollector:
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir) if storage_dir else DEFAULT_STORAGE_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
        })

    def get_destination_path(self, chapter_info: Dict[str, Any]) -> Path:
        grade = chapter_info["grade"]
        filename = chapter_info["filename"]
        grade_dir = self.storage_dir / f"class_{grade}"
        grade_dir.mkdir(parents=True, exist_ok=True)
        return grade_dir / filename

    def is_already_downloaded(self, chapter_info: Dict[str, Any], min_bytes: int = 50000) -> bool:
        dest = self.get_destination_path(chapter_info)
        return dest.exists() and dest.stat().st_size >= min_bytes

    def download_chapter(self, chapter_info: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        dest = self.get_destination_path(chapter_info)
        book_code = chapter_info["book_code"]
        filename = chapter_info["filename"]
        title = chapter_info["title"]
        grade = chapter_info["grade"]
        ch_num = chapter_info["chapter_num"]

        if self.is_already_downloaded(chapter_info):
            return {
                "status": "cached",
                "grade": grade,
                "chapter_num": ch_num,
                "title": title,
                "path": str(dest),
                "size_bytes": dest.stat().st_size
            }

        urls = [
            ARCHIVE_URL_TEMPLATE.format(book_code=book_code, filename=filename),
            BACKUP_ARCHIVE_URL_TEMPLATE.format(book_code=book_code, filename=filename)
        ]

        last_error = None
        for attempt in range(1, max_retries + 1):
            for url in urls:
                try:
                    resp = self.session.get(url, stream=True, timeout=25, allow_redirects=True)
                    if resp.status_code == 200:
                        temp_dest = dest.with_suffix(".tmp")
                        total_bytes = 0
                        with open(temp_dest, "wb") as f:
                            for chunk in resp.iter_content(chunk_size=65536):
                                if chunk:
                                    f.write(chunk)
                                    total_bytes += len(chunk)
                        
                        if total_bytes > 20000:
                            temp_dest.replace(dest)
                            return {
                                "status": "downloaded",
                                "grade": grade,
                                "chapter_num": ch_num,
                                "title": title,
                                "path": str(dest),
                                "size_bytes": total_bytes
                            }
                        else:
                            if temp_dest.exists():
                                temp_dest.unlink()
                except Exception as e:
                    last_error = e
            time.sleep(1.0 * attempt)

        return {
            "status": "failed",
            "grade": grade,
            "chapter_num": ch_num,
            "title": title,
            "error": str(last_error) if last_error else "Download failed"
        }

    def collect_chapters(
        self,
        chapters: Optional[List[Dict[str, Any]]] = None,
        grade: Optional[int] = None,
        max_workers: int = 4
    ) -> List[Dict[str, Any]]:
        if chapters is None:
            if grade is not None:
                chapters = get_chapters_by_grade(grade)
            else:
                chapters = NCERT_CHAPTERS

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ch = {
                executor.submit(self.download_chapter, ch): ch
                for ch in chapters
            }
            for future in as_completed(future_to_ch):
                res = future.result()
                results.append(res)
        
        results.sort(key=lambda r: (r["grade"], r["chapter_num"]))
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="NCERT Biology Textbook Collector")
    parser.add_argument("--grade", type=int, choices=[9, 10, 11, 12], help="Download a specific grade (9, 10, 11, or 12)")
    parser.add_argument("--chapter", type=int, help="Download a specific chapter number (requires --grade)")
    parser.add_argument("--all", action="store_true", help="Download all biology chapters for Classes 9-12")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent download threads")

    args = parser.parse_args()
    collector = NCERTCollector()

    if args.chapter and args.grade:
        ch = get_chapter(args.grade, args.chapter)
        if not ch:
            print(f"Error: Chapter {args.chapter} not found in Grade {args.grade}")
            sys.exit(1)
        print(f"Downloading Class {args.grade} Ch {args.chapter}: {ch['title']}...")
        res = collector.download_chapter(ch)
        print("Result:", res)
    elif args.grade:
        print(f"Downloading all Class {args.grade} Biology chapters...")
        results = collector.collect_chapters(grade=args.grade, max_workers=args.workers)
        cached = sum(1 for r in results if r["status"] == "cached")
        downloaded = sum(1 for r in results if r["status"] == "downloaded")
        failed = sum(1 for r in results if r["status"] == "failed")
        print(f"Completed Grade {args.grade}: {downloaded} downloaded, {cached} cached, {failed} failed.")
    elif args.all:
        print(f"Downloading all 50 Biology chapters for Classes 9, 10, 11, and 12...")
        results = collector.collect_chapters(max_workers=args.workers)
        cached = sum(1 for r in results if r["status"] == "cached")
        downloaded = sum(1 for r in results if r["status"] == "downloaded")
        failed = sum(1 for r in results if r["status"] == "failed")
        print(f"Completed All: {downloaded} downloaded, {cached} cached, {failed} failed.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
