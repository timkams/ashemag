"""
NCERT Biology Interactive CLI.
Ask biology questions, view citations, and manage downloading/scraping.
"""
import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from ncert_bio.qa_engine import NCERTBioQAEngine
from ncert_bio.catalog import NCERT_CHAPTERS
from ncert_bio.collector import NCERTCollector
from ncert_bio.scraper import NCERTTextScraper

console = Console()

def handle_ask(args):
    engine = NCERTBioQAEngine()
    query = " ".join(args.query)
    
    with console.status(f"[bold green]Searching NCERT Class 9-12 Biology knowledge base for:[/bold green] '{query}'..."):
        res = engine.answer_question(query, grade=args.grade, top_k=args.top_k)

    if not res.get("found"):
        console.print(Panel(f"[yellow]{res['answer']}[/yellow]", title="[bold red]No Result[/bold red]", border_style="red"))
        return

    # Print Answer Panel
    console.print()
    console.print(Panel(
        f"[bold white]{res['answer']}[/bold white]",
        title=f"[bold cyan]🌿 NCERT Biology Answer (Class {args.grade if args.grade else '9-12'})[/bold cyan]",
        subtitle=f"[dim]{res['primary_source']}[/dim]",
        border_style="green",
        padding=(1, 2)
    ))

    # Print Citations Table
    table = Table(title="📚 Textbook Citations & Exact Excerpts", border_style="blue", show_lines=True)
    table.add_column("#", style="bold yellow", width=3)
    table.add_column("NCERT Reference", style="bold cyan", width=38)
    table.add_column("Section & Page", style="magenta", width=25)
    table.add_column("Excerpt", style="white")

    for i, cit in enumerate(res["citations"], 1):
        table.add_row(
            str(i),
            cit["reference"],
            f"{cit['section']}\n({cit['page']})",
            cit["excerpt"]
        )

    console.print(table)
    console.print()


def handle_status(args):
    raw_dir = Path(__file__).parent / "data" / "raw_pdf"
    corpus_dir = Path(__file__).parent / "data" / "scraped_corpus"
    db_path = Path(__file__).parent / "data" / "ncert_bio_fts.db"

    table = Table(title="NCERT Biology Knowledge Base Status", border_style="cyan")
    table.add_column("Grade", style="bold yellow")
    table.add_column("Subject", style="white")
    table.add_column("Catalog Chapters", style="cyan")
    table.add_column("Downloaded PDFs", style="green")
    table.add_column("Scraped Chapters", style="magenta")

    for g in [9, 10, 11, 12]:
        cat_count = sum(1 for c in NCERT_CHAPTERS if c["grade"] == g)
        raw_count = len(list((raw_dir / f"class_{g}").glob("*.pdf"))) if (raw_dir / f"class_{g}").exists() else 0
        scraped_count = len(list((corpus_dir / f"class_{g}").glob("*.json"))) if (corpus_dir / f"class_{g}").exists() else 0
        table.add_row(f"Class {g}", "Science" if g < 11 else "Biology", str(cat_count), str(raw_count), str(scraped_count))

    console.print(table)

    engine = NCERTBioQAEngine()
    with engine._get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM chunks")
            total_chunks = cursor.fetchone()[0]
        except Exception:
            total_chunks = 0
    console.print(f"[bold]Total Indexed Knowledge Chunks in FTS5:[/bold] [green]{total_chunks}[/green]\n")


def handle_reindex(args):
    engine = NCERTBioQAEngine()
    with console.status("[bold green]Rebuilding SQLite FTS5 Full-Text Index...[/bold green]"):
        count = engine.build_index(force_rebuild=True)
    console.print(f"[bold green]✓ Reindex complete![/bold green] Total chunks indexed: [bold cyan]{count}[/bold cyan]")


def main():
    parser = argparse.ArgumentParser(description="NCERT Biology Question-Answering & Text Scraper Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'ask' command
    ask_parser = subparsers.add_parser("ask", help="Ask a biology question")
    ask_parser.add_argument("query", nargs="+", help="The biology question to ask")
    ask_parser.add_argument("--grade", type=int, choices=[9, 10, 11, 12], help="Filter by class (9, 10, 11, or 12)")
    ask_parser.add_argument("--top-k", type=int, default=3, help="Number of citations to show")

    # 'status' command
    subparsers.add_parser("status", help="Show knowledge base status")

    # 'reindex' command
    subparsers.add_parser("reindex", help="Rebuild the FTS5 search index from scraped corpus")

    args = parser.parse_args()

    if args.command == "ask":
        handle_ask(args)
    elif args.command == "status":
        handle_status(args)
    elif args.command == "reindex":
        handle_reindex(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
