"""
Topperify AI - Note Renderer
Premium UI with glassmorphism, smooth animations, and Apple/Linear/Stripe aesthetics.
"""

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# ── Font Constants ────────────────────────────────────────────────────────
FONT_HEADING = "'Instrument Serif', 'Georgia', serif"
FONT_BODY = "'Inter', 'Plus Jakarta Sans', -apple-system, sans-serif"
FONT_MONO = "'Geist Mono', 'JetBrains Mono', monospace"


# ═══════════════════════════════════════════════════════════════════════════
#  GLOBAL STYLES - injected once at page load
# ═══════════════════════════════════════════════════════════════════════════


def inject_global_styles():
    """Inject global CSS for the entire app. Call once in streamlit_app.py."""
    st.html(
        """
    <style>
    /* ── Font Import ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@300;400;500;600&family=Geist+Mono:wght@400;500;600&display=swap');

    /* ══════════════════════════════════════════════════════════════
       ROOT VARIABLES - design tokens
       ══════════════════════════════════════════════════════════════ */
    :root {
        --font-heading: 'Instrument Serif', 'Georgia', serif;
        --font-body: 'Inter', 'Plus Jakarta Sans', -apple-system, sans-serif;
        --font-mono: 'Geist Mono', 'JetBrains Mono', monospace;
        --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
        --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
        --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
        --glass-bg: rgba(15, 23, 42, 0.6);
        --glass-border: rgba(148, 163, 184, 0.08);
        --glass-blur: blur(20px);
        --glow-blue: 0 0 40px rgba(59, 130, 246, 0.15);
        --glow-purple: 0 0 40px rgba(139, 92, 246, 0.15);
        --glow-emerald: 0 0 40px rgba(16, 185, 129, 0.15);
    }

    /* ── Remove header bar, keep sidebar button ── */
    [data-testid="stHeader"] {background:transparent !important;box-shadow:none !important;border:none !important;}
    [data-testid="stToolbarActions"] {display:none !important;}
    [data-testid="stAppDeployButton"] {display:none !important;}
    #MainMenu {display:none !important;}
    [data-testid="stMainMenu"] {display:none !important;}

    /* ══════════════════════════════════════════════════════════════
       GLOBAL RESET & BASE
       ══════════════════════════════════════════════════════════════ */
    html {
        scroll-behavior: smooth;
    }

    html, body {
        font-family: var(--font-body);
        font-size: 15px;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        letter-spacing: 0;
        color: #F1F5F9;
    }

    /* Animated mesh gradient background */
    .stApp {
        background: 
            radial-gradient(ellipse 80% 50% at 20% 40%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse 60% 40% at 80% 20%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse 50% 60% at 50% 80%, rgba(16, 185, 129, 0.04) 0%, transparent 50%),
            #0B0F19 !important;
        background-attachment: fixed !important;
    }

    .block-container {
        padding-top: 2rem !important;
        max-width: 1100px !important;
        padding-bottom: 4rem !important;
    }

    /* Hide Streamlit branding */
    footer {visibility: hidden;}

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { 
        background: rgba(148, 163, 184, 0.15); 
        border-radius: 999px;
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: rgba(148, 163, 184, 0.25); 
    }

    /* ══════════════════════════════════════════════════════════════
       TYPOGRAPHY
       ══════════════════════════════════════════════════════════════ */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3 {
        font-family: var(--font-heading) !important;letter-spacing:0.03em;
        letter-spacing: -0.03em !important;
        line-height: 1.15 !important;
        font-weight: 700 !important;
    }

    p, li, span, div {
        line-height: 1.7 !important;
    }

    code, pre, .formula-text {
        font-family: var(--font-mono) !important;
    }

    /* ══════════════════════════════════════════════════════════════
       SIDEBAR - Glassmorphism
       ══════════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.06) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] textarea {
        font-family: var(--font-body) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: var(--font-heading) !important;letter-spacing:0.03em;
        letter-spacing: -0.02em !important;
    }

    /* ══════════════════════════════════════════════════════════════
       TABS - Smooth pill-style
       ══════════════════════════════════════════════════════════════ */
    [data-testid="stTabs"] {
        gap: 4px !important;
    }

    [data-testid="stTabs"] button {
        font-family: var(--font-heading) !important;letter-spacing:0.03em;
        font-weight: 500 !important;
        letter-spacing: -0.01em !important;
        font-size: 0.9rem !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        transition: all 0.3s var(--ease-out-expo) !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        color: #64748B !important;
    }

    [data-testid="stTabs"] button:hover {
        background: rgba(148, 163, 184, 0.06) !important;
        color: #F1F5F9 !important;
    }

    [data-testid="stTabs"] button[data-selected="true"],
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: rgba(99, 102, 241, 0.12) !important;
        color: #A5B4FC !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.08) !important;
    }

    /* ══════════════════════════════════════════════════════════════
       BUTTONS - Premium micro-interactions
       ══════════════════════════════════════════════════════════════ */
    .stButton button {
        font-family: var(--font-heading) !important;letter-spacing:0.03em;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        transition: all 0.3s var(--ease-out-expo) !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    .stButton button::before {
        content: '' !important;
        position: absolute !important;
        inset: 0 !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, transparent 50%) !important;
        opacity: 0 !important;
        transition: opacity 0.3s ease !important;
    }

    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
        border-color: rgba(148, 163, 184, 0.2) !important;
    }

    .stButton button:hover::before {
        opacity: 1 !important;
    }

    .stButton button:active {
        transform: translateY(0) !important;
        transition-duration: 0.1s !important;
    }

    /* Primary button glow */
    .stButton button[kind="primary"],
    .stButton button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.2) !important;
        color: white !important;
    }

    .stButton button[kind="primary"]:hover {
        box-shadow: 0 0 40px rgba(99, 102, 241, 0.35) !important;
        transform: translateY(-2px) !important;
    }

    /* ══════════════════════════════════════════════════════════════
       INPUTS - Focus states
       ══════════════════════════════════════════════════════════════ */
    label, .stTextInput label, .stSelectbox label {
        font-family: var(--font-heading) !important;letter-spacing:0.03em;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0 !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s var(--ease-out-expo) !important;
        padding: 12px 16px !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: rgba(99, 102, 241, 0.4) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1), 0 0 20px rgba(99, 102, 241, 0.08) !important;
    }

    /* ══════════════════════════════════════════════════════════════
       EXPANDER - Glass effect
       ══════════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        font-family: var(--font-heading) !important;letter-spacing:0.03em;
        font-weight: 500 !important;
        border-radius: 12px !important;
        transition: all 0.3s var(--ease-out-expo) !important;
    }

    .streamlit-expanderHeader:hover {
        background: rgba(148, 163, 184, 0.06) !important;
    }

    /* ══════════════════════════════════════════════════════════════
       METRIC DISPLAY
       ══════════════════════════════════════════════════════════════ */
    [data-testid="metric-container"] {
        font-family: var(--font-heading) !important;letter-spacing:0.03em;
        border-radius: 16px !important;
        padding: 16px !important;
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(148, 163, 184, 0.06) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s var(--ease-out-expo) !important;
    }

    [data-testid="metric-container"]:hover {
        border-color: rgba(148, 163, 184, 0.12) !important;
        transform: translateY(-1px) !important;
    }

    /* ══════════════════════════════════════════════════════════════
       BADGES - Pill style
       ══════════════════════════════════════════════════════════════ */
    .badge-easy { 
        background: rgba(16,185,129,0.12) !important; 
        color: #6EE7B7 !important; 
        border: 1px solid rgba(16,185,129,0.2) !important; 
    }
    .badge-medium { 
        background: rgba(245,158,11,0.12) !important; 
        color: #FCD34D !important; 
        border: 1px solid rgba(245,158,11,0.2) !important; 
    }
    .badge-hard { 
        background: rgba(239,68,68,0.12) !important; 
        color: #FCA5A5 !important; 
        border: 1px solid rgba(239,68,68,0.2) !important; 
    }
    .badge-low { 
        background: rgba(107,114,128,0.12) !important; 
        color: #94A3B8 !important; 
        border: 1px solid rgba(107,114,128,0.2) !important; 
    }
    .badge-high { 
        background: rgba(245,158,11,0.12) !important; 
        color: #FCD34D !important; 
        border: 1px solid rgba(245,158,11,0.2) !important; 
    }
    .badge-veryhigh { 
        background: rgba(239,68,68,0.12) !important; 
        color: #FCA5A5 !important; 
        border: 1px solid rgba(239,68,68,0.2) !important; 
    }

    /* ══════════════════════════════════════════════════════════════
       KEYFRAME ANIMATIONS
       ══════════════════════════════════════════════════════════════ */

     /* Card entrance - staggered fade up */
    @keyframes cardReveal {
        from {
            opacity: 0;
            transform: translateY(24px) scale(0.98);
            filter: blur(4px);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
            filter: blur(0);
        }
    }

    /* Gentle float */
    @keyframes gentleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }

    /* Pulse glow */
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.1); }
        50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.2); }
    }

    /* Gradient shift for title */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Shimmer effect */
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Cover glow rotation */
    @keyframes coverGlow {
        0% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(3deg) scale(1.02); }
        100% { transform: rotate(0deg) scale(1); }
    }

    /* Fade in up */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Scale in */
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    /* Slide in from left */
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Border glow pulse */
    @keyframes borderGlow {
        0%, 100% { border-color: rgba(99, 102, 241, 0.15); }
        50% { border-color: rgba(99, 102, 241, 0.3); }
    }

    /* Orb floating */
    @keyframes orbFloat1 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(30px, -20px) scale(1.05); }
        66% { transform: translate(-20px, 15px) scale(0.95); }
    }

    @keyframes orbFloat2 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(-25px, 20px) scale(1.03); }
        66% { transform: translate(15px, -25px) scale(0.97); }
    }

    </style>
    """,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  RENDER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def render_app_header():
    """Render the main app header with animated gradient text."""
    st.html(
        f"""
    <div style="text-align:center;padding:2rem 0 3rem 0;position:relative;">
        <!-- Floating orbs behind title -->
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:300px;height:100px;pointer-events:none;">
            <div style="position:absolute;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);top:-40px;left:20px;animation:orbFloat1 8s ease-in-out infinite;filter:blur(30px);"></div>
            <div style="position:absolute;width:100px;height:100px;border-radius:50%;background:radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%);top:-30px;right:30px;animation:orbFloat2 10s ease-in-out infinite;filter:blur(25px);"></div>
        </div>

        <div style="
            font-family: {FONT_HEADING};
            font-size: 3rem;
            font-weight: 800;
            letter-spacing: -0.05em;
            line-height: 1.05;
            background: linear-gradient(135deg, #818CF8 0%, #C084FC 25%, #F0ABFC 50%, #818CF8 75%, #C084FC 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: gradientShift 6s ease-in-out infinite;
            margin-bottom: 0.6rem;
            position: relative;
            z-index: 1;
        ">\u2728 TOPPERIFY AI</div>

        <div style="
            font-family: {FONT_BODY};
            font-size: 1.1rem;
            font-weight: 400;
            color: #64748B;
            letter-spacing: -0.01em;
            animation: fadeInUp 0.8s var(--ease-out-expo) both;
            animation-delay: 0.2s;
            position: relative;
            z-index: 1;
        ">Turn boring PDFs into beautiful topper-style notes</div>

        <!-- Decorative line -->
        <div style="
            width: 60px;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(99,102,241,0.5), transparent);
            margin: 1.5rem auto 0;
            animation: fadeInUp 0.8s var(--ease-out-expo) both;
            animation-delay: 0.4s;
            position: relative;
            z-index: 1;
        "></div>
    </div>
    """,
    )


def render_cover_page(cover_data: dict, chapter_title: str, subject: str):
    """Render the premium chapter cover page with animated mesh gradient."""
    tagline = cover_data.get("tagline", "")
    study_time = cover_data.get("study_time", "~30 min")
    difficulty = cover_data.get("difficulty", "Medium")
    importance = cover_data.get("exam_importance", "Medium")
    goals = cover_data.get("learning_goals", [])

    diff_class = {
        "Easy": "badge-easy",
        "Medium": "badge-medium",
        "Hard": "badge-hard",
    }.get(difficulty, "badge-medium")

    imp_class = {
        "Low": "badge-low",
        "Medium": "badge-medium",
        "High": "badge-high",
        "Very High": "badge-veryhigh",
    }.get(importance, "badge-medium")

    goals_html = ""
    if goals:
        goals_items = "".join(
            f'<li style="font-family:{FONT_BODY};font-size:0.88rem;color:#F1F5F9;line-height:1.9;padding:4px 0;animation:slideInLeft 0.5s var(--ease-out-expo) both;animation-delay:{0.6 + i * 0.08}s;">{g}</li>'
            for i, g in enumerate(goals)
        )
        goals_html = f"""
        <div style="text-align:left;max-width:520px;margin:1.8rem auto 0;position:relative;z-index:1;">
            <div style="
                font-family:{FONT_HEADING};
                font-size:0.7rem;
                font-weight:600;
                letter-spacing:0.1em;
                text-transform:uppercase;
                color:#94A3B8;
                margin-bottom:0.8rem;
                animation:fadeInUp 0.6s var(--ease-out-expo) both;
                animation-delay:0.5s;
            ">\U0001f3af Learning Goals</div>
            <ul style="margin:0;padding-left:20px;list-style:none;">
                {goals_items}
            </ul>
        </div>
        """

    st.html(
        f"""
    <div style="
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 30%, #0F172A 60%, #1E293B 100%);
        border-radius: 24px;
        padding: 3.5rem 3rem;
        margin-bottom: 2.5rem;
        text-align: center;
        border: 1px solid rgba(99,102,241,0.15);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s var(--ease-out-expo) both;
    ">
        <!-- Animated gradient orbs -->
        <div style="position:absolute;top:-100px;left:-100px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);animation:orbFloat1 12s ease-in-out infinite;filter:blur(40px);pointer-events:none;"></div>
        <div style="position:absolute;bottom:-80px;right:-80px;width:250px;height:250px;border-radius:50%;background:radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%);animation:orbFloat2 14s ease-in-out infinite;filter:blur(35px);pointer-events:none;"></div>
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:200px;height:200px;border-radius:50%;background:radial-gradient(circle, rgba(16,185,129,0.06) 0%, transparent 70%);animation:orbFloat1 16s ease-in-out infinite reverse;filter:blur(30px);pointer-events:none;"></div>

        <!-- Noise texture overlay -->
        <div style="position:absolute;inset:0;opacity:0.03;background-image:url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\");pointer-events:none;"></div>

        <div style="
            font-family:{FONT_HEADING};
            font-size:0.72rem;
            font-weight:600;
            color:#64748B;
            text-transform:uppercase;
            letter-spacing:0.15em;
            margin-bottom:1.2rem;
            position:relative;
            z-index:1;
            animation:fadeInUp 0.6s var(--ease-out-expo) both;
            animation-delay:0.1s;
        ">\U0001f4da Topperify AI \u2014 Chapter Notes</div>

        <div style="
            font-family:{FONT_HEADING};
            font-size:2.4rem;
            font-weight:800;
            letter-spacing:-0.04em;
            line-height:1.08;
            background:linear-gradient(135deg, #E0E7FF 0%, #C4B5FD 40%, #F0ABFC 70%, #E0E7FF 100%);
            background-size:200% 200%;
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
            background-clip:text;
            animation:gradientShift 8s ease-in-out infinite, fadeInUp 0.6s var(--ease-out-expo) both;
            animation-delay:0.2s, 0.2s;
            margin-bottom:0.8rem;
            position:relative;
            z-index:1;
        ">{chapter_title}</div>

        {"<div style='font-family:" + FONT_BODY + ";font-size:1.05rem;color:#94A3B8;font-style:italic;margin-bottom:1.8rem;position:relative;z-index:1;animation:fadeInUp 0.6s var(--ease-out-expo) both;animation-delay:0.3s;'>" + tagline + "</div>" if tagline else ""}

        <div style="position:relative;z-index:1;display:flex;gap:10px;justify-content:center;flex-wrap:wrap;animation:fadeInUp 0.6s var(--ease-out-expo) both;animation-delay:0.4s;">
            <span class="badge {diff_class}" style="font-family:{FONT_HEADING};font-weight:600;letter-spacing:0.04em;font-size:0.78rem;padding:6px 14px;border-radius:999px;display:inline-flex;align-items:center;gap:6px;">
                \U0001f4ca {difficulty}
            </span>
            <span class="badge {imp_class}" style="font-family:{FONT_HEADING};font-weight:600;letter-spacing:0.04em;font-size:0.78rem;padding:6px 14px;border-radius:999px;display:inline-flex;align-items:center;gap:6px;">
                \U0001f3af {importance} Importance
            </span>
            <span class="badge" style="font-family:{FONT_HEADING};font-weight:600;letter-spacing:0.04em;font-size:0.78rem;padding:6px 14px;border-radius:999px;background:rgba(99,102,241,0.1);color:#A5B4FC;border:1px solid rgba(99,102,241,0.2);display:inline-flex;align-items:center;gap:6px;">
                \u23f1 {study_time}
            </span>
        </div>
        {goals_html}
    </div>
    """,
    )


def _render_section_header(emoji: str, title: str):
    """Render a styled section header with gradient accent."""
    st.html(
        f"""
    <div style="
        font-family:{FONT_HEADING};
        font-size:1.4rem;
        font-weight:700;
        letter-spacing:-0.03em;
        line-height:1.2;
        color:#F1F5F9;
        margin:2.5rem 0 1.2rem 0;
        padding-bottom:0.6rem;
        border-bottom:1px solid rgba(148,163,184,0.06);
        display:flex;
        align-items:center;
        gap:10px;
        animation:fadeInUp 0.5s var(--ease-out-expo) both;
    ">
        <span style="
            display:inline-flex;
            align-items:center;
            justify-content:center;
            width:32px;
            height:32px;
            border-radius:10px;
            background:rgba(99,102,241,0.1);
            font-size:1rem;
        ">{emoji}</span>
        {title}
    </div>
    """,
    )


def _card_wrapper(color: str, delay: float = 0) -> tuple[str, str]:
    """Return opening and closing HTML for a premium glass card."""
    open_tag = f"""
    <div style="
        background:rgba(15,23,42,0.5);
        backdrop-filter:blur(16px);
        -webkit-backdrop-filter:blur(16px);
        border:1px solid rgba(148,163,184,0.06);
        border-left:3px solid {color};
        border-radius:16px;
        padding:22px 26px;
        margin-bottom:16px;
        position:relative;
        overflow:hidden;
        transition:all 0.4s var(--ease-out-expo);
        animation:cardReveal 0.6s var(--ease-out-expo) both;
        animation-delay:{delay}s;
    ">
        <!-- Subtle gradient glow on left -->
        <div style="position:absolute;top:0;left:0;width:80px;height:100%;background:linear-gradient(90deg, {color}11, transparent);pointer-events:none;"></div>
    """
    close_tag = "</div>"
    return open_tag, close_tag


def render_definition(term: str, meaning: str):
    """Render a blue definition card with glassmorphism."""
    open_tag, close_tag = _card_wrapper("#3B82F6")
    st.html(
        f"""
    {open_tag}
        <div style="
            font-family:{FONT_HEADING};
            font-size:0.65rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
            color:#60A5FA;
            margin-bottom:8px;
            display:flex;
            align-items:center;
            gap:6px;
        "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(59,130,246,0.15);font-size:0.6rem;">\U0001f4d8</span> Definition</div>
        <div style="
            font-family:{FONT_HEADING};
            font-size:1.08rem;
            font-weight:600;
            letter-spacing:-0.01em;
            color:#F8FAFC;
            margin-bottom:10px;
            line-height:1.3;
        ">{term}</div>
        <div style="
            font-family:{FONT_BODY};
            font-size:0.92rem;
            font-weight:400;
            line-height:1.75;
            color:rgba(203,213,225,0.9);
        ">{meaning}</div>
    {close_tag}
    """,
    )


def render_formula(name: str, formula: str, meaning: str):
    """Render a purple formula card with glassmorphism."""
    open_tag, close_tag = _card_wrapper("#8B5CF6")
    st.html(
        f"""
    {open_tag}
        <div style="
            font-family:{FONT_HEADING};
            font-size:0.65rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
            color:#A78BFA;
            margin-bottom:8px;
            display:flex;
            align-items:center;
            gap:6px;
        "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(139,92,246,0.15);font-size:0.6rem;">\u26a1</span> Formula</div>
        <div style="
            font-family:{FONT_HEADING};
            font-size:1.02rem;
            font-weight:600;
            letter-spacing:-0.01em;
            color:#F8FAFC;
            margin-bottom:12px;
        ">{name}</div>
        <div style="
            font-family:{FONT_MONO};
            font-size:1.35rem;
            font-weight:500;
            color:#C4B5FD;
            text-align:center;
            padding:16px 20px;
            letter-spacing:0.02em;
            background:rgba(139,92,246,0.06);
            border:1px solid rgba(139,92,246,0.12);
            border-radius:12px;
            margin-bottom:12px;
        ">{formula}</div>
        <div style="
            font-family:{FONT_BODY};
            font-size:0.88rem;
            font-weight:400;
            line-height:1.65;
            color:#94A3B8;
        ">{meaning}</div>
    {close_tag}
    """,
    )


def render_example(question: str, solution: str):
    """Render a green example card with glassmorphism."""
    open_tag, close_tag = _card_wrapper("#10B981")
    st.html(
        f"""
    {open_tag}
        <div style="
            font-family:{FONT_HEADING};
            font-size:0.65rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
            color:#34D399;
            margin-bottom:8px;
            display:flex;
            align-items:center;
            gap:6px;
        "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(16,185,129,0.15);font-size:0.6rem;">\u270f\ufe0f</span> Example</div>
        <div style="
            font-family:{FONT_HEADING};
            font-size:1.02rem;
            font-weight:600;
            letter-spacing:-0.01em;
            color:#6EE7B7;
            margin-bottom:10px;
            line-height:1.35;
        ">Q: {question}</div>
        <div style="
            font-family:{FONT_BODY};
            font-size:0.92rem;
            font-weight:400;
            line-height:1.75;
            color:rgba(203,213,225,0.9);
        "><span style="font-weight:600;color:#34D399;">A:</span> {solution}</div>
    {close_tag}
    """,
    )


def render_exam_tip(tip: str):
    """Render a yellow exam tip card with glassmorphism."""
    open_tag, close_tag = _card_wrapper("#F59E0B")
    st.html(
        f"""
    {open_tag}
        <div style="
            font-family:{FONT_HEADING};
            font-size:0.65rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
            color:#FBBF24;
            margin-bottom:8px;
            display:flex;
            align-items:center;
            gap:6px;
        "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(245,158,11,0.15);font-size:0.6rem;">\U0001f6a8</span> Exam Tip</div>
        <div style="
            font-family:{FONT_BODY};
            font-size:0.93rem;
            font-weight:500;
            line-height:1.7;
            color:#FDE68A;
        ">{tip}</div>
    {close_tag}
    """,
    )


def render_memory_trick(trick: str):
    """Render a lime memory trick card with glassmorphism."""
    open_tag, close_tag = _card_wrapper("#84CC16")
    st.html(
        f"""
    {open_tag}
        <div style="
            font-family:{FONT_HEADING};
            font-size:0.65rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
            color:#A3E635;
            margin-bottom:8px;
            display:flex;
            align-items:center;
            gap:6px;
        "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(132,204,22,0.15);font-size:0.6rem;">\U0001f9e0</span> Memory Trick</div>
        <div style="
            font-family:{FONT_BODY};
            font-size:0.93rem;
            font-weight:400;
            line-height:1.75;
            color:#D9F99D;
            font-style:italic;
        ">{trick}</div>
    {close_tag}
    """,
    )


def render_common_mistake(mistake: str):
    """Render a red common mistake card with glassmorphism."""
    open_tag, close_tag = _card_wrapper("#EF4444")
    st.html(
        f"""
    {open_tag}
        <div style="
            font-family:{FONT_HEADING};
            font-size:0.65rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
            color:#F87171;
            margin-bottom:8px;
            display:flex;
            align-items:center;
            gap:6px;
        "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(239,68,68,0.15);font-size:0.6rem;">\u26a0\ufe0f</span> Common Mistake</div>
        <div style="
            font-family:{FONT_BODY};
            font-size:0.93rem;
            font-weight:400;
            line-height:1.7;
            color:#FCA5A5;
        ">{mistake}</div>
    {close_tag}
    """,
    )


def render_key_concept(title: str, explanation: str):
    """Render a cyan key concept card with glassmorphism."""
    open_tag, close_tag = _card_wrapper("#06B6D4")
    st.html(
        f"""
    {open_tag}
        <div style="
            font-family:{FONT_HEADING};
            font-size:0.65rem;
            font-weight:600;
            letter-spacing:0.12em;
            text-transform:uppercase;
            color:#22D3EE;
            margin-bottom:8px;
            display:flex;
            align-items:center;
            gap:6px;
        "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(6,182,212,0.15);font-size:0.6rem;">\U0001f4a1</span> Key Concept</div>
        <div style="
            font-family:{FONT_HEADING};
            font-size:1.05rem;
            font-weight:600;
            letter-spacing:-0.01em;
            color:#F8FAFC;
            margin-bottom:10px;
            line-height:1.3;
        ">{title}</div>
        <div style="
            font-family:{FONT_BODY};
            font-size:0.92rem;
            font-weight:400;
            line-height:1.75;
            color:rgba(203,213,225,0.9);
        ">{explanation}</div>
    {close_tag}
    """,
    )


def render_flashcard_deck(flashcards: list[dict]):
    """Render interactive flashcards with glassmorphism and hover effects."""
    _render_section_header("\U0001f0cf", "Flashcards")

    if not flashcards:
        st.info("No flashcards generated for this content.")
        return

    cols_per_row = 2
    for i in range(0, len(flashcards), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(flashcards):
                break
            card = flashcards[idx]
            delay = 0.1 + (idx * 0.08)
            with col:
                st.html(
                    f"""
                <div style="
                    background:rgba(15,23,42,0.5);
                    backdrop-filter:blur(16px);
                    -webkit-backdrop-filter:blur(16px);
                    border:1px solid rgba(99,102,241,0.12);
                    border-radius:18px;
                    padding:1.8rem 1.5rem;
                    text-align:center;
                    min-height:120px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-family:{FONT_HEADING};
                    font-size:1.02rem;
                    font-weight:600;
                    color:#F1F5F9;
                    line-height:1.5;
                    position:relative;
                    overflow:hidden;
                    transition:all 0.4s var(--ease-out-expo);
                    animation:cardReveal 0.6s var(--ease-out-expo) both;
                    animation-delay:{delay}s;
                ">
                    <!-- Subtle gradient overlay -->
                    <div style="position:absolute;inset:0;background:linear-gradient(135deg, rgba(99,102,241,0.06) 0%, rgba(139,92,246,0.03) 100%);pointer-events:none;"></div>
                    <div style="position:relative;z-index:1;">{card.get("question", "")}</div>
                </div>
                """,
                )
                with st.expander("\U0001f50d Reveal Answer", expanded=False):
                    st.html(
                        f"""
                    <div style="
                        font-family:{FONT_BODY};
                        font-size:0.95rem;
                        line-height:1.7;
                        color:#F1F5F9;
                        padding:8px 0;
                    "><strong style="color:#A5B4FC;">{card.get("answer", "")}</strong></div>
                    """,
                    )


def render_mindmap(mindmap_data: dict):
    """Render an interactive mind map using streamlit-agraph."""
    _render_section_header("\U0001f5fa\ufe0f", "Mind Map")

    if not mindmap_data or not mindmap_data.get("children"):
        st.info("No mind map data available for this content.")
        return

    root = mindmap_data.get("root", "Topic")
    children = mindmap_data.get("children", {})

    nodes = []
    edges = []

    nodes.append(
        Node(
            id=root,
            label=root,
            size=35,
            color="#6366F1",
            font={"color": "#FFFFFF", "size": 16, "face": "Arial, sans-serif"},
            shape="dot",
        )
    )

    branch_colors = [
        "#3B82F6",
        "#8B5CF6",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#06B6D4",
        "#84CC16",
        "#EC4899",
    ]

    for i, (branch, leaves) in enumerate(children.items()):
        color = branch_colors[i % len(branch_colors)]

        nodes.append(
            Node(
                id=branch,
                label=branch,
                size=25,
                color=color,
                font={"color": "#FFFFFF", "size": 14, "face": "Arial, sans-serif"},
                shape="dot",
            )
        )
        edges.append(Edge(source=root, target=branch, color=color, width=2))

        if isinstance(leaves, list):
            for leaf in leaves:
                leaf_id = f"{branch}_{leaf}"
                nodes.append(
                    Node(
                        id=leaf_id,
                        label=str(leaf),
                        size=15,
                        color=color,
                        font={
                            "color": "#F1F5F9",
                            "size": 11,
                            "face": "Arial, sans-serif",
                        },
                        shape="dot",
                    )
                )
                edges.append(
                    Edge(
                        source=branch,
                        target=leaf_id,
                        color=color,
                        width=1,
                    )
                )

    config = Config(
        width=1000,
        height=500,
        directed=False,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F0ABFC",
        collapsible=False,
        node={"renderLabel": True},
        link={"renderLabel": False},
    )

    agraph(nodes=nodes, edges=edges, config=config)


def render_revision_sheet(revision_data: dict):
    """Render a compact revision sheet panel with glassmorphism."""
    _render_section_header("\U0001f4cb", "Quick Revision Sheet")

    definitions = revision_data.get("definitions", [])
    facts = revision_data.get("facts", [])
    formulas = revision_data.get("formulas", [])
    questions = revision_data.get("questions", [])

    def _render_revision_list(title: str, items: list, emoji: str, delay: float = 0):
        if not items:
            return
        st.html(
            f"""
        <div style="
            background:rgba(15,23,42,0.5);
            backdrop-filter:blur(16px);
            -webkit-backdrop-filter:blur(16px);
            border:1px solid rgba(99,102,241,0.08);
            border-radius:18px;
            padding:1.6rem 1.8rem;
            margin-bottom:1rem;
            position:relative;
            overflow:hidden;
            animation:cardReveal 0.6s var(--ease-out-expo) both;
            animation-delay:{delay}s;
        ">
            <div style="position:absolute;top:0;left:0;width:60px;height:100%;background:linear-gradient(90deg, rgba(99,102,241,0.06), transparent);pointer-events:none;"></div>
            <div style="
                font-family:{FONT_HEADING};
                font-size:0.65rem;
                font-weight:600;
                letter-spacing:0.12em;
                text-transform:uppercase;
                color:#818CF8;
                margin-bottom:0.8rem;
                display:flex;
                align-items:center;
                gap:6px;
            "><span style="display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:6px;background:rgba(99,102,241,0.12);font-size:0.6rem;">{
                emoji
            }</span> {title}</div>
            {
                "".join(
                    f'<div style="padding:0.65rem 0;border-bottom:1px solid rgba(148,163,184,0.04);font-family:{FONT_BODY};font-size:0.9rem;color:#F1F5F9;line-height:1.65;display:flex;align-items:flex-start;gap:8px;"><span style="color:#818CF8;font-weight:700;font-size:0.8rem;margin-top:2px;">\u25b8</span><span>{item}</span></div>'
                    for item in items
                )
            }
        </div>
        """,
        )

    col1, col2 = st.columns(2)
    with col1:
        _render_revision_list("Key Definitions", definitions, "\U0001f4d8", 0.1)
        _render_revision_list("Key Formulas", formulas, "\u26a1", 0.25)
    with col2:
        _render_revision_list("Important Facts", facts, "\U0001f4cc", 0.15)
        _render_revision_list("Important Questions", questions, "\u2753", 0.3)


def render_all_notes(data: dict):
    """Render the complete Notes tab with all card types."""

    definitions = data.get("definitions", [])
    if definitions:
        _render_section_header("\U0001f4d8", "Definitions")
        for i, d in enumerate(definitions):
            render_definition(d.get("term", ""), d.get("meaning", ""))

    concepts = data.get("key_concepts", [])
    if concepts:
        _render_section_header("\U0001f4a1", "Key Concepts")
        for c in concepts:
            render_key_concept(c.get("title", ""), c.get("explanation", ""))

    formulas = data.get("formulas", [])
    if formulas:
        _render_section_header("\u26a1", "Formulas")
        for f in formulas:
            render_formula(
                f.get("name", ""), f.get("formula", ""), f.get("meaning", "")
            )

    examples = data.get("examples", [])
    if examples:
        _render_section_header("\u270f\ufe0f", "Examples")
        for e in examples:
            render_example(e.get("question", ""), e.get("solution", ""))

    tips = data.get("exam_tips", [])
    if tips:
        _render_section_header("\U0001f6a8", "Exam Tips")
        for t in tips:
            if t:
                render_exam_tip(t)

    tricks = data.get("memory_tricks", [])
    if tricks:
        _render_section_header("\U0001f9e0", "Memory Tricks")
        for t in tricks:
            if t:
                render_memory_trick(t)

    mistakes = data.get("common_mistakes", [])
    if mistakes:
        _render_section_header("\u26a0\ufe0f", "Common Mistakes")
        for m in mistakes:
            if m:
                render_common_mistake(m)

    questions = data.get("important_questions", [])
    if questions:
        _render_section_header("\u2753", "Important Questions")
        for q in questions:
            if q:
                open_tag, close_tag = _card_wrapper("#06B6D4")
                st.html(
                    f"""
                {open_tag}
                    <div style="
                        font-family:{FONT_BODY};
                        font-size:0.92rem;
                        font-weight:400;
                        line-height:1.75;
                        color:rgba(203,213,225,0.9);
                    ">\u2753 {q}</div>
                {close_tag}
                """,
                )
