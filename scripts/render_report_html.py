#!/usr/bin/env python3
"""Compile reports/8D_Report.md into a standalone styled HTML report with embedded figures.

Saves to reports/8D_Report.html.
"""
from __future__ import annotations

import re
from pathlib import Path
import mistune

REPO_ROOT = Path(__file__).resolve().parents[1]
MD_PATH = REPO_ROOT / "reports" / "8D_Report.md"
HTML_PATH = REPO_ROOT / "reports" / "8D_Report.html"


def render_html() -> None:
    """Render markdown 8D report to standalone HTML with custom CSS."""
    if not MD_PATH.exists():
        raise FileNotFoundError(f"8D Report source markdown not found at {MD_PATH}")

    md_content = MD_PATH.read_text(encoding="utf-8")

    # Use mistune with table and formatting plugins
    markdown = mistune.create_markdown(plugins=["table", "strikethrough"])
    html_body = markdown(md_content)

    # Wrap sections and enhance headings with styling hooks
    html_body = re.sub(r"<h2>(D\d\s*—\s*[^<]+)</h2>", r'<div class="discipline-card"><h2>\1</h2>', html_body)
    html_body = html_body.replace("---", '</div><hr class="section-divider"/>')

    # Append embedded figure gallery before D8 closure
    figures_html = """
    <div class="figure-gallery">
        <h3>Statistical Evidence & Process Artifact Gallery</h3>
        <div class="figure-card">
            <h4>Figure 1: Manufacturing Process Flow & QC Routing</h4>
            <img src="figures/process_flow.png" alt="Manufacturing Process Flow" />
            <p class="caption">Process sequence showing Saw, CNC Milling, and CNC Lathe component paths converging at Assembly.</p>
        </div>
        <div class="figure-card">
            <h4>Figure 2: Line-Wide Defect Pareto Analysis</h4>
            <img src="figures/pareto.png" alt="Defect Pareto Chart" />
            <p class="caption">Pareto distribution identifying Assembly Rework (52 parts, 6.48%) as the primary end-product non-conformance.</p>
        </div>
        <div class="figure-card">
            <h4>Figure 3: Univariate Screening Effect Sizes (FDR Corrected)</h4>
            <img src="figures/univariate_ranking.png" alt="Univariate Screening Ranking" />
            <p class="caption">Ranked effect sizes showing significant pass-vs-fail separation across upstream operations.</p>
        </div>
        <div class="figure-card">
            <h4>Figure 4: Root Cause 'Smoking-Gun' Isolation</h4>
            <img src="figures/smoking_gun.png" alt="Smoking Gun Chart" />
            <p class="caption">Distribution shift (Panel A) and defect surge to 16.9% in the short saw blank region (Panel B).</p>
        </div>
        <div class="figure-card">
            <h4>Figure 5: Statistical Process Control (I-MR Chart) — Operation 10</h4>
            <img src="figures/spc_chart.png" alt="SPC Control Chart" />
            <p class="caption">Individual-Moving Range chart with 3-sigma limits from in-control subset detecting out-of-control signals.</p>
        </div>
    </div>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>8D Corrective Action Report — Sentinel-8D (CiP-DMD)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0d47a1;
            --primary-dark: #002171;
            --primary-light: #e3f2fd;
            --accent: #d32f2f;
            --success: #2e7d32;
            --text: #263238;
            --text-muted: #546e7a;
            --border: #cfd8dc;
            --bg-card: #ffffff;
            --bg-page: #f8fafc;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-page);
            color: var(--text);
            line-height: 1.6;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 50px 60px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        }}

        h1 {{
            font-size: 26px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 8px;
            border-bottom: 3px solid var(--primary);
            padding-bottom: 12px;
        }}

        h2 {{
            font-size: 19px;
            font-weight: 700;
            color: var(--primary-dark);
            margin-top: 30px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 6px;
        }}

        h3 {{
            font-size: 15px;
            font-weight: 600;
            color: #37474f;
            margin-top: 18px;
            margin-bottom: 8px;
        }}

        h4 {{
            font-size: 13.5px;
            font-weight: 600;
            color: #455a64;
            margin-bottom: 6px;
        }}

        p, li {{
            font-size: 14px;
            color: #37474f;
            margin-bottom: 10px;
        }}

        ul, ol {{
            margin-left: 24px;
            margin-bottom: 16px;
        }}

        li {{
            margin-bottom: 6px;
        }}

        strong {{
            color: #1a237e;
        }}

        blockquote {{
            background: var(--primary-light);
            border-left: 4px solid var(--primary);
            padding: 12px 18px;
            margin: 16px 0;
            border-radius: 0 8px 8px 0;
            font-size: 13.5px;
            color: #0d47a1;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0;
            font-size: 13px;
        }}

        th, td {{
            padding: 9px 12px;
            border: 1px solid var(--border);
            text-align: left;
        }}

        th {{
            background-color: #f1f5f9;
            color: #1e293b;
            font-weight: 600;
        }}

        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}

        hr.section-divider {{
            border: 0;
            height: 1px;
            background: var(--border);
            margin: 30px 0;
        }}

        .discipline-card {{
            margin-bottom: 25px;
        }}

        .figure-gallery {{
            margin-top: 40px;
            border-top: 2px solid var(--primary);
            padding-top: 25px;
        }}

        .figure-card {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        }}

        .figure-card img {{
            width: 100%;
            height: auto;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            margin: 10px 0;
        }}

        .figure-card .caption {{
            font-size: 12px;
            color: var(--text-muted);
            font-style: italic;
            text-align: center;
        }}

        @media print {{
            body {{
                padding: 0;
                background: #ffffff;
            }}
            .container {{
                border: none;
                box-shadow: none;
                padding: 0;
                max-width: 100%;
            }}
            .discipline-card {{
                page-break-inside: avoid;
            }}
            .figure-card {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_body}
        {figures_html}
    </div>
</body>
</html>
"""

    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(full_html, encoding="utf-8")
    print(f"Successfully compiled 8D Report HTML to {HTML_PATH}")


if __name__ == "__main__":
    render_html()
