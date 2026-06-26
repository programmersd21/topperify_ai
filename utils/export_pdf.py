"""
Topperify AI - Modern HTML/CSS PDF Export
Uses Playwright to render beautiful glassmorphism PDFs matching the UI.
"""

import io
import os
import zipfile
from datetime import datetime


# Auto-install Playwright browsers on first import (for Streamlit Cloud)
# Install chromium (not just headless-shell) - this includes both variants
if not os.path.exists(os.path.expanduser("~/.cache/ms-playwright/chromium-1223")):
    os.system("playwright install chromium")


def _html_template(content: str, title: str) -> str:
    """Premium dark glassmorphism HTML template."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@700&family=Geist+Mono:wght@400&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        @page {{
            size: A4;
            margin: 15mm;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0B0F19 0%, #151B2C 100%);
            color: #F1F5F9;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .cover {{
            text-align: center;
            padding: 80px 40px;
            min-height: 70vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .cover-line {{
            width: 120px;
            height: 3px;
            background: linear-gradient(90deg, #6366F1, #A5B4FC);
            margin: 0 auto 20px;
            border-radius: 2px;
        }}
        
        .cover-title {{
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: 36px;
            font-weight: 700;
            letter-spacing: 2px;
            background: linear-gradient(135deg, #6366F1, #A5B4FC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 12px;
        }}
        
        .cover-subtitle {{
            font-size: 14px;
            color: #64748B;
            margin-bottom: 40px;
            letter-spacing: 1px;
        }}
        
        .cover-chapter {{
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: 28px;
            color: #A5B4FC;
            margin-bottom: 30px;
            letter-spacing: 1px;
        }}
        
        .cover-meta {{
            color: #64748B;
            font-size: 13px;
            margin: 20px 0;
        }}
        
        .section {{
            margin: 40px 0 20px;
            page-break-before: auto;
        }}
        
        .section-title {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 20px;
            font-weight: 700;
            color: #6366F1;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #334155;
            letter-spacing: 1px;
        }}
        
        .card {{
            background: rgba(26, 26, 46, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            border-left: 4px solid;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            page-break-inside: avoid;
        }}
        
        .card.definition {{ border-left-color: #60A5FA; }}
        .card.concept {{ border-left-color: #22D3EE; }}
        .card.formula {{ border-left-color: #A78BFA; }}
        .card.example {{ border-left-color: #34D399; }}
        .card.tip {{ border-left-color: #FBBF24; }}
        .card.memory {{ border-left-color: #A3E635; }}
        .card.mistake {{ border-left-color: #F87171; }}
        .card.flashcard {{ border-left-color: #6366F1; }}
        
        .card-label {{
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 8px;
            opacity: 0.8;
        }}
        
        .card.definition .card-label {{ color: #60A5FA; }}
        .card.concept .card-label {{ color: #22D3EE; }}
        .card.formula .card-label {{ color: #A78BFA; }}
        .card.example .card-label {{ color: #34D399; }}
        .card.tip .card-label {{ color: #FBBF24; }}
        .card.memory .card-label {{ color: #A3E635; }}
        .card.mistake .card-label {{ color: #F87171; }}
        .card.flashcard .card-label {{ color: #A5B4FC; }}
        
        .card-title {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 10px;
        }}
        
        .card-body {{
            font-size: 14px;
            color: #CBD5E1;
            line-height: 1.7;
        }}
        
        .footer {{
            text-align: center;
            color: #64748B;
            font-size: 11px;
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }}
        
        .bullet-item {{
            padding: 12px 16px;
            margin: 8px 0;
            background: rgba(26, 26, 46, 0.5);
            border-radius: 8px;
            border-left: 3px solid #6366F1;
        }}
        
        .flashcard-q {{
            font-family: 'Instrument Serif', Georgia, serif;
            font-size: 18px;
            color: #A5B4FC;
            margin-bottom: 12px;
            text-align: center;
        }}
        
        .flashcard-a {{
            font-size: 14px;
            color: #F1F5F9;
            text-align: center;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #334155;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""


def _cover_html(data: dict) -> str:
    """Generate cover page HTML."""
    cover = data.get("cover_page", {})
    chapter = data.get("chapter_title", "Untitled Chapter")
    subject = data.get("subject", "Study Notes")

    meta = []
    if cover.get("difficulty"):
        meta.append(f"Difficulty: {cover['difficulty']}")
    if cover.get("study_time"):
        meta.append(f"Study Time: {cover['study_time']}")
    if cover.get("exam_importance"):
        meta.append(f"Exam Importance: {cover['exam_importance']}")

    goals_html = ""
    if cover.get("learning_goals"):
        goals_html = "<div style='margin-top: 30px;'><h3 style='color: #F1F5F9; font-size: 16px; margin-bottom: 12px;'>Learning Goals</h3>"
        for goal in cover.get("learning_goals", []):
            goals_html += f"<div class='bullet-item'>• {goal}</div>"
        goals_html += "</div>"

    return f"""
    <div class="cover">
        <div class="cover-line"></div>
        <h1 class="cover-title">TOPPERIFY AI</h1>
        <p class="cover-subtitle">{subject}</p>
        <h2 class="cover-chapter">{chapter}</h2>
        {f'<p class="cover-meta">{" | ".join(meta)}</p>' if meta else ""}
        {goals_html}
        <div class="cover-line" style="margin-top: 40px;"></div>
    </div>
    <div style="page-break-after: always;"></div>
    """


def _sections_html(data: dict) -> str:
    """Generate all content sections HTML."""
    html = ""

    # Definitions
    definitions = data.get("definitions", [])
    if definitions:
        html += '<div class="section"><h2 class="section-title">Definitions</h2>'
        for item in definitions:
            html += f"""
            <div class="card definition">
                <div class="card-label">Definition</div>
                <div class="card-title">{item.get("term", "")}</div>
                <div class="card-body">{item.get("meaning", "")}</div>
            </div>
            """
        html += "</div>"

    # Key Concepts
    concepts = data.get("key_concepts", [])
    if concepts:
        html += '<div class="section"><h2 class="section-title">Key Concepts</h2>'
        for item in concepts:
            html += f"""
            <div class="card concept">
                <div class="card-label">Concept</div>
                <div class="card-title">{item.get("title", "")}</div>
                <div class="card-body">{item.get("explanation", "")}</div>
            </div>
            """
        html += "</div>"

    # Formulas
    formulas = data.get("formulas", [])
    if formulas:
        html += '<div class="section"><h2 class="section-title">Formulas</h2>'
        for item in formulas:
            html += f"""
            <div class="card formula">
                <div class="card-label">Formula</div>
                <div class="card-title">{item.get("name", "")}</div>
                <div class="card-body">{item.get("formula", "")} - {item.get("meaning", "")}</div>
            </div>
            """
        html += "</div>"

    # Examples
    examples = data.get("examples", [])
    if examples:
        html += '<div class="section"><h2 class="section-title">Worked Examples</h2>'
        for item in examples:
            html += f"""
            <div class="card example">
                <div class="card-label">Example</div>
                <div class="card-title">Q: {item.get("question", "")}</div>
                <div class="card-body">A: {item.get("solution", "")}</div>
            </div>
            """
        html += "</div>"

    # Exam Tips
    tips = [t for t in data.get("exam_tips", []) if t]
    if tips:
        html += '<div class="section"><h2 class="section-title">Exam Tips</h2>'
        for tip in tips:
            html += f"""
            <div class="card tip">
                <div class="card-label">Exam Tip</div>
                <div class="card-body">{tip}</div>
            </div>
            """
        html += "</div>"

    # Memory Tricks
    memory = [m for m in data.get("memory_tricks", []) if m]
    if memory:
        html += '<div class="section"><h2 class="section-title">Memory Tricks</h2>'
        for trick in memory:
            html += f"""
            <div class="card memory">
                <div class="card-label">Memory Trick</div>
                <div class="card-body">{trick}</div>
            </div>
            """
        html += "</div>"

    # Common Mistakes
    mistakes = [m for m in data.get("common_mistakes", []) if m]
    if mistakes:
        html += '<div class="section"><h2 class="section-title">Common Mistakes</h2>'
        for mistake in mistakes:
            html += f"""
            <div class="card mistake">
                <div class="card-label">Common Mistake</div>
                <div class="card-body">{mistake}</div>
            </div>
            """
        html += "</div>"

    return html


def _flashcards_html(flashcards: list[dict]) -> str:
    """Generate flashcards section HTML."""
    if not flashcards:
        return ""

    html = '<div style="page-break-before: always;"></div>'
    html += '<div class="section"><h2 class="section-title">Flashcards</h2>'

    for fc in flashcards:
        html += f"""
        <div class="card flashcard">
            <div class="card-label">Flashcard</div>
            <div class="flashcard-q"><strong>Q:</strong> {fc.get("question", "")}</div>
            <div class="flashcard-a"><strong>A:</strong> {fc.get("answer", "")}</div>
        </div>
        """

    html += "</div>"
    return html


def _revision_html(revision: dict) -> str:
    """Generate revision sheet HTML."""
    has_content = any(
        revision.get(k) for k in ["definitions", "facts", "formulas", "questions"]
    )
    if not has_content:
        return ""

    html = '<div style="page-break-before: always;"></div>'
    html += '<div class="section"><h2 class="section-title">Quick Revision Sheet</h2>'

    sections = [
        ("definitions", "Key Definitions"),
        ("facts", "Important Facts"),
        ("formulas", "Key Formulas"),
        ("questions", "Important Questions"),
    ]

    for key, label in sections:
        items = revision.get(key, [])
        if items:
            html += f'<h3 style="color: #A5B4FC; font-size: 16px; margin: 20px 0 12px;">{label}</h3>'
            for item in items:
                html += f'<div class="bullet-item">▸ {item}</div>'

    html += "</div>"
    return html


def _footer_html() -> str:
    """Generate footer HTML."""
    return f"""
    <div class="footer">
        Generated by Topperify AI - {datetime.now().strftime("%B %d, %Y")}
    </div>
    """


async def _render_pdf_async(html: str) -> bytes:
    """Render HTML to PDF using Playwright."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html, wait_until="networkidle")

        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "15mm", "right": "15mm", "bottom": "15mm", "left": "15mm"},
        )

        await browser.close()
        return pdf_bytes


def generate_notes_pdf(data: dict) -> bytes:
    """Generate full notes PDF with glassmorphism styling."""
    import asyncio

    content = _cover_html(data)
    content += _sections_html(data)
    content += _flashcards_html(data.get("flashcards", []))
    content += _revision_html(data.get("revision_sheet", {}))
    content += _footer_html()

    html = _html_template(content, data.get("chapter_title", "Notes"))

    return asyncio.run(_render_pdf_async(html))


def generate_flashcards_pdf(flashcards: list[dict], title: str = "Flashcards") -> bytes:
    """Generate flashcards-only PDF."""
    import asyncio

    content = f"""
    <div class="cover">
        <div class="cover-line"></div>
        <h1 class="cover-title">FLASHCARDS</h1>
        <h2 class="cover-chapter">{title}</h2>
        <div class="cover-line" style="margin-top: 40px;"></div>
    </div>
    <div style="page-break-after: always;"></div>
    """

    content += '<div class="section">'
    for fc in flashcards:
        content += f"""
        <div class="card flashcard">
            <div class="card-label">Flashcard</div>
            <div class="flashcard-q"><strong>Q:</strong> {fc.get("question", "")}</div>
            <div class="flashcard-a"><strong>A:</strong> {fc.get("answer", "")}</div>
        </div>
        """
    content += "</div>"
    content += _footer_html()

    html = _html_template(content, title)
    return asyncio.run(_render_pdf_async(html))


def generate_revision_pdf(
    revision_data: dict, chapter_title: str = "Revision"
) -> bytes:
    """Generate revision sheet PDF."""
    import asyncio

    content = f"""
    <div class="cover">
        <div class="cover-line"></div>
        <h1 class="cover-title">QUICK REVISION</h1>
        <h2 class="cover-chapter">{chapter_title}</h2>
        <div class="cover-line" style="margin-top: 40px;"></div>
    </div>
    <div style="page-break-after: always;"></div>
    """

    content += _revision_html(revision_data)
    content += _footer_html()

    html = _html_template(content, f"Revision - {chapter_title}")
    return asyncio.run(_render_pdf_async(html))


def generate_mindmap_png(mindmap_data: dict) -> bytes:
    """Generate mindmap PNG as a node-edge network graph via Playwright."""
    import asyncio
    import math

    root = mindmap_data.get("root", "Topic") if mindmap_data else "Topic"
    children = mindmap_data.get("children", {}) if mindmap_data else {}

    branch_colors = [
        "#6366F1",
        "#3B82F6",
        "#8B5CF6",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#06B6D4",
        "#84CC16",
    ]

    PAD = 40
    TITLE_H = 55

    def _text_width(text: str, font_size: int) -> int:
        return int(len(text) * font_size * 0.6 + font_size * 2)

    class Node:
        __slots__ = ("label", "x", "y", "r", "color", "font_size")

        def __init__(
            self, label: str, x: float, y: float, r: float, color: str, font_size: int
        ):
            self.label = label
            self.x = x
            self.y = y
            self.r = r
            self.color = color
            self.font_size = font_size

    root_tw = _text_width(root, 16)
    root_r = max(36, root_tw // 2 + 10)
    nodes: list[Node] = [Node(root, 0.0, 0.0, root_r, "#6366F1", 16)]
    node_map: dict[str, Node] = {root: nodes[0]}

    branches = list(children.items())
    n_branches = len(branches) if branches else 1

    branch_nodes_info: list[tuple[str, int, int]] = []
    for branch, _ in branches:
        tw = _text_width(branch, 13)
        br = max(26, tw // 2 + 8)
        branch_nodes_info.append((branch, tw, br))

    leaf_info: dict[str, tuple[str, int, int]] = {}
    for branch, leaves in branches:
        leaf_list = leaves if isinstance(leaves, list) else [str(leaves)]
        for lf in leaf_list:
            tw_l = _text_width(str(lf), 11)
            lr = max(20, tw_l // 2 + 6)
            leaf_info[str(lf)] = (str(lf), tw_l, lr)

    for i, (branch, tw, br) in enumerate(branch_nodes_info):
        angle = (2 * math.pi * i) / n_branches - math.pi / 2
        color = branch_colors[i % len(branch_colors)]

        dist = root_r + br + 25
        bx = dist * math.cos(angle)
        by = dist * math.sin(angle)
        bnode = Node(branch, bx, by, br, color, 13)
        nodes.append(bnode)
        node_map[branch] = bnode

        leaf_list = (
            children[branch]
            if isinstance(children[branch], list)
            else [str(children[branch])]
        )
        n_leaves = len(leaf_list)
        spread = min(0.6, 0.25 + 0.1 * n_leaves)

        for j, leaf in enumerate(leaf_list):
            leaf_label = str(leaf)
            if n_leaves == 1:
                la = angle
            else:
                la = angle + (j - (n_leaves - 1) / 2) * spread
            lr = leaf_info[leaf_label][2]
            leaf_dist = br + lr + 25
            lx = bx + leaf_dist * math.cos(la)
            ly = by + leaf_dist * math.sin(la)
            lnode = Node(leaf_label, lx, ly, lr, color, 11)
            nodes.append(lnode)
            node_map[leaf_label] = lnode

    min_x = min(n.x - n.r for n in nodes)
    max_x = max(n.x + n.r for n in nodes)
    min_y = min(n.y - n.r for n in nodes)
    max_y = max(n.y + n.r for n in nodes)

    W = int(max_x - min_x + PAD * 2)
    H = int(max_y - min_y + PAD * 2) + TITLE_H
    W = max(W, 400)
    H = max(H, 300)

    offset_x = -min_x + PAD
    offset_y = -min_y + PAD + TITLE_H

    for n in nodes:
        n.x += offset_x
        n.y += offset_y

    edge_list: list[tuple[str, str, str]] = []
    for branch, _ in branches:
        edge_list.append((root, branch, node_map[branch].color))
        leaf_list_v = children[branch]
        if isinstance(leaf_list_v, list):
            for lf in leaf_list_v:
                edge_list.append((branch, str(lf), node_map[branch].color))

    svg_edges = ""
    for src, dst, color in edge_list:
        sn, dn = node_map[src], node_map[dst]
        svg_edges += f'<line x1="{sn.x:.1f}" y1="{sn.y:.1f}" x2="{dn.x:.1f}" y2="{dn.y:.1f}" stroke="{color}" stroke-width="2"/>\n'

    svg_nodes = ""
    for n in nodes:
        svg_nodes += (
            f'<circle cx="{n.x:.1f}" cy="{n.y:.1f}" r="{n.r}" '
            f'fill="{n.color}" stroke="white" stroke-width="2" opacity="0.95"/>\n'
            f'<text x="{n.x:.1f}" y="{n.y:.1f}" text-anchor="middle" dominant-baseline="central" '
            f'fill="white" font-family="Inter, sans-serif" font-size="{n.font_size}" '
            f'font-weight="600">{n.label}</text>\n'
        )

    html = f"""<!DOCTYPE html>
<html><head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  body {{ margin:0; background:#0B0F19; width:{W}px; height:{H}px; overflow:hidden; }}
  .title {{ text-align:center; padding:14px 0 0; font:700 20px/1 Inter,sans-serif; color:#F1F5F9; }}
</style>
</head><body>
<div class="title"><b>{root}</b> - Mind Map</div>
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;top:0;left:0;">
{svg_edges}{svg_nodes}
</svg>
</body></html>"""

    async def capture_png():
        import tempfile
        from playwright.async_api import async_playwright

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(html)
            temp_path = f.name

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page(viewport={"width": W, "height": H})
                await page.goto(f"file://{temp_path}", wait_until="networkidle")
                await page.wait_for_timeout(1500)
                screenshot = await page.screenshot(type="png")
                await browser.close()
                return screenshot
        finally:
            import os

            os.unlink(temp_path)

    return asyncio.run(capture_png())


def generate_all_zip(data: dict) -> bytes:
    """Generate ZIP bundle with all exports."""
    buf = io.BytesIO()
    chapter = data.get("chapter_title", "notes").replace(" ", "_")

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Full notes
        zf.writestr(f"topperify_{chapter}_notes.pdf", generate_notes_pdf(data))

        # Flashcards
        flashcards = data.get("flashcards", [])
        if flashcards:
            zf.writestr(
                f"topperify_{chapter}_flashcards.pdf",
                generate_flashcards_pdf(
                    flashcards, data.get("chapter_title", "Flashcards")
                ),
            )

        # Revision sheet
        revision = data.get("revision_sheet", {})
        if any(
            revision.get(k) for k in ["definitions", "facts", "formulas", "questions"]
        ):
            zf.writestr(
                f"topperify_{chapter}_revision.pdf",
                generate_revision_pdf(revision, data.get("chapter_title", "Revision")),
            )

        # Mindmap PNG
        mindmap = data.get("mindmap", {})
        if mindmap and mindmap.get("children"):
            zf.writestr(
                f"topperify_{chapter}_mindmap.png", generate_mindmap_png(mindmap)
            )

    return buf.getvalue()
