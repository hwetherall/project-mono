#!/usr/bin/env python3
"""
Build a clean, professional competitive-landscape HTML from competitive_table.json.
Designed for Innovera — a venture and innovation strategy firm.
"""

import json, html, datetime

with open("competitive_table.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ── Attribute metadata ──────────────────────────────────────────────────
attrs = data["attributes"]
attr_map = {a["attribute_id"]: a for a in attrs}

# Curated column order per group (skip 'name' — it's the row header)
group_meta = {
    "profile": {
        "label": "Company Profile",
        "color": "#0f172a",
        "cols": ["description", "year_founded", "hq_location", "revenue_estimate",
                 "employee_count", "ownership_structure"],
    },
    "manufacturing_technical": {
        "label": "Manufacturing & Technical",
        "color": "#1e3a5f",
        "cols": ["primary_product_category", "substrate_technology", "minimum_line_space",
                 "electrode_fabrication_capability", "manufacturing_scale",
                 "cleanroom_capability", "biocompatibility_materials", "cdmo_service_offering"],
    },
    "regulatory_quality": {
        "label": "Regulatory & Quality",
        "color": "#365314",
        "cols": ["iso_13485_status", "iso_10993_compliance", "fda_registration",
                 "mdr_eu_compliance", "quality_track_record", "liability_model"],
    },
    "market_positioning": {
        "label": "Market Positioning",
        "color": "#4c1d95",
        "cols": ["target_medical_applications", "key_oem_relationships",
                 "geographic_presence", "patent_count_medical", "vertical_integration_level"],
    },
    "strategic_positioning": {
        "label": "Strategic Positioning",
        "color": "#7c2d12",
        "cols": ["ma_activity", "business_model_type", "competitive_moat",
                 "medical_revenue_share", "strategic_threat_to_lgit"],
    },
    "custom": {
        "label": "Custom Parameters",
        "color": "#374151",
        "cols": [a["attribute_id"] for a in attrs if a["group"] == "custom"],
    },
}

# Shortened display labels
short_labels = {
    "description": "Description",
    "year_founded": "Founded",
    "hq_location": "HQ Location",
    "revenue_estimate": "Revenue (USD)",
    "employee_count": "Employees",
    "ownership_structure": "Ownership",
    "primary_product_category": "Product Category",
    "substrate_technology": "Substrate Tech",
    "minimum_line_space": "Min Line/Space",
    "electrode_fabrication_capability": "Electrode Fab",
    "manufacturing_scale": "Mfg Scale",
    "cleanroom_capability": "Cleanroom",
    "biocompatibility_materials": "Biocompat. Materials",
    "cdmo_service_offering": "CDMO Services",
    "iso_13485_status": "ISO 13485",
    "iso_10993_compliance": "ISO 10993",
    "fda_registration": "FDA Registered",
    "mdr_eu_compliance": "EU MDR / CE",
    "quality_track_record": "Quality Record",
    "liability_model": "Liability Model",
    "target_medical_applications": "Medical Apps",
    "key_oem_relationships": "Key OEM Partners",
    "geographic_presence": "Geography",
    "patent_count_medical": "Patent Portfolio",
    "vertical_integration_level": "Vertical Integ.",
    "ma_activity": "M&A Activity",
    "business_model_type": "Business Model",
    "competitive_moat": "Competitive Moat",
    "medical_revenue_share": "Medical Rev %",
    "strategic_threat_to_lgit": "LGIT Threat",
}

# For custom attributes, use their short name
for a in attrs:
    if a["attribute_id"] not in short_labels:
        # Truncate long custom names
        name = a["name"]
        if len(name) > 30:
            name = name[:28] + "…"
        short_labels[a["attribute_id"]] = name

# Build flat column list in group order
groups_in_order = []
all_columns = []
for gid, gm in group_meta.items():
    if gm["cols"]:
        groups_in_order.append(gid)
        all_columns.extend(gm["cols"])


def cell_text(val):
    if val is None:
        return ""
    if isinstance(val, bool):
        return "Yes" if val else "No"
    if isinstance(val, (int, float)):
        return str(int(val)) if val == int(val) else str(val)
    if isinstance(val, list):
        val = ", ".join(str(v) for v in val)
    val = str(val).strip()
    if len(val) <= 140:
        return val
    for sep in [". ", "; ", " — ", " - "]:
        idx = val.find(sep)
        if 15 < idx < 140:
            return val[: idx + 1].strip()
    return val[:137].rsplit(" ", 1)[0] + "…"


def esc(s):
    return html.escape(str(s))


# ── Filter & sort competitors ───────────────────────────────────────────
MIN_FILLED = 5
competitors = [
    c for c in data["competitors"]
    if sum(1 for v in c.get("attributes", {}).values()
           if v and v.get("value") is not None) >= MIN_FILLED
]
competitors = sorted(
    competitors,
    key=lambda c: (
        c["tier"],
        -sum(1 for v in c.get("attributes", {}).values()
             if v and v.get("value") is not None),
    ),
)

# ── Date for header ─────────────────────────────────────────────────────
gen_date = data.get("generated_at", "")[:10] or datetime.date.today().isoformat()

# ── Build HTML ──────────────────────────────────────────────────────────
o = []
o.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Competitive Landscape — {esc(data['venture_name'])}</title>
<style>
:root {{
  --bg: #fafbfc;
  --surface: #ffffff;
  --border: #e5e7eb;
  --border-strong: #d1d5db;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --accent: #0f172a;
  --green: #166534;
  --green-bg: #f0fdf4;
  --red: #991b1b;
  --red-bg: #fef2f2;
  --t1: #0f172a;
  --t2: #475569;
  --t3: #94a3b8;
  --row-alt: #f9fafb;
  --row-hover: #f3f4f6;
  --shadow: 0 1px 3px rgba(0,0,0,.04), 0 1px 2px rgba(0,0,0,.06);
  --shadow-lg: 0 4px 6px rgba(0,0,0,.04), 0 2px 4px rgba(0,0,0,.06);
  --radius: 6px;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: var(--font);
  background: var(--bg);
  color: var(--text-primary);
  padding: 40px 32px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

/* ── Header ─────────────────────────────────────────────────────────── */
.page-header {{
  max-width: 1200px;
  margin: 0 auto 32px;
}}
.page-header .brand {{
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 8px;
}}
.page-header h1 {{
  font-size: 26px;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: -0.3px;
  line-height: 1.2;
}}
.page-header .subtitle {{
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
  font-weight: 400;
}}
.page-header .meta-row {{
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 16px;
  flex-wrap: wrap;
}}
.page-header .meta-item {{
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}}
.page-header .meta-item .dot {{
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
}}

/* ── Legend ──────────────────────────────────────────────────────────── */
.legend {{
  max-width: 1200px;
  margin: 0 auto 20px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}}
.legend-item {{
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}}
.legend-item .swatch {{
  width: 14px;
  height: 4px;
  border-radius: 2px;
}}

/* ── Table container ────────────────────────────────────────────────── */
.table-wrap {{
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-lg);
}}

/* ── Table ──────────────────────────────────────────────────────────── */
table {{
  border-collapse: collapse;
  width: 100%;
  font-size: 12px;
  line-height: 1.5;
}}

th, td {{
  padding: 8px 12px;
  border: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
}}

/* Group header row */
.grp th {{
  text-align: center;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: #fff;
  padding: 10px 12px;
  border-bottom: none;
}}

/* Column header row */
.col-hdr th {{
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg);
  position: sticky;
  top: 0;
  z-index: 2;
  min-width: 120px;
  max-width: 180px;
  border-bottom: 2px solid var(--border-strong);
  white-space: nowrap;
  padding: 8px 12px;
}}

/* Frozen company column */
.company-cell {{
  position: sticky;
  left: 0;
  z-index: 1;
  background: var(--surface);
  min-width: 200px;
  max-width: 240px;
  border-right: 2px solid var(--border-strong) !important;
  padding: 10px 14px;
}}
.col-hdr .company-cell {{
  position: sticky;
  left: 0;
  z-index: 3;
  background: var(--bg);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
}}

.company-cell .name {{
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}}
.company-cell .type-label {{
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-top: 2px;
}}

/* Tier badges */
.tier {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 3px;
  color: #fff;
  margin-left: 6px;
  vertical-align: middle;
  letter-spacing: 0.3px;
}}
.tier-1 {{ background: var(--t1); }}
.tier-2 {{ background: var(--t2); }}
.tier-3 {{ background: var(--t3); }}

/* Cell states */
td.empty {{
  color: var(--text-muted);
  text-align: center;
  font-size: 11px;
}}
td.yes {{
  color: var(--green);
  font-weight: 600;
  background: var(--green-bg);
}}
td.no {{
  color: var(--red);
  font-weight: 500;
  background: var(--red-bg);
}}

/* Row striping & hover */
tbody tr:nth-child(even) td {{ background: var(--row-alt); }}
tbody tr:nth-child(even) .company-cell {{ background: var(--row-alt); }}
tbody tr:hover td {{ background: var(--row-hover) !important; }}
tbody tr:hover .company-cell {{ background: var(--row-hover) !important; }}

/* Tier divider */
.tier-break td {{ border-top: 3px solid var(--accent); }}

/* Cell with long content — tooltip on hover */
td .cell-content {{
  display: block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
td:hover .cell-content {{
  white-space: normal;
  overflow: visible;
}}

/* ── Footer ─────────────────────────────────────────────────────────── */
.page-footer {{
  max-width: 1200px;
  margin: 24px auto 0;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}}

/* ── Print ──────────────────────────────────────────────────────────── */
@media print {{
  body {{ padding: 8px; background: #fff; }}
  .table-wrap {{ box-shadow: none; border: none; }}
  td, th {{ font-size: 8.5px; padding: 3px 6px; }}
  .page-header {{ margin-bottom: 16px; }}
  .page-footer {{ margin-top: 12px; }}
}}
</style>
</head>
<body>

<div class="page-header">
  <div class="brand">Innovera Research</div>
  <h1>Competitive Landscape Matrix</h1>
  <div class="subtitle">{esc(data['venture_name'])} — {esc(data['industry'])}</div>
  <div class="meta-row">
    <div class="meta-item"><span class="dot"></span>{len(competitors)} companies</div>
    <div class="meta-item"><span class="dot"></span>{len(all_columns)} attributes</div>
    <div class="meta-item"><span class="dot"></span>Generated {gen_date}</div>
  </div>
</div>

<div class="legend">""")

for gid in groups_in_order:
    gm = group_meta[gid]
    o.append(f'  <div class="legend-item"><span class="swatch" style="background:{gm["color"]}"></span>{esc(gm["label"])}</div>')

o.append("""</div>

<div class="table-wrap">
<table>
<thead>
<tr class="grp">
  <th style="background:var(--accent);border-right:2px solid var(--border-strong)" rowspan="2">Company</th>""")

for gid in groups_in_order:
    gm = group_meta[gid]
    span = len(gm["cols"])
    o.append(f'  <th colspan="{span}" style="background:{gm["color"]}">{esc(gm["label"])}</th>')

o.append('</tr>\n<tr class="col-hdr">')

for col_id in all_columns:
    label = short_labels.get(col_id, col_id)
    o.append(f"  <th>{esc(label)}</th>")

o.append("</tr>\n</thead>\n<tbody>")

# ── Rows ────────────────────────────────────────────────────────────────
tier_badge = {
    1: '<span class="tier tier-1">T1</span>',
    2: '<span class="tier tier-2">T2</span>',
    3: '<span class="tier tier-3">T3</span>',
}

prev_tier = None
for comp in competitors:
    tier = comp["tier"]
    tr_class = ' class="tier-break"' if prev_tier is not None and tier != prev_tier else ""
    badge = tier_badge.get(tier, tier_badge[3])
    ctype = comp.get("competitor_type", "")

    o.append(f"<tr{tr_class}>")
    o.append(f'  <td class="company-cell"><div class="name">{esc(comp["name"])} {badge}</div><div class="type-label">{esc(ctype)}</div></td>')

    attrs_dict = comp.get("attributes", {})
    for col_id in all_columns:
        attr = attrs_dict.get(col_id, {})
        val = attr.get("value") if attr else None
        text = cell_text(val)

        if not text:
            o.append('  <td class="empty">—</td>')
        elif text in ("Yes", "True"):
            o.append(f'  <td class="yes">✓ Yes</td>')
        elif text in ("No", "False"):
            o.append(f'  <td class="no">✗ No</td>')
        else:
            o.append(f"  <td>{esc(text)}</td>")

    o.append("</tr>")
    prev_tier = tier

o.append(f"""</tbody>
</table>
</div>

<div class="page-footer">
  <span>Innovera Research · Venture & Innovation Strategy</span>
  <span>{len(competitors)} of {len(data['competitors'])} competitors shown (≥{MIN_FILLED} attributes populated)</span>
</div>

</body>
</html>""")

out_path = "competitive_matrix.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(o))

print(f"Written {out_path}: {len(competitors)} companies x {len(all_columns)} columns")
