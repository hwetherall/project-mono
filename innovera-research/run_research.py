"""
CLI entry point for the Innovera research pre-step.

Usage:
  python run_research.py --docs ./venture_docs/
  python run_research.py --docs ./venture_docs/ --metadata ./metadata.yaml
  python run_research.py --docs ./venture_docs/ --output ./custom_output/
  python run_research.py --docs ./venture_docs/ --only EC-04,EC-05,EC-10
"""
import os
import sys

if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import asyncio
import argparse
import yaml
from pathlib import Path
from rich.console import Console

from config.settings import VENTURE_DOCS_DIR, OUTPUT_DIR
from context_extraction.extractor import ContextExtractor
from orchestrator.runner import ResearchRunner
from orchestrator.progress import ProgressTracker
from output.package_assembler import PackageAssembler

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Innovera Web Research Pre-Step")
    parser.add_argument(
        "--docs", type=str, default=str(VENTURE_DOCS_DIR),
        help="Path to directory containing venture documents"
    )
    parser.add_argument(
        "--metadata", type=str, default=None,
        help="Path to YAML file with structured metadata (optional)"
    )
    parser.add_argument(
        "--output", type=str, default=str(OUTPUT_DIR),
        help="Path to output directory for evidence packages"
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help="Comma-separated category IDs to run (e.g. EC-04,EC-05,EC-10). "
             "Skips already-succeeded categories for faster re-runs."
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs)
    output_dir = Path(args.output)

    if not docs_dir.exists():
        console.print(f"[red]Error: Documents directory not found: {docs_dir}[/red]")
        sys.exit(1)

    metadata = None
    if args.metadata:
        metadata_path = Path(args.metadata)
        if metadata_path.exists():
            with open(metadata_path, encoding="utf-8") as f:
                metadata = yaml.safe_load(f)
        else:
            console.print(f"[yellow]Warning: Metadata file not found: {metadata_path}[/yellow]")

    only_categories = None
    if args.only:
        only_categories = [c.strip().upper() for c in args.only.split(",")]
        console.print(f"\n[bold yellow]Selective run: only {', '.join(only_categories)}[/bold yellow]")

    # --- Step 1: Context Extraction ---
    console.print("\n[bold]Step 1: Extracting context from venture documents...[/bold]")
    extractor = ContextExtractor()
    context = extractor.extract(docs_dir, metadata)
    console.print(f"[green]+ Context extracted for: {context.venture_name}[/green]")
    console.print(f"  Industry: {context.industry_vertical}")
    console.print(f"  Problem keywords: {', '.join(context.problem_keywords[:5])}...")
    console.print(f"  Named competitors: {', '.join(context.named_competitors) or 'None'}")

    # --- Step 2: Research Execution ---
    target_count = len(only_categories) if only_categories else 13
    console.print(f"\n[bold]Step 2: Executing research across {target_count} evidence categories...[/bold]")
    progress = ProgressTracker()
    runner = ResearchRunner(context, docs_dir, progress, only_categories=only_categories)
    results = asyncio.run(runner.run_all())

    # --- Step 3: Package Assembly ---
    console.print("\n[bold]Step 3: Assembling evidence package...[/bold]")
    assembler = PackageAssembler(
        context, results, output_dir,
        consultant_context=runner.consultant_context,
    )
    yaml_path, md_path = assembler.assemble()

    console.print(f"\n[bold green]+ Evidence package generated:[/bold green]")
    console.print(f"  YAML: {yaml_path}")
    console.print(f"  Markdown: {md_path}")
    console.print(f"  Raw reports: {output_dir / 'raw_reports'}/")


if __name__ == "__main__":
    main()
