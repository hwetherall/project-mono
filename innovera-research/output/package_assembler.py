"""
Assembles all category results into the final evidence package.
"""
from datetime import datetime, timezone
from pathlib import Path

from context_extraction.models import ContextSignals
from evidence_categories.base import CategoryResult
from evidence_categories.registry import get_consumption_map, CATEGORY_REGISTRY
from market_research.registry import get_mr_consumption_map, MR_CATEGORY_REGISTRY
from output.yaml_formatter import format_yaml_package
from output.markdown_formatter import format_markdown_report


class PackageAssembler:
    """Combines all category outputs into the final evidence package."""

    def __init__(
        self,
        context: ContextSignals,
        results: dict[str, CategoryResult],
        output_dir: Path,
    ):
        self.context = context
        self.results = results
        self.output_dir = output_dir

        if context.research_mode == "market_research":
            self.consumption_map = get_mr_consumption_map()
            self.registry = MR_CATEGORY_REGISTRY
        else:
            self.consumption_map = get_consumption_map()
            self.registry = CATEGORY_REGISTRY

    def assemble(self) -> tuple[Path, Path]:
        """Produce both output formats. Returns (yaml_path, markdown_path)."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        venture_slug = self.context.venture_name.lower().replace(" ", "-")

        package = self._build_package(timestamp)

        # YAML output
        yaml_filename = f"{venture_slug}_evidence_{timestamp}.yaml"
        yaml_path = self.output_dir / yaml_filename
        yaml_content = format_yaml_package(package)
        yaml_path.write_text(yaml_content, encoding="utf-8")

        # Markdown output
        md_filename = f"{venture_slug}_evidence_{timestamp}.md"
        md_path = self.output_dir / md_filename
        md_content = format_markdown_report(package, self.context, self.results)
        md_path.write_text(md_content, encoding="utf-8")

        # Save raw reports individually
        raw_dir = self.output_dir / "raw_reports"
        raw_dir.mkdir(exist_ok=True)
        for cid, result in self.results.items():
            if result.raw_report:
                raw_path = raw_dir / f"{cid}_{venture_slug}.md"
                raw_path.write_text(result.raw_report, encoding="utf-8")

        return yaml_path, md_path

    def _build_package(self, timestamp: str) -> dict:
        """Build the complete package data structure."""
        total_sources = sum(len(r.sources) for r in self.results.values())
        successful = sum(1 for r in self.results.values() if r.status == "success")
        failed = sum(1 for r in self.results.values() if r.status == "failed")
        total_time = sum(r.execution_time_seconds for r in self.results.values())

        critical_gaps = []
        moderate_gaps = []
        for cid, result in self.results.items():
            meta = self.registry.get(cid)
            priority = "high" if meta and any(
                v == "primary" for v in meta.section_consumption.values()
            ) else "moderate"

            for gap in result.gaps:
                gap_entry = {
                    "category_id": cid,
                    "category_name": result.category_name,
                    "gap": gap,
                }
                if result.status == "failed" or priority == "high":
                    critical_gaps.append(gap_entry)
                else:
                    moderate_gaps.append(gap_entry)

        return {
            "research_package": {
                "metadata": {
                    "venture_name": self.context.venture_name,
                    "research_mode": self.context.research_mode,
                    "generated_at": timestamp,
                    "categories_executed": len(self.results),
                    "categories_succeeded": successful,
                    "categories_failed": failed,
                    "total_sources_consulted": total_sources,
                    "total_execution_seconds": round(total_time, 1),
                },
                "context_signals": self.context.model_dump(),
                "evidence": {
                    cid: {
                        "category_name": result.category_name,
                        "status": result.status,
                        "findings": result.structured_findings,
                        "sources": result.sources,
                        "gaps": result.gaps,
                        "execution_seconds": round(result.execution_time_seconds, 1),
                    }
                    for cid, result in sorted(self.results.items())
                },
                "consumption_map": self.consumption_map,
                "gap_summary": {
                    "critical_gaps": critical_gaps,
                    "moderate_gaps": moderate_gaps,
                },
            }
        }
