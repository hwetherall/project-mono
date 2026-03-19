"""
Tiered consultant domain lists and sector-specific domain selection.
"""
from typing import Optional


# Tier 1 — Global Strategy Firms (highest authority)
TIER1_DOMAINS = [
    "mckinsey.com",
    "bcg.com",
    "bcgperspectives.com",
    "bain.com",
]

# Tier 2 — Big Four + Major Consultancies
TIER2_DOMAINS = [
    "pwc.com",
    "ey.com",
    "deloitte.com",
    "kpmg.com",
    "accenture.com",
    "oliverwyman.com",
    "rolandberger.com",
    "strategyand.pwc.com",
    "lek.com",
]

# Tier 3 — Industry Research & Analyst Firms
TIER3_DOMAINS = [
    "gartner.com",
    "forrester.com",
    "idc.com",
    "woodmac.com",
    "ihsmarkit.com",
    "spglobal.com",
    "frost.com",
    "mordorintelligence.com",
    "grandviewresearch.com",
    "marketsandmarkets.com",
    "verifiedmarketresearch.com",
]

# Tier 4 — Sector-Specific (selected by industry_vertical)
TIER4_BY_SECTOR: dict[str, list[str]] = {
    "energy": ["woodmac.com", "lazard.com", "bnef.com"],
    "cleantech": ["woodmac.com", "lazard.com", "bnef.com"],
    "oil": ["woodmac.com", "ihsmarkit.com"],
    "utilities": ["woodmac.com", "lazard.com", "bnef.com"],
    "healthcare": ["evaluate.com", "iqvia.com"],
    "pharma": ["evaluate.com", "iqvia.com"],
    "biotech": ["evaluate.com", "iqvia.com"],
    "medtech": ["evaluate.com", "iqvia.com"],
    "technology": ["cb-insights.com", "pitchbook.com", "crunchbase.com"],
    "software": ["cb-insights.com", "pitchbook.com", "crunchbase.com"],
    "saas": ["cb-insights.com", "pitchbook.com", "crunchbase.com"],
    "fintech": ["cb-insights.com", "pitchbook.com"],
    "ai": ["cb-insights.com", "pitchbook.com", "crunchbase.com"],
}

# Map domains to firm display names
DOMAIN_TO_FIRM: dict[str, str] = {
    "mckinsey.com": "McKinsey",
    "bcg.com": "BCG",
    "bcgperspectives.com": "BCG",
    "bain.com": "Bain",
    "pwc.com": "PwC",
    "ey.com": "EY",
    "deloitte.com": "Deloitte",
    "kpmg.com": "KPMG",
    "accenture.com": "Accenture",
    "oliverwyman.com": "Oliver Wyman",
    "rolandberger.com": "Roland Berger",
    "strategyand.pwc.com": "Strategy&",
    "lek.com": "L.E.K. Consulting",
    "gartner.com": "Gartner",
    "forrester.com": "Forrester",
    "idc.com": "IDC",
    "woodmac.com": "Wood Mackenzie",
    "ihsmarkit.com": "IHS Markit",
    "spglobal.com": "S&P Global",
    "frost.com": "Frost & Sullivan",
    "mordorintelligence.com": "Mordor Intelligence",
    "grandviewresearch.com": "Grand View Research",
    "marketsandmarkets.com": "MarketsandMarkets",
    "verifiedmarketresearch.com": "Verified Market Research",
    "lazard.com": "Lazard",
    "bnef.com": "BloombergNEF",
    "evaluate.com": "Evaluate",
    "iqvia.com": "IQVIA",
    "cb-insights.com": "CB Insights",
    "pitchbook.com": "PitchBook",
    "crunchbase.com": "Crunchbase",
}

# Map domains to their tier number
DOMAIN_TO_TIER: dict[str, int] = {}
for _d in TIER1_DOMAINS:
    DOMAIN_TO_TIER[_d] = 1
for _d in TIER2_DOMAINS:
    DOMAIN_TO_TIER[_d] = 2
for _d in TIER3_DOMAINS:
    DOMAIN_TO_TIER[_d] = 3
for _sector_domains in TIER4_BY_SECTOR.values():
    for _d in _sector_domains:
        if _d not in DOMAIN_TO_TIER:
            DOMAIN_TO_TIER[_d] = 4


def get_domains_for_context(
    industry_vertical: Optional[str] = None,
    include_tier3: bool = True,
) -> list[str]:
    """Select the right consultant domains based on industry vertical.

    Always includes Tier 1 + 2.
    Includes Tier 3 when include_tier3 is True.
    Includes Tier 4 domains matching the industry vertical.
    """
    domains = list(TIER1_DOMAINS) + list(TIER2_DOMAINS)

    if include_tier3:
        domains.extend(TIER3_DOMAINS)

    if industry_vertical:
        vertical_lower = industry_vertical.lower()
        for sector_key, sector_domains in TIER4_BY_SECTOR.items():
            if sector_key in vertical_lower or vertical_lower in sector_key:
                for d in sector_domains:
                    if d not in domains:
                        domains.append(d)

    return domains


def firm_name_from_url(url: str) -> str:
    """Extract the consulting firm name from a URL."""
    url_lower = url.lower()
    for domain, name in DOMAIN_TO_FIRM.items():
        if domain in url_lower:
            return name
    return "Unknown"


def tier_from_url(url: str) -> int:
    """Determine the tier of a source from its URL."""
    url_lower = url.lower()
    for domain, tier in DOMAIN_TO_TIER.items():
        if domain in url_lower:
            return tier
    return 4  # Default to lowest tier for unknown domains
