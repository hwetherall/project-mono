"""
EC-02: Competitor Landscape & Positioning

Deep research category that maps direct competitors, adjacent solutions,
and DIY alternatives. Produces a competitor list consumed by Phase 2 categories.
"""
import re
from pathlib import Path
from evidence_categories.base import BaseCategory, CategoryResult
from context_extraction.models import ContextSignals
from config.settings import GPTR_CONFIG_DIR


class EC02CompetitorLandscape(BaseCategory):

    @property
    def category_id(self) -> str:
        return "EC-02"

    @property
    def category_name(self) -> str:
        return "Competitor Landscape & Positioning"

    def get_report_type(self) -> str:
        return "deep"

    def get_config_path(self) -> Path:
        return GPTR_CONFIG_DIR / "deep_landscape.json"

    def build_query(self) -> str:
        competitor_seed = ""
        if self.context.named_competitors:
            names = ", ".join(self.context.named_competitors)
            competitor_seed = f"\n\nKnown competitors to start with (search for more): {names}"

        workaround_context = ""
        if self.context.workaround_mentions:
            workarounds = ", ".join(self.context.workaround_mentions)
            workaround_context = f"\n\nKnown workarounds customers use today: {workarounds}"

        # Build discovery queries based on spec
        problem_kw = ", ".join(self.context.problem_keywords[:5])

        query = f"""Conduct a comprehensive competitive landscape analysis for the following venture:

**Venture:** {self.context.venture_name}
**Industry:** {self.context.industry_vertical} / {self.context.sub_vertical or 'General'}
**Geography:** {self.context.geography}
**Solution category:** {self.context.solution_category}
**Problem being solved:** {self.context.problem_summary}
**Target customer:** {self.context.target_customer_summary}
{competitor_seed}
{workaround_context}

Research and report on:

1. **Direct Competitors**: Companies offering products/services that directly address the same problem for the same target customer. Search for "{self.context.solution_category} companies {self.context.geography}", "{problem_kw} software vendors", and "{problem_kw} solutions comparison". For each competitor found, include: what they do, who they target, their positioning/messaging, pricing model (if public), known strengths, known weaknesses, and funding stage.

2. **Adjacent Solutions**: Products that partially address the problem or serve an adjacent market that could expand into this space. Search for "alternatives to {', '.join(self.context.workaround_mentions[:3]) if self.context.workaround_mentions else self.context.solution_category}". Include the same details as above.

3. **DIY Alternatives**: Manual processes, spreadsheets, internal tools, outsourced services, or consultancies that customers currently use to address this problem without a dedicated product. Search for "{problem_kw} how companies solve", "{problem_kw} consulting firms services", "{problem_kw} manual process workaround".

4. **Do-Nothing Analysis**: What happens when organizations don't adopt any solution? How prevalent is inaction, and what does it cost?

5. **Landscape Summary**: Total competitors found, market maturity assessment (early/growing/mature/consolidating), dominant approach in the market, the gap no current player adequately addresses, and fragmentation level.

Structure the report with clear sections for each of the above. For each competitor, use a consistent format with the company name in bold. Be specific — name companies, cite sources, provide concrete details rather than generalities. If pricing information is not public, say so explicitly rather than guessing.

Focus on {self.context.geography} but include global players that compete in this market."""

        return query

    def parse_report(self, raw_report: str) -> dict:
        structured = {
            "raw_report_text": raw_report,
            "competitor_names_extracted": self._extract_competitor_names(raw_report),
            "landscape_maturity": self._extract_field(raw_report, "maturity"),
        }
        return structured

    def _extract_competitor_names(self, report: str) -> list[str]:
        """
        Extract competitor names from the report using heuristics.
        Looks for bold text patterns commonly used for company names.
        """
        names = []
        # Match **CompanyName** patterns (common in markdown reports)
        bold_pattern = re.findall(r'\*\*([A-Z][A-Za-z0-9\s&\.\-]+?)\*\*', report)
        # Filter out section headers and common non-company phrases
        skip_phrases = {
            "direct competitors", "adjacent solutions", "diy alternatives",
            "do-nothing analysis", "landscape summary", "key strengths",
            "known weaknesses", "pricing", "target market", "description",
            "venture", "industry", "geography", "solution category",
            "problem being solved", "target customer", "research and report",
            "note", "important", "summary", "conclusion", "sources",
        }
        for name in bold_pattern:
            name_clean = name.strip()
            if (
                len(name_clean) > 2
                and len(name_clean) < 50
                and name_clean.lower() not in skip_phrases
                and not any(skip in name_clean.lower() for skip in skip_phrases)
                and name_clean not in names
            ):
                names.append(name_clean)
        return names

    def _extract_field(self, report: str, field_name: str) -> str:
        return "see raw report"

    def get_competitor_list(self, result: CategoryResult) -> list[str]:
        """
        Public method for Phase 2 categories to get the competitor list.
        Called by the orchestrator after EC-02 completes.
        """
        if result and result.structured_findings:
            names = result.structured_findings.get("competitor_names_extracted", [])
            all_names = list(set(names + self.context.named_competitors))
            return all_names
        return self.context.named_competitors
