#!/usr/bin/env python3
"""Reads tracker.csv and generates site/dashboard.html."""
import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote as url_quote

ROOT     = Path(__file__).parent
CSV_PATH = ROOT / "tracker.csv"
OUT_PATH = ROOT / "site" / "dashboard.html"

PAST_PHONE     = {"Phone Screen", "Interview", "Offer",
                  "Rejected - Phone", "Rejected - Interview", "Withdrawn"}
PAST_INTERVIEW = {"Interview", "Offer", "Rejected - Interview", "Withdrawn"}


def auto_ghost():
    """Mark Applied rows older than 2 weeks as Ghosted, rewriting tracker.csv in-place."""
    cutoff = date.today() - timedelta(weeks=2)
    rows, changed, fieldnames = [], False, []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            if (row.get("Status", "Applied") == "Applied"
                    and row.get("Date")
                    and date.fromisoformat(row["Date"]) <= cutoff):
                row["Status"] = "Ghosted"
                changed = True
            rows.append(row)
    if changed:
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        ghosted = sum(1 for r in rows if r["Status"] == "Ghosted")
        print(f"Auto-ghosted {ghosted} stale application(s).")


def load_data():
    rows = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("Date"):
                continue
            row.setdefault("Job ID", "")
            row.setdefault("Status", "Applied")
            rows.append(row)
    return rows


def compute_stats(rows):
    today    = date.today()
    statuses = [r["Status"] for r in rows]
    total    = len(rows)

    phones     = sum(1 for s in statuses if s in PAST_PHONE)
    interviews = sum(1 for s in statuses if s in PAST_INTERVIEW)
    offers     = statuses.count("Offer")

    if total:
        first_date     = date.fromisoformat(min(r["Date"] for r in rows))
        weeks_elapsed  = max(1, (today - first_date).days / 7)
        apps_per_week  = round(total / weeks_elapsed, 1)
        interview_rate = round(interviews / total * 100)
    else:
        apps_per_week  = 0
        interview_rate = 0

    weekly = {}
    for r in rows:
        d      = date.fromisoformat(r["Date"])
        monday = (d - timedelta(days=d.weekday())).isoformat()
        weekly[monday] = weekly.get(monday, 0) + 1

    flows = {
        "Applied|Phone Screen":           phones,
        "Applied|Rejected - Resume":      statuses.count("Rejected - Resume") + statuses.count("Rejected"),
        "Phone Screen|Interview":         interviews,
        "Phone Screen|Rejected - Phone":  statuses.count("Rejected - Phone"),
        "Interview|Offer":                offers,
        "Interview|Rejected - Interview": statuses.count("Rejected - Interview"),
        "Interview|Withdrawn":            statuses.count("Withdrawn"),
    }

    return {
        "total": total,
        "phones": phones,
        "interviews": interviews,
        "offers": offers,
        "apps_per_week": apps_per_week,
        "interview_rate": interview_rate,
        "weekly": weekly,
        "flows": flows,
        "generated": today.strftime("%B %d, %Y"),
        "rows": rows,
    }


def file_link(rel_path, label):
    if not rel_path or not (ROOT / rel_path).exists():
        return ""
    href = "../" + url_quote(rel_path, safe="/")
    return f'<a href="{href}" target="_blank">{label}</a>'


def badge_class(value, field):
    if field == "type":
        return "type-technical" if value == "technical" else "type-general"
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return f"status-{slug}"


def render_kpi_cards(s):
    cards = [
        ("Total Applied",  str(s["total"]),          "applications submitted"),
        ("Interview Rate", f'{s["interview_rate"]}%', "reached interview stage"),
        ("Offers",         str(s["offers"]),           "offers received"),
        ("Apps / Week",    str(s["apps_per_week"]),    "average rate"),
    ]
    parts = []
    for title, val, sub in cards:
        parts.append(
            f'<div class="kpi-card">'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-title">{title}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>'
        )
    return "\n".join(parts)


def render_table_rows(rows):
    parts = []
    for r in sorted(rows, key=lambda x: x["Date"], reverse=True):
        job_id      = r.get("Job ID", "")
        resume_path = r.get("PDF", "")
        letter_path = resume_path.replace("Resume.pdf", "Letter.pdf")
        links = " ".join(filter(None, [
            file_link(resume_path, "Resume"),
            file_link(letter_path, "Letter"),
        ]))
        parts.append(
            f'<tr>'
            f'<td>{r["Date"]}</td>'
            f'<td><code>{job_id}</code></td>'
            f'<td>{r["Company"]}</td>'
            f'<td>{r["Role"]}</td>'
            f'<td><span class="badge {badge_class(r["Resume Type"], "type")}">{r["Resume Type"]}</span></td>'
            f'<td><span class="badge {badge_class(r["Status"], "status")}">{r["Status"]}</span></td>'
            f'<td class="links-cell">{links}</td>'
            f'</tr>'
        )
    return "\n".join(parts)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Job Search Dashboard</title>
  <style>
    :root {
      --dark-blue: #003366;
      --mid-gray:  #666666;
      --font: "Times New Roman", Georgia, "Times", serif;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--font);
      color: #111;
      background: #fff;
      padding: 32px 40px;
      max-width: 1000px;
      margin: 0 auto;
    }
    .top-nav {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 28px;
    }
    .top-nav h1  { font-size: 20pt; color: var(--dark-blue); font-weight: bold; }
    .generated   { font-size: 9pt; color: var(--mid-gray); margin-top: 4px; }
    .top-nav a   { color: var(--dark-blue); font-size: 10pt; text-decoration: none; }
    .top-nav a:hover { text-decoration: underline; }
    h2 {
      font-size: 12pt; font-weight: bold; color: var(--dark-blue);
      text-transform: uppercase; letter-spacing: .05em;
      border-bottom: 1.5px solid var(--dark-blue);
      padding-bottom: 4px; margin: 28px 0 16px;
    }
    .kpi-row { display: flex; gap: 16px; }
    .kpi-card {
      flex: 1; border: 1px solid #d0d8e4;
      border-top: 3px solid var(--dark-blue); padding: 16px 20px;
    }
    .kpi-value { font-size: 28pt; font-weight: bold; color: var(--dark-blue); line-height: 1; }
    .kpi-title { font-size: 11pt; font-weight: bold; margin-top: 6px; }
    .kpi-sub   { font-size: 9pt; color: var(--mid-gray); margin-top: 2px; }
    .charts-row {
      display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start;
    }
    .chart-box { border: 1px solid #d0d8e4; padding: 16px; }
    .chart-box h3 {
      font-size: 10pt; font-weight: bold; color: var(--mid-gray);
      text-transform: uppercase; letter-spacing: .04em; margin-bottom: 12px;
    }
    svg { width: 100%; height: auto; display: block; }
    table { border-collapse: collapse; width: 100%; font-size: 10pt; margin-top: 4px; }
    thead tr { background: var(--dark-blue); color: #fff; }
    thead th { padding: 8px 10px; text-align: left; font-weight: bold; }
    tbody tr:nth-child(even) { background: #f7f9fb; }
    tbody tr:hover           { background: #e8eef5; }
    tbody td { padding: 6px 10px; vertical-align: middle; }
    code { font-size: 9pt; color: var(--mid-gray); }
    .badge {
      display: inline-block; padding: 2px 8px;
      border-radius: 3px; font-size: 9pt;
    }
    .status-applied            { background: #e8eef5; color: #003366; }
    .status-phone_screen       { background: #fff3cd; color: #7a5000; }
    .status-interview          { background: #d4edda; color: #155724; }
    .status-offer              { background: #c3e6cb; color: #0a4a1e; font-weight: bold; }
    .status-rejected           { background: #f8d7da; color: #721c24; }
    .status-rejected_resume    { background: #f8d7da; color: #721c24; }
    .status-rejected_phone     { background: #f8d7da; color: #721c24; }
    .status-rejected_interview { background: #f8d7da; color: #721c24; }
    .status-withdrawn          { background: #e9ecef; color: #495057; }
    .status-no_response        { background: #f5f5f5; color: #888; }
    .status-ghosted            { background: #f0f0f0; color: #888; font-style: italic; }
    .type-technical            { background: #e0e8f5; color: #003366; }
    .type-general              { background: #f0e8f5; color: #4a0066; }
    .links-cell a {
      color: var(--dark-blue); font-size: 9pt; text-decoration: none;
      padding: 1px 7px; border: 1px solid #c0cfe0; border-radius: 3px;
      margin-right: 4px; white-space: nowrap; display: inline-block;
    }
    .links-cell a:hover { background: #e8eef5; }
  </style>
</head>
<body>

<div class="top-nav">
  <div>
    <h1>Job Search Dashboard</h1>
    <div class="generated">Generated <!--GENERATED_DATE--></div>
  </div>
  <a href="index.html">← Resume</a>
</div>

<h2>Overview</h2>
<div class="kpi-row">
<!--KPI_CARDS-->
</div>

<h2>Application Funnel</h2>
<div class="charts-row">
  <div class="chart-box">
    <h3>Stage Breakdown</h3>
    <svg id="sankey-svg" viewBox="0 0 700 280"></svg>
  </div>
  <div class="chart-box">
    <h3>Applications per Week</h3>
    <svg id="bar-svg" viewBox="0 0 500 160"></svg>
  </div>
</div>

<h2>Applications</h2>
<table>
  <thead>
    <tr>
      <th>Date</th><th>Job ID</th><th>Company</th>
      <th>Role</th><th>Type</th><th>Status</th><th>Files</th>
    </tr>
  </thead>
  <tbody>
<!--TABLE_ROWS-->
  </tbody>
</table>

<script>const DATA = /*DATA_JSON*/null;</script>

<script>
// Sankey diagram
(function() {
  const W = 700, H = 280, NW = 14, GAP = 10;
  const COL_X  = [28, 200, 400, 570];
  const COLORS = {
    "Applied":              "#003366",
    "Phone Screen":         "#1a5fa8",
    "Interview":            "#2e8b57",
    "Offer":                "#1a7a3c",
    "Rejected - Resume":    "#b03030",
    "Rejected - Phone":     "#b03030",
    "Rejected - Interview": "#b03030",
    "Withdrawn":            "#888888",
  };
  const COLUMNS = [
    ["Applied"],
    ["Phone Screen", "Rejected - Resume"],
    ["Interview",    "Rejected - Phone"],
    ["Offer",        "Rejected - Interview", "Withdrawn"],
  ];
  const LINK_DEFS = [
    { src: "Applied",      tgt: "Phone Screen",         key: "Applied|Phone Screen" },
    { src: "Applied",      tgt: "Rejected - Resume",    key: "Applied|Rejected - Resume" },
    { src: "Phone Screen", tgt: "Interview",             key: "Phone Screen|Interview" },
    { src: "Phone Screen", tgt: "Rejected - Phone",     key: "Phone Screen|Rejected - Phone" },
    { src: "Interview",    tgt: "Offer",                key: "Interview|Offer" },
    { src: "Interview",    tgt: "Rejected - Interview", key: "Interview|Rejected - Interview" },
    { src: "Interview",    tgt: "Withdrawn",            key: "Interview|Withdrawn" },
  ];

  const total = DATA.total;
  if (total === 0) return;

  const SCALE = 220 / total;
  const MIN_H = 5;
  const ns    = "http://www.w3.org/2000/svg";
  const svg   = document.getElementById("sankey-svg");

  function el(tag, attrs, text) {
    const e = document.createElementNS(ns, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
    if (text != null) e.textContent = text;
    return e;
  }

  // Build nodes
  const nodes = {};
  COLUMNS.forEach((col, ci) => {
    col.forEach(name => {
      nodes[name] = { col: ci, x: COL_X[ci], color: COLORS[name],
                      inflow: 0, outflow: 0, count: 0, height: 0,
                      outOffset: 0, inOffset: 0, y: 0 };
    });
  });
  nodes["Applied"].inflow = total;

  const links = LINK_DEFS
    .map(d => ({ ...d, count: DATA.flows[d.key] || 0 }))
    .filter(l => l.count > 0);

  links.forEach(l => {
    nodes[l.src].outflow += l.count;
    nodes[l.tgt].inflow  += l.count;
  });

  Object.entries(nodes).forEach(([name, n]) => {
    n.count  = name === "Applied" ? total : Math.max(n.inflow, n.outflow);
    n.height = n.count > 0 ? Math.max(MIN_H, n.count * SCALE) : 0;
  });

  // Vertical layout
  COLUMNS.forEach((col) => {
    const vis    = col.filter(name => nodes[name].height > 0 || name === "Applied");
    const totalH = vis.reduce((s, n) => s + nodes[n].height, 0) + GAP * (vis.length - 1);
    let y = (H - totalH) / 2;
    vis.forEach(name => {
      nodes[name].y = y;
      y += nodes[name].height + GAP;
    });
  });

  // Draw links (behind nodes)
  links.forEach(link => {
    const S  = nodes[link.src], T = nodes[link.tgt];
    const lh = Math.max(3, link.count * SCALE);
    const sx = S.x + NW, sy0 = S.y + S.outOffset;
    const tx = T.x,       ty0 = T.y + T.inOffset;
    const mx = (sx + tx) / 2;
    const d  = "M " + sx + " " + sy0 +
               " C " + mx + " " + sy0 + ", " + mx + " " + ty0 + ", " + tx + " " + ty0 +
               " L " + tx + " " + (ty0 + lh) +
               " C " + mx + " " + (ty0 + lh) + ", " + mx + " " + (sy0 + lh) + ", " + sx + " " + (sy0 + lh) +
               " Z";
    svg.appendChild(el("path", { d, fill: S.color, opacity: "0.38" }));
    S.outOffset += lh;
    T.inOffset  += lh;
  });

  // Draw nodes
  Object.entries(nodes).forEach(([name, n]) => {
    if (n.height === 0) return;
    svg.appendChild(el("rect", { x: n.x, y: n.y, width: NW, height: n.height, fill: n.color }));
    const lx = n.col === 0 ? n.x - 4 : n.x + NW + 5;
    const la = n.col === 0 ? "end" : "start";
    svg.appendChild(el("text", {
      x: lx, y: n.y + n.height / 2 + 4,
      "font-size": 10, "font-family": "Times New Roman, serif",
      fill: "#222", "text-anchor": la,
    }, name + " (" + n.count + ")"));
  });

  // Empty state
  if (links.length === 0) {
    svg.appendChild(el("text", {
      x: W / 2, y: H / 2 + 6,
      "text-anchor": "middle", fill: "#888",
      "font-size": 11, "font-family": "Times New Roman, serif",
    }, "No stage transitions yet — all applications pending"));
  }
})();
</script>

<script>
// Weekly bar chart
(function() {
  const weekly = DATA.weekly;
  const keys   = Object.keys(weekly).sort();
  if (keys.length === 0) return;

  const W = 500, H = 160;
  const ML = 28, MR = 10, MT = 10, MB = 36;
  const cW = W - ML - MR, cH = H - MT - MB;

  const maxVal = Math.max(...Object.values(weekly));
  const slot   = cW / keys.length;
  const barW   = Math.max(10, slot * 0.65);

  function scaleY(v) { return v === 0 ? 0 : Math.max(4, (v / maxVal) * cH); }

  const svg = document.getElementById("bar-svg");
  const ns  = "http://www.w3.org/2000/svg";

  function el(tag, attrs, text) {
    const e = document.createElementNS(ns, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
    if (text != null) e.textContent = text;
    return e;
  }

  // Gridlines + y-axis labels
  [0, 0.5, 1].forEach(f => {
    const y = MT + cH * (1 - f);
    svg.appendChild(el("line", { x1: ML, x2: ML + cW, y1: y, y2: y, stroke: "#e0e0e0", "stroke-width": 1 }));
    svg.appendChild(el("text", {
      x: ML - 4, y: y + 4, "font-size": 8,
      "font-family": "Times New Roman, serif", fill: "#888", "text-anchor": "end",
    }, String(Math.round(maxVal * f))));
  });

  // Bars
  keys.forEach((week, i) => {
    const count = weekly[week];
    const bh    = scaleY(count);
    const bx    = ML + i * slot + (slot - barW) / 2;
    const by    = MT + cH - bh;

    if (count > 0) {
      svg.appendChild(el("rect", { x: bx, y: by, width: barW, height: bh, fill: "#003366", opacity: 0.8 }));
      svg.appendChild(el("text", {
        x: bx + barW / 2, y: by - 3, "font-size": 9,
        "font-family": "Times New Roman, serif", fill: "#003366", "text-anchor": "middle",
      }, String(count)));
    }

    // X label (MM/DD)
    const d    = new Date(week + "T12:00:00");
    const lbl  = (d.getMonth() + 1) + "/" + String(d.getDate()).padStart(2, "0");
    const rot  = keys.length > 6;
    const lx   = bx + barW / 2;
    const ly   = MT + cH + (rot ? 12 : 14);
    const attrs = { x: lx, y: ly, "font-size": 9, "font-family": "Times New Roman, serif",
                    fill: "#444", "text-anchor": rot ? "end" : "middle" };
    if (rot) attrs.transform = "rotate(-35 " + lx + " " + ly + ")";
    svg.appendChild(el("text", attrs, lbl));
  });

  // Baseline
  svg.appendChild(el("line", { x1: ML, x2: ML + cW, y1: MT + cH, y2: MT + cH, stroke: "#ccc", "stroke-width": 1 }));
})();
</script>

</body>
</html>"""


def main():
    auto_ghost()
    rows  = load_data()
    stats = compute_stats(rows)

    js_data = {k: v for k, v in stats.items() if k not in ("rows", "generated")}
    data_json = json.dumps(js_data, indent=2, ensure_ascii=False)

    html = (HTML_TEMPLATE
            .replace("<!--GENERATED_DATE-->", stats["generated"])
            .replace("<!--KPI_CARDS-->",      render_kpi_cards(stats))
            .replace("<!--TABLE_ROWS-->",      render_table_rows(stats["rows"]))
            .replace("/*DATA_JSON*/null",      data_json))

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard written → {OUT_PATH}")


if __name__ == "__main__":
    main()
