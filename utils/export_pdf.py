"""
Topperify AI - Premium Export
Generates glorious PDF notes, flashcards, revision sheets, mindmap PNGs,
and a ZIP bundle containing everything. All in-memory via io.BytesIO.
"""

import io
import zipfile
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Premium Color Palette ──────────────────────────────────────────────────

P = {
    "bg": HexColor("#0B0F19"),
    "bg_card": HexColor("#1A1A2E"),
    "bg_section": HexColor("#141428"),
    "text": HexColor("#F1F5F9"),
    "text_muted": HexColor("#64748B"),
    "primary": HexColor("#6366F1"),
    "primary_glow": HexColor("#A5B4FC"),
    "definition": HexColor("#60A5FA"),
    "formula": HexColor("#A78BFA"),
    "example": HexColor("#34D399"),
    "tip": HexColor("#FBBF24"),
    "memory": HexColor("#A3E635"),
    "mistake": HexColor("#F87171"),
    "concept": HexColor("#22D3EE"),
    "accent_line": HexColor("#334155"),
}

# ── Font Registration (with fallback to Helvetica) ─────────────────────────

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"

FONT_HEADING = "Helvetica-Bold"
FONT_BODY = "Helvetica"
FONT_MONO = "Courier"

_heading_registered = False
_body_registered = False
_mono_registered = False


def _register_fonts():
    """Register Inter, Instrument Serif, Plus Jakarta Sans, GeistMono."""
    global FONT_HEADING, FONT_BODY, FONT_MONO, _heading_registered, _body_registered, _mono_registered
    if _heading_registered:
        return

    # --- Serif heading: Instrument Serif ---
    iserif = FONTS_DIR / "InstrumentSerif-Regular.ttf"
    iserif_i = FONTS_DIR / "InstrumentSerif-Italic.ttf"
    if iserif.exists():
        try:
            pdfmetrics.registerFont(TTFont("InstrumentSerif", str(iserif)))
            if iserif_i.exists():
                pdfmetrics.registerFont(TTFont("InstrumentSerif-Italic", str(iserif_i)))
                from reportlab.pdfbase.pdfmetrics import registerFontFamily
                registerFontFamily(
                    "InstrumentSerif",
                    normal="InstrumentSerif",
                    italic="InstrumentSerif-Italic",
                    bold="InstrumentSerif",
                    boldItalic="InstrumentSerif-Italic",
                )
            FONT_HEADING = "InstrumentSerif"
        except Exception:
            pass

    # --- Body: Inter (variable font) ---
    inter = FONTS_DIR / "Inter-Variable.ttf"
    if inter.exists():
        try:
            pdfmetrics.registerFont(TTFont("Inter", str(inter)))
            pdfmetrics.registerFont(TTFont("Inter-Bold", str(inter)))
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            registerFontFamily(
                "Inter",
                normal="Inter",
                bold="Inter-Bold",
                italic="Inter",
                boldItalic="Inter-Bold",
            )
            FONT_BODY = "Inter"
        except Exception:
            pass

    # --- Bold body: Plus Jakarta Sans 700 (for section titles) ---
    pjs_bold = FONTS_DIR / "PlusJakartaSans-700Normal.ttf"
    if pjs_bold.exists():
        try:
            pdfmetrics.registerFont(TTFont("PJS-Bold", str(pjs_bold)))
        except Exception:
            pass

    # --- Monospace: GeistMono ---
    geist_mono = FONTS_DIR / "GeistMono-Regular.ttf"
    if geist_mono.exists():
        try:
            pdfmetrics.registerFont(TTFont("GeistMono", str(geist_mono)))
            FONT_MONO = "GeistMono"
        except Exception:
            pass

    _heading_registered = True
    _body_registered = True
    _mono_registered = True


_register_fonts()


# ── Style Builder ──────────────────────────────────────────────────────────


def _build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CoverTitle", fontName="InstrumentSerif", fontSize=28, leading=34,
        alignment=TA_CENTER, textColor=P["primary"], spaceAfter=8, tracking=100,
    ))
    styles.add(ParagraphStyle(
        name="CoverSub", fontName="Inter", fontSize=13, leading=18,
        alignment=TA_CENTER, textColor=P["text_muted"], spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="CoverChapter", fontName="InstrumentSerif", fontSize=22, leading=28,
        alignment=TA_CENTER, textColor=P["primary_glow"], spaceAfter=12, tracking=100,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle", fontName="PJS-Bold", fontSize=15, leading=20,
        textColor=P["primary"], spaceBefore=14, spaceAfter=6, tracking=100,
    ))
    styles.add(ParagraphStyle(
        name="CardLabel", fontName="Inter", fontSize=7, leading=10,
        textColor=P["primary_glow"], spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="CardTitle", fontName="PJS-Bold", fontSize=10, leading=14,
        textColor=P["text"], spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="CardBody", fontName="Inter", fontSize=9, leading=13,
        textColor=P["text_muted"], spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="FooterText", fontName="Inter", fontSize=7, leading=10,
        alignment=TA_CENTER, textColor=P["text_muted"],
    ))
    styles.add(ParagraphStyle(
        name="BulletItem", fontName="Inter", fontSize=9, leading=13,
        textColor=P["text_muted"], leftIndent=10, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="FlashcardQ", fontName="InstrumentSerif", fontSize=11, leading=15,
        alignment=TA_CENTER, textColor=P["primary_glow"], spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="FlashcardA", fontName="Inter", fontSize=9, leading=14,
        alignment=TA_CENTER, textColor=P["text"], spaceAfter=6,
    ))
    return styles


# ── Helpers ────────────────────────────────────────────────────────────────


def _safe(text) -> str:
    if not text:
        return ""
    s = str(text)
    for ch, esc in [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;")]:
        s = s.replace(ch, esc)
    return s


def _section(elements, title: str, color: HexColor, styles):
    elements.append(Spacer(1, 6 * mm))
    # Thin accent line above section
    elements.append(Table(
        [[""]], colWidths=[170 * mm],
        style=TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 1, color),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]),
    ))
    elements.append(Paragraph(
        f'<font color="{color.hexval()}"><b>{_safe(title)}</b></font>',
        styles["SectionTitle"],
    ))


def _card(elements, label: str, title: str, body: str, color: HexColor, styles):
    """Dark glassmorphism card with colored left accent bar."""
    inner = Table(
        [
            [Paragraph(
                f'<font color="{color.hexval()}" size="7"><b>{_safe(label)}</b></font>',
                styles["CardLabel"],
            )],
            [Paragraph(f"<b>{_safe(title)}</b>", styles["CardTitle"])] if title else [""],
            [Paragraph(_safe(body), styles["CardBody"])] if body else [""],
        ],
        colWidths=[152 * mm],
    )
    inner.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, -1), P["bg_card"]),
    ]))

    # Card with colored left bar
    card = Table(
        [["", inner]],
        colWidths=[3 * mm, 165 * mm],
    )
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), color),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    elements.append(card)
    elements.append(Spacer(1, 2.5 * mm))


def _build_doc(buffer, title: str):
    def _draw_bg(canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFillColor(P["bg"])
        canvas_obj.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas_obj.restoreState()

    return SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"Topperify AI - {title}",
        author="Topperify AI",
        onFirstPage=_draw_bg,
        onLaterPages=_draw_bg,
    )


def _cover_page(elements, data: dict, styles):
    """Premium dark cover page with chapter info."""
    elements.append(Spacer(1, 25 * mm))

    # Decorative top line
    elements.append(Table(
        [[""]], colWidths=[40 * mm],
        style=TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 2, P["primary"]),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    ))
    elements.append(Spacer(1, 3 * mm))

    elements.append(Paragraph('TOPPERIFY AI', styles["CoverTitle"]))
    elements.append(Paragraph(
        _safe(data.get("subject", "Study Notes")), styles["CoverSub"],
    ))
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(
        _safe(data.get("chapter_title", "Untitled Chapter")),
        styles["CoverChapter"],
    ))

    cover = data.get("cover_page", {})
    tagline = cover.get("tagline", "")
    if tagline:
        elements.append(Paragraph(
            f'<i>"{_safe(tagline)}"</i>', styles["CoverSub"],
        ))

    meta = []
    if cover.get("difficulty"):
        meta.append(f"Difficulty: {cover['difficulty']}")
    if cover.get("study_time"):
        meta.append(f"Study Time: {cover['study_time']}")
    if cover.get("exam_importance"):
        meta.append(f"Exam Importance: {cover['exam_importance']}")
    if meta:
        elements.append(Spacer(1, 5 * mm))
        elements.append(Paragraph(" | ".join(meta), styles["CoverSub"]))

    goals = cover.get("learning_goals", [])
    if goals:
        elements.append(Spacer(1, 6 * mm))
        elements.append(Paragraph("<b>Learning Goals</b>", styles["CardTitle"]))
        for g in goals:
            elements.append(Paragraph(f"• {_safe(g)}", styles["BulletItem"]))

    # Decorative bottom line
    elements.append(Spacer(1, 8 * mm))
    elements.append(Table(
        [[""]], colWidths=[40 * mm],
        style=TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 2, P["primary"]),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    ))

    elements.append(PageBreak())


def _footer(elements, styles):
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(
        f"Generated by Topperify AI - {datetime.now().strftime('%B %d, %Y')}",
        styles["FooterText"],
    ))


# ═══════════════════════════════════════════════════════════════════════════
# 1. FULL NOTES PDF
# ═══════════════════════════════════════════════════════════════════════════


def generate_notes_pdf(data: dict) -> bytes:
    """Premium full notes PDF with all sections."""
    buf = io.BytesIO()
    styles = _build_styles()
    doc = _build_doc(buf, data.get("chapter_title", "Notes"))
    els: list = []

    _cover_page(els, data, styles)

    # Definitions
    for item in data.get("definitions", []):
        _card(els, "DEFINITION", item.get("term", ""), item.get("meaning", ""),
              P["definition"], styles)

    # Key Concepts
    for item in data.get("key_concepts", []):
        _card(els, "CONCEPT", item.get("title", ""), item.get("explanation", ""),
              P["concept"], styles)

    # Formulas
    for item in data.get("formulas", []):
        body = f"{item.get('formula', '')}  -  {item.get('meaning', '')}"
        _card(els, "FORMULA", item.get("name", ""), body, P["formula"], styles)

    # Examples
    for item in data.get("examples", []):
        body = f"A: {item.get('solution', '')}"
        _card(els, "EXAMPLE", f"Q: {item.get('question', '')}", body,
              P["example"], styles)

    # Exam Tips
    for tip in [t for t in data.get("exam_tips", []) if t]:
        _card(els, "EXAM TIP", "", tip, P["tip"], styles)

    # Memory Tricks
    for t in [t for t in data.get("memory_tricks", []) if t]:
        _card(els, "MEMORY TRICK", "", t, P["memory"], styles)

    # Common Mistakes
    for m in [m for m in data.get("common_mistakes", []) if m]:
        _card(els, "COMMON MISTAKE", "", m, P["mistake"], styles)

    # Important Questions
    for q in [q for q in data.get("important_questions", []) if q]:
        els.append(Paragraph(f"• {_safe(q)}", styles["BulletItem"]))

    # Flashcards
    flashcards = data.get("flashcards", [])
    if flashcards:
        els.append(PageBreak())
        _section(els, "Flashcards", P["primary"], styles)
        for fc in flashcards:
            _card(els, "FLASHCARD",
                  f"Q: {fc.get('question', '')}",
                  f"A: {fc.get('answer', '')}",
                  P["primary"], styles)

    # Revision Sheet
    rev = data.get("revision_sheet", {})
    has_rev = any(rev.get(k) for k in ["definitions", "facts", "formulas", "questions"])
    if has_rev:
        els.append(PageBreak())
        _section(els, "Quick Revision Sheet", P["primary"], styles)
        for key, label in [
            ("definitions", "Key Definitions"),
            ("facts", "Important Facts"),
            ("formulas", "Key Formulas"),
            ("questions", "Important Questions"),
        ]:
            for item in rev.get(key, []):
                els.append(Paragraph(f"▸ {_safe(item)}", styles["BulletItem"]))
        els.append(Spacer(1, 3 * mm))

    _footer(els, styles)
    doc.build(els)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 2. FLASHCARDS PDF
# ═══════════════════════════════════════════════════════════════════════════


def generate_flashcards_pdf(flashcards: list[dict], title: str = "Flashcards") -> bytes:
    """PDF containing only the flashcards in a clean Q&A layout."""
    buf = io.BytesIO()
    styles = _build_styles()
    doc = _build_doc(buf, title)
    els: list = []

    els.append(Spacer(1, 15 * mm))
    els.append(Paragraph('FLASHCARDS', styles["CoverTitle"]))
    els.append(Paragraph(_safe(title), styles["CoverChapter"]))
    els.append(Spacer(1, 8 * mm))
    els.append(Table(
        [[""]], colWidths=[50 * mm],
        style=TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 2, P["primary"]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    ))

    for i, fc in enumerate(flashcards):
        if i > 0 and i % 4 == 0:
            els.append(PageBreak())

        q = fc.get("question", "")
        a = fc.get("answer", "")
        if not q and not a:
            continue

        # Front: question
        card_data = Table(
            [
                [Paragraph(
                    f'<font color="{P["primary_glow"].hexval()}"><b>Q</b></font>',
                    styles["CardLabel"],
                )],
                [Paragraph(f"<b>{_safe(q)}</b>", styles["FlashcardQ"])],
                [Spacer(1, 2 * mm)],
                [Paragraph(
                    f'<font color="{P["primary"].hexval()}" size="7">ANSWER</font>',
                    styles["CardLabel"],
                )],
                [Paragraph(_safe(a), styles["FlashcardA"])],
            ],
            colWidths=[160 * mm],
        )
        card_data.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, -1), P["bg_card"]),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        els.append(card_data)
        els.append(Spacer(1, 3 * mm))

    _footer(els, styles)
    doc.build(els)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 3. REVISION SHEET PDF
# ═══════════════════════════════════════════════════════════════════════════


def generate_revision_pdf(revision_data: dict, chapter_title: str = "Revision") -> bytes:
    """Compact revision sheet PDF with definitions, facts, formulas, questions."""
    buf = io.BytesIO()
    styles = _build_styles()
    doc = _build_doc(buf, f"Revision - {chapter_title}")
    els: list = []

    els.append(Spacer(1, 15 * mm))
    els.append(Paragraph('QUICK REVISION', styles["CoverTitle"]))
    els.append(Paragraph(_safe(chapter_title), styles["CoverChapter"]))
    els.append(Spacer(1, 6 * mm))
    els.append(Table(
        [[""]], colWidths=[50 * mm],
        style=TableStyle([
            ("LINEBELOW", (0, 0), (-1, -1), 2, P["primary"]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    ))
    els.append(Spacer(1, 4 * mm))

    sections = [
        ("definitions", "Key Definitions", P["definition"]),
        ("facts", "Important Facts", P["example"]),
        ("formulas", "Key Formulas", P["formula"]),
        ("questions", "Important Questions", P["tip"]),
    ]

    for key, label, color in sections:
        items = revision_data.get(key, [])
        if not items:
            continue
        _section(els, label, color, styles)
        for item in items:
            # Mini card per item
            row = Table(
                [[Paragraph(f"▸ {_safe(item)}", styles["BulletItem"])]],
                colWidths=[162 * mm],
            )
            row.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), P["bg_card"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            els.append(row)
            els.append(Spacer(1, 1.5 * mm))

    _footer(els, styles)
    doc.build(els)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 4. MINDMAP PNG
# ═══════════════════════════════════════════════════════════════════════════


def generate_mindmap_png(mindmap_data: dict) -> bytes:
    """Render mindmap as a premium PNG matching the UI's streamlit-agraph graph."""
    root = mindmap_data.get("root", "Topic") if mindmap_data else "Topic"
    children = mindmap_data.get("children", {}) if mindmap_data else {}

    try:
        import networkx as nx
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return _kaleido_fallback(root, children)

    if not children:
        return _kaleido_fallback(root, children)

    BG = "#0B0F19"
    BRANCH_COLORS = [
        "#3B82F6", "#8B5CF6", "#10B981", "#F59E0B",
        "#EF4444", "#06B6D4", "#84CC16", "#EC4899",
    ]

    G = nx.Graph()
    G.add_node(root, color="#6366F1", size=900, node_type="root")

    for i, (branch, leaves) in enumerate(children.items()):
        color = BRANCH_COLORS[i % len(BRANCH_COLORS)]
        G.add_node(branch, color=color, size=450, node_type="branch")
        G.add_edge(root, branch, color=color, width=2.0)

        if isinstance(leaves, list):
            for leaf in leaves:
                leaf_id = f"{branch}_{leaf}"
                G.add_node(leaf_id, label=str(leaf), color=color, size=150, node_type="leaf")
                G.add_edge(branch, leaf_id, color=color, width=0.8)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.1, 1.1)
    ax.axis("off")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.02)

    title_font = None
    label_font = None
    leaf_font_obj = None
    for fpath in [
        FONTS_DIR / "Geist-Bold.ttf",
        FONTS_DIR / "GeistMono-Regular.ttf",
        FONTS_DIR / "PlusJakartaSans-500Normal.ttf",
    ]:
        if fpath.exists():
            try:
                from matplotlib import font_manager
                font_manager.fontManager.addfont(str(fpath))
            except Exception:
                pass
    try:
        title_font = matplotlib.font_manager.FontProperties(fname=str(FONTS_DIR / "Geist-Bold.ttf"))
        label_font = matplotlib.font_manager.FontProperties(fname=str(FONTS_DIR / "Geist-Bold.ttf"), size=10)
        leaf_font_obj = matplotlib.font_manager.FontProperties(fname=str(FONTS_DIR / "PlusJakartaSans-500Normal.ttf"), size=8)
    except Exception:
        pass

    ax.set_title(
        f"{root}",
        fontproperties=title_font,
        fontsize=18,
        fontweight="bold",
        color="#F1F5F9",
        pad=16,
    )

    pos = nx.spring_layout(G, k=1.8, iterations=80, seed=42, scale=1.0)

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        ax.plot(
            [x0, x1], [y0, y1],
            color=data.get("color", "#334155"),
            linewidth=data.get("width", 1.0),
            alpha=0.5,
            solid_capstyle="round",
            zorder=1,
        )

    for node in G.nodes():
        x, y = pos[node]
        data = G.nodes[node]
        color = data.get("color", "#6366F1")
        size = data.get("size", 200)
        ntype = data.get("node_type", "leaf")

        ax.scatter(
            x, y,
            s=size,
            c=color,
            edgecolors="white",
            linewidths=0.0,
            alpha=0.95,
            zorder=2,
        )

        label = data.get("label", node)
        if ntype == "root":
            fp = title_font or label_font
            fs = 13
            fw = "bold"
            fc = "#FFFFFF"
        elif ntype == "branch":
            fp = label_font
            fs = 10
            fw = "bold"
            fc = "#FFFFFF"
        else:
            fp = leaf_font_obj
            fs = 8
            fw = "normal"
            fc = "#F1F5F9"

        offset_y = 0.07 if ntype == "root" else 0.05 if ntype == "branch" else 0.04
        ax.text(
            x, y + offset_y,
            label,
            fontproperties=fp,
            fontsize=fs,
            fontweight=fw,
            color=fc,
            ha="center",
            va="bottom",
            zorder=3,
        )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=BG, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    return buf.getvalue()


def _kaleido_fallback(root: str, children: dict) -> bytes:
    """Fallback using Plotly + kaleido when Pillow is unavailable."""
    labels = [root]
    parents = [""]
    values = [1]
    branch_colors = [
        "#6366F1", "#3B82F6", "#8B5CF6", "#10B981",
        "#F59E0B", "#EF4444", "#06B6D4", "#84CC16",
    ]
    for i, (branch, leaves) in enumerate(children.items()):
        labels.append(branch)
        parents.append(root)
        values.append(len(leaves) if isinstance(leaves, list) else 1)
        if isinstance(leaves, list):
            for leaf in leaves:
                labels.append(str(leaf))
                parents.append(branch)
                values.append(1)

    color_map = {root: "#6366F1"}
    for i, branch in enumerate(children.keys()):
        color_map[branch] = branch_colors[i % len(branch_colors)]
    node_colors = [color_map.get(label, "#6366F1") for label in labels]

    fig = go.Figure(go.Treemap(
        labels=labels, parents=parents, values=values,
        marker=dict(colors=node_colors),
        textfont=dict(size=14, color="white"),
        branchvalues="total",
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="#0B0F19",
        font=dict(color="white"),
        title=dict(text=f"<b>{root}</b> - Mind Map", font=dict(size=20, color="#F1F5F9"), x=0.5, xanchor="center"),
        width=900, height=600,
    )
    return fig.to_image(format="png", scale=2)


# ═══════════════════════════════════════════════════════════════════════════
# 5. ZIP BUNDLE
# ═══════════════════════════════════════════════════════════════════════════


def generate_all_zip(data: dict) -> bytes:
    """Generate a ZIP containing notes PDF, flashcards PDF, revision PDF, mindmap PNG."""
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
                generate_flashcards_pdf(flashcards, data.get("chapter_title", "Flashcards")),
            )

        # Revision sheet
        revision = data.get("revision_sheet", {})
        has_rev = any(revision.get(k) for k in ["definitions", "facts", "formulas", "questions"])
        if has_rev:
            zf.writestr(
                f"topperify_{chapter}_revision.pdf",
                generate_revision_pdf(revision, data.get("chapter_title", "Revision")),
            )

        # Mindmap PNG
        mindmap = data.get("mindmap", {})
        if mindmap and mindmap.get("children"):
            zf.writestr(f"topperify_{chapter}_mindmap.png", generate_mindmap_png(mindmap))

    return buf.getvalue()
