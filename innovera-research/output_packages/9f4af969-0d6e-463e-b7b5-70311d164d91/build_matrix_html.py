import json, html

with open("competitive_table.json", "r", encoding="utf-8") as f:
    data = json.load(f)

attrs = data["attributes"]
attr_ids = [a["attribute_id"] for a in attrs if a["attribute_id"] != "name"]
attr_labels = {a["attribute_id"]: a["name"] for a in attrs}
attr_groups = {a["attribute_id"]: a["group"] for a in attrs}

group_colors = {
    "profile": "#1a365d",
    "technical": "#744210",
    "regulatory": "#22543d",
    "commercial": "#553c9a",
    "strategic": "#9b2c2c",
}
group_labels = {
    "profile": "Company Profile",
    "technical": "Technical Capabilities",
    "regulatory": "Regulatory & Quality",
    "commercial": "Commercial",
    "strategic": "Strategic Position",
}

# Shortened display labels
short_labels = {
    "description": "Description",
    "hq_location": "HQ",
    "revenue_estimate": "Revenue (USD)",
    "employee_count": "Employees",
    "supply_chain_role": "Supply Chain Role",
    "primary_device_segments": "Device Segments",
    "substrate_technology": "Substrate Tech",
    "biocompatible_materials": "Biocompat.",
    "implantable_vs_wearable": "Implant / Wear",
    "manufacturing_scale": "Mfg Scale",
    "iso_13485_certified": "ISO 13485",
    "fda_registration_status": "FDA Status",
    "key_oem_relationships": "Key OEM Partners",
    "business_model": "Business Model",
    "geographic_presence": "Geography",
    "vertical_integration_level": "Vertical Integ.",
    "competitive_moat": "Competitive Moat",
    "lgit_displacement_risk": "LGIT Threat",
}

exec_columns = list(short_labels.keys())


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
    if len(val) <= 100:
        return val
    for sep in [". ", "; ", " - "]:
        idx = val.find(sep)
        if 15 < idx < 100:
            return val[: idx + 1].strip()
    return val[:97].rsplit(" ", 1)[0] + "\u2026"


def esc(s):
    return html.escape(str(s))


# Filter out competitors with insufficient data (fewer than 5 filled attributes)
MIN_FILLED = 5
competitors = [
    c for c in data["competitors"]
    if sum(1 for v in c.get("attributes", {}).values() if v and v.get("value") is not None) >= MIN_FILLED
]

# Sort: tier 1 first, then by data completeness desc
competitors = sorted(
    competitors,
    key=lambda c: (
        c["tier"],
        -sum(
            1
            for v in c.get("attributes", {}).values()
            if v and v.get("value") is not None
        ),
    ),
)

# Group header spans
groups_in_order = []
col_spans = []
current_group = None
for col_id in exec_columns:
    g = attr_groups[col_id]
    if g != current_group:
        groups_in_order.append(g)
        col_spans.append(1)
        current_group = g
    else:
        col_spans[-1] += 1

# --- Build HTML ---
out = []
out.append(
    """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Competitive Landscape \u2014 LGIT MedTech</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f7fafc;color:#1a202c;padding:32px 24px}
.header{margin-bottom:20px}
.header h1{font-size:22px;font-weight:700;color:#1a202c;margin-bottom:2px}
.header .sub{font-size:13px;color:#718096}
.legend{display:flex;gap:18px;margin-bottom:18px;font-size:12px;flex-wrap:wrap}
.legend .item{display:flex;align-items:center;gap:5px}
.legend .swatch{width:12px;height:12px;border-radius:2px}
.table-wrap{overflow-x:auto;border:1px solid #e2e8f0;border-radius:8px;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.06)}
table{border-collapse:collapse;width:100%;font-size:11.5px;line-height:1.45}
th,td{padding:7px 9px;border:1px solid #e2e8f0;text-align:left;vertical-align:top}
.grp th{text-align:center;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:#fff;border-bottom:none}
.col th{font-size:10.5px;font-weight:600;color:#4a5568;background:#f7fafc;position:sticky;top:0;z-index:2;min-width:110px;max-width:170px;border-bottom:2px solid #cbd5e0;white-space:nowrap}
.col th.cc{min-width:170px;position:sticky;left:0;z-index:3;background:#f7fafc}
.cc{position:sticky;left:0;z-index:1;background:#fff;font-weight:600;min-width:170px;border-right:2px solid #cbd5e0!important;white-space:nowrap}
.cc .nm{font-size:12.5px;color:#1a202c}
.cc .tp{font-size:9.5px;color:#a0aec0;text-transform:uppercase;letter-spacing:.3px}
.tier{display:inline-block;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;color:#fff;margin-left:4px;vertical-align:middle}
.t1{background:#c53030}.t2{background:#b7791f}.t3{background:#718096}
td.e{color:#cbd5e0;text-align:center;font-style:italic;font-size:10px}
td.y{color:#276749;font-weight:600}
td.n{color:#c53030}
tr:nth-child(even) td{background:#fafbfc}
tr:nth-child(even) .cc{background:#fafbfc}
tr:hover td{background:#edf2f7!important}
tr:hover .cc{background:#edf2f7!important}
.td td{border-top:3px solid #2d3748}
@media print{body{padding:8px}td,th{font-size:8.5px;padding:3px 5px}.table-wrap{box-shadow:none;border:none}}
</style>
</head>
<body>
<div class="header">
<h1>Competitive Landscape Matrix</h1>
<div class="sub">LG Innotek MedTech Expansion &mdash; Medical Devices / MedTech &mdash; 2026-03-19</div>
</div>
<div class="legend">"""
)

for g in ["profile", "technical", "regulatory", "commercial", "strategic"]:
    out.append(
        f'<div class="item"><span class="swatch" style="background:{group_colors[g]}"></span>{group_labels[g]}</div>'
    )

out.append(
    """</div>
<div class="table-wrap">
<table>
<thead>
<tr class="grp">
<th style="background:#2d3748;border-right:2px solid #cbd5e0" rowspan="2">Company</th>"""
)

for i, g in enumerate(groups_in_order):
    out.append(
        f'<th colspan="{col_spans[i]}" style="background:{group_colors[g]}">{esc(group_labels[g])}</th>'
    )

out.append('</tr>\n<tr class="col">')
for col_id in exec_columns:
    out.append(f"<th>{esc(short_labels[col_id])}</th>")

out.append("</tr>\n</thead>\n<tbody>")

tier_html = {
    1: '<span class="tier t1">T1</span>',
    2: '<span class="tier t2">T2</span>',
    3: '<span class="tier t3">T3</span>',
}

prev_tier = None
for comp in competitors:
    tier = comp["tier"]
    tr_class = ' class="td"' if prev_tier is not None and tier != prev_tier else ""
    badge = tier_html.get(tier, tier_html[3])
    ctype = comp.get("competitor_type", "")

    out.append(f"<tr{tr_class}>")
    out.append(
        f'<td class="cc"><div class="nm">{esc(comp["name"])} {badge}</div><div class="tp">{esc(ctype)}</div></td>'
    )

    attrs_dict = comp.get("attributes", {})
    for col_id in exec_columns:
        attr = attrs_dict.get(col_id, {})
        val = attr.get("value") if attr else None
        text = cell_text(val)

        if not text:
            out.append('<td class="e">\u2014</td>')
        elif text in ("Yes", "True"):
            out.append('<td class="y">\u2713 Yes</td>')
        elif text in ("No", "False"):
            out.append('<td class="n">\u2717 No</td>')
        else:
            out.append(f"<td>{esc(text)}</td>")

    out.append("</tr>")
    prev_tier = tier

out.append("</tbody>\n</table>\n</div>\n</body>\n</html>")

out_path = "competitive_matrix.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"Written {out_path}: {len(competitors)} companies x {len(exec_columns)} columns")
