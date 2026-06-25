"""
Topperify AI - Main Application
Turn boring PDFs into beautiful topper-style notes.

Entry point for Streamlit Community Cloud.
"""

import streamlit as st

# Page Config (MUST be first Streamlit command)

st.set_page_config(
    page_title="Topperify AI - Topper-Style Notes",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Imports (after page config)

import time  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

from streamlit_cookies_controller import CookieController  # noqa: E402

from utils.pdf_parser import extract_text_from_pdf, chunk_text  # noqa: E402
from utils.gemini_processor import generate_notes  # noqa: E402
from utils.note_renderer import (  # noqa: E402
    inject_global_styles,
    render_app_header,
    render_cover_page,
    render_all_notes,
    render_flashcard_deck,
    render_mindmap,
    render_revision_sheet,
)
from utils.export_pdf import (  # noqa: E402
    generate_all_zip,
    generate_flashcards_pdf,
    generate_mindmap_png,
    generate_notes_pdf,
    generate_revision_pdf,
)


def section_heading(icon: str, title: str, subtitle: str = ""):
    """Render a consistent section heading with typography."""
    subtitle_html = (
        f"""
    <div style="
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.88rem;
        font-weight: 400;
        color: #64748B;
        margin-top: 4px;
        line-height: 1.5;
    ">{subtitle}</div>
    """
        if subtitle
        else ""
    )

    st.html(
        f"""
    <div style="margin: 28px 0 18px 0;">
        <div style="
            font-family: 'Instrument Serif', 'Georgia', serif;
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.2;
            color: #F1F5F9;
        ">{icon} {title}</div>
        {subtitle_html}
    </div>
    """,
    )


# Cookie Manager

COOKIE_NAME = "topperify_gemini_key"
MODEL_COOKIE = "topperify_model"

controller = CookieController(key="cookie_ctrl")

# Hide the cookie controller iframe
st.html("""
<style>
div[data-testid='element-container']:has(iframe[title='streamlit_cookies_controller.cookie_controller.cookie_controller']){
    display:none;
}
</style>
""")

# Load cookies from browser on every page load
cookies = controller.getAll()
time.sleep(1)  # Critical: wait for async cookie loading

# Initialize session state from cookies if not already set
if COOKIE_NAME in cookies and "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = cookies[COOKIE_NAME]

if MODEL_COOKIE in cookies and "selected_model" not in st.session_state:
    st.session_state["selected_model"] = cookies[MODEL_COOKIE]

MODEL_OPTIONS = {
    "gemini-3.1-flash-lite (Fastest)": "gemini-3.1-flash-lite",
    "gemma-4-26b-a4b-it (Deep Reasoning)": "gemma-4-26b-a4b-it",
    "gemma-4-31b-it (Most Powerful)": "gemma-4-31b-it",
}


def load_api_key() -> str:
    """Load API key from session state."""
    return st.session_state.get("gemini_api_key", "")


def save_api_key(key: str):
    """Save API key to session state + browser cookie (30-day expiry)."""
    st.session_state["gemini_api_key"] = key
    controller.set(COOKIE_NAME, key, max_age=30*24*60*60)


def delete_api_key():
    """Remove the stored API key from session state + cookie."""
    st.session_state["gemini_api_key"] = ""
    st.session_state["editing_key"] = False
    controller.remove(COOKIE_NAME)


def load_model_choice() -> str:
    """Load saved model from session state."""
    return st.session_state.get("selected_model", "gemini-3.1-flash-lite")


def save_model_choice(model_key: str):
    """Save model choice to cookie + session state."""
    st.session_state["selected_model"] = model_key
    controller.set(MODEL_COOKIE, model_key, max_age=30*24*60*60)


# API Key - Sidebar UI

saved_key = load_api_key()

with st.sidebar:
    st.html(
        """
    <div style="
        font-family: 'Instrument Serif', 'Georgia', serif;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F1F5F9;
        padding: 0.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    "><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:rgba(99,102,241,0.12);font-size:0.9rem;">🔑</span> Gemini API Key</div>
    """,
    )

    if saved_key:
        st.html(
            f"""
        <div style="
            background: rgba(16,185,129,0.08);
            border: 1px solid rgba(16,185,129,0.15);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            <span style="color:#34D399;font-size:0.9rem;">✓</span>
            <span style="font-family:'Instrument Serif','Georgia', serif;font-size:0.82rem;font-weight:600;color:#6EE7B7;">API key saved</span>
        </div>
        <div style="
            font-family:'Geist Mono',monospace;
            font-size:0.75rem;
            color:#64748B;
            margin-bottom:12px;
            padding:8px 12px;
            background:rgba(15,23,42,0.4);
            border-radius:8px;
            border:1px solid rgba(148,163,184,0.06);
        ">...{saved_key[-6:]}</div>
        """,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Change Key", use_container_width=True):
                st.session_state["editing_key"] = True
        with col2:
            if st.button("Remove Key", type="secondary", use_container_width=True):
                delete_api_key()
                st.session_state["editing_key"] = False
                st.rerun()

        if st.session_state.get("editing_key"):
            new_key = st.text_input(
                "Enter new Gemini API key",
                type="password",
                placeholder="AIza...",
            )
            if st.button("Save New Key", type="primary", use_container_width=True):
                if new_key.strip():
                    save_api_key(new_key.strip())
                    st.session_state["editing_key"] = False
                    st.rerun()
                else:
                    st.warning("Key cannot be empty.")

        GEMINI_API_KEY = saved_key

    else:
        st.html(
            """
        <div style="
            font-family:'Plus Jakarta Sans',sans-serif;
            font-size:0.85rem;
            color:#94A3B8;
            margin-bottom:12px;
            line-height:1.5;
        ">Enter your Gemini API key to get started.</div>
        """,
        )

        entered_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            help="Get your key at https://aistudio.google.com/",
        )

        remember = st.checkbox("Remember on this device", value=True)

        if st.button("Save & Continue", type="primary", use_container_width=True):
            if entered_key.strip():
                if remember:
                    save_api_key(entered_key.strip())
                    st.success("Key saved to your browser!")
                    st.rerun()
                else:
                    st.session_state["temp_api_key"] = entered_key.strip()
                    st.rerun()
            else:
                st.error("Please enter a valid API key.")

        GEMINI_API_KEY = st.session_state.get("temp_api_key", "")

    # Model Selection
    st.html(
        """
    <div style="
        font-family: 'Instrument Serif', 'Georgia', serif;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F1F5F9;
        padding: 1.5rem 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    "><span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:rgba(99,102,241,0.12);font-size:0.9rem;">\U0001f916</span> AI Model</div>
    """,
    )

    saved_model_key = load_model_choice()
    display_names = list(MODEL_OPTIONS.keys())
    saved_display = next(
        (k for k, v in MODEL_OPTIONS.items() if v == saved_model_key),
        display_names[0],
    )
    default_index = display_names.index(saved_display)

    model_display = st.selectbox(
        "Select AI Model",
        options=display_names,
        index=default_index,
        key="model_display",
    )
    selected_key = MODEL_OPTIONS[model_display]
    if selected_key != st.session_state.get("selected_model"):
        save_model_choice(selected_key)

# Global Styles

inject_global_styles()

# App Header

render_app_header()

# Stop if no key available yet

if not GEMINI_API_KEY:
    no_key_col1, no_key_col2, no_key_col3 = st.columns([1, 2, 1])
    with no_key_col2:
        st.html(
            """
        <div style="
            text-align: center;
            padding: 4rem 2.5rem;
            background: rgba(15, 23, 42, 0.5);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(99,102,241,0.1);
            border-radius: 24px;
            margin: 2rem 0;
            position: relative;
            overflow: hidden;
        ">
            <!-- Animated orbs -->
            <div style="position:absolute;top:-40px;right:-40px;width:150px;height:150px;border-radius:50%;background:radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);animation:orbFloat1 8s ease-in-out infinite;filter:blur(30px);pointer-events:none;"></div>
            <div style="position:absolute;bottom:-30px;left:-30px;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%);animation:orbFloat2 10s ease-in-out infinite;filter:blur(25px);pointer-events:none;"></div>

            <div style="font-size: 3.5rem; margin-bottom: 1.2rem;animation:gentleFloat 3s ease-in-out infinite;">\U0001f511</div>
            <div style="
                font-family: 'Instrument Serif', 'Georgia', serif;
                font-size: 1.3rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                color: #F1F5F9;
                margin-bottom: 0.6rem;
                position: relative;
                z-index: 1;
            ">Enter your Gemini API key in the sidebar</div>
            <div style="
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 0.92rem;
                color: #94A3B8;
                line-height: 1.6;
                position: relative;
                z-index: 1;
            ">Get a free key at <a href="https://aistudio.google.com/" target="_blank"
            style="color:#818CF8;text-decoration:none;font-weight:600;border-bottom:1px solid rgba(129,140,248,0.3);transition:all 0.3s ease;">Google AI Studio \u2197</a></div>
        </div>
        """,
        )
    st.stop()


# PDF Upload

st.markdown("---")

upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
with upload_col2:
    uploaded_file = st.file_uploader(
        "📄 Upload your PDF",
        type=["pdf"],
        help="Upload a textbook chapter, notes, or any educational PDF (max 50MB).",
        key="pdf_uploader",
    )

# Processing Pipeline

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()

    # Clear generated data on new file upload
    if st.session_state.get("_pdf_name") != uploaded_file.name:
        st.session_state["_pdf_name"] = uploaded_file.name
        st.session_state.pop("generated_data", None)

    # Step 1: Extract text
    with st.spinner("📖 Extracting text from PDF..."):
        extraction = extract_text_from_pdf(pdf_bytes)

    if not extraction["success"]:
        st.error(f"❌ {extraction['error']}")
        st.stop()

    # Success feedback
    st.success(
        f"✅ Extracted text from **{extraction['pages']} pages** "
        f"({len(extraction['text']):,} characters)"
    )

    # Step 2: Generate notes (manual button)
    if "generated_data" not in st.session_state:
        text = extraction["text"]
        chunks = chunk_text(text)
        primary_text = chunks[0]
        selected_model = st.session_state.get("selected_model", "gemini-3.1-flash-lite")

        col_btn, _, _ = st.columns([1.5, 1, 1.5])
        with col_btn:
            if st.button("🚀 Generate Notes", type="primary", use_container_width=True):
                result = generate_notes(primary_text, GEMINI_API_KEY, selected_model)
                if result["success"]:
                    st.session_state["generated_data"] = result["data"]
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
    else:
        col_regen, _, _ = st.columns([1, 3, 1])
        with col_regen:
            if st.button("🔄 Regenerate", use_container_width=True):
                del st.session_state["generated_data"]
                st.rerun()

# Step 3: Render Notes

if "generated_data" in st.session_state:
    data = st.session_state["generated_data"]

    # Cover page (outside tabs)
    render_cover_page(
        data.get("cover_page", {}),
        data.get("chapter_title", "Untitled"),
        data.get("subject", ""),
    )

    # Tabbed Interface
    tab_notes, tab_mindmap, tab_flashcards, tab_revision = st.tabs(
        [
            "📚 Notes",
            "🗺️ Mind Map",
            "🃏 Flashcards",
            "📋 Revision",
        ]
    )

    with tab_notes:
        render_all_notes(data)

    with tab_mindmap:
        render_mindmap(data.get("mindmap", {}))

    with tab_flashcards:
        render_flashcard_deck(data.get("flashcards", []))

    with tab_revision:
        render_revision_sheet(data.get("revision_sheet", {}))

    # ── Export Section ───────────────────────────────────────────────────
    st.markdown("---")

    chapter = data.get("chapter_title", "notes").replace(" ", "_")
    flashcards = data.get("flashcards", [])
    revision = data.get("revision_sheet", {})
    mindmap = data.get("mindmap", {})
    has_rev = any(revision.get(k) for k in ["definitions", "facts", "formulas", "questions"])

    try:
        # Prominent "Download All" button
        st.download_button(
            label="📦 Download All as ZIP",
            data=generate_all_zip(data),
            file_name=f"topperify_{chapter}_bundle.zip",
            mime="application/zip",
            use_container_width=True,
            type="primary",
        )

        # Individual downloads row
        dl_cols = st.columns(4)
        with dl_cols[0]:
            st.download_button(
                label="📄 Notes PDF",
                data=generate_notes_pdf(data),
                file_name=f"topperify_{chapter}_notes.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with dl_cols[1]:
            if flashcards:
                st.download_button(
                    label="🃏 Flashcards PDF",
                    data=generate_flashcards_pdf(flashcards, data.get("chapter_title", "Flashcards")),
                    file_name=f"topperify_{chapter}_flashcards.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.button("🃏 Flashcards", disabled=True, use_container_width=True)
        with dl_cols[2]:
            if has_rev:
                st.download_button(
                    label="📋 Revision PDF",
                    data=generate_revision_pdf(revision, data.get("chapter_title", "Revision")),
                    file_name=f"topperify_{chapter}_revision.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.button("📋 Revision", disabled=True, use_container_width=True)
        with dl_cols[3]:
            if mindmap and mindmap.get("children"):
                st.download_button(
                    label="🗺️ Mindmap PNG",
                    data=generate_mindmap_png(mindmap),
                    file_name=f"topperify_{chapter}_mindmap.png",
                    mime="image/png",
                    use_container_width=True,
                )
            else:
                st.button("🗺️ Mindmap", disabled=True, use_container_width=True)
    except Exception:
        st.warning("⚠️ Some exports failed. Your notes are still viewable above.")

elif uploaded_file is None:
    st.markdown("")
    empty_col1, empty_col2, empty_col3 = st.columns([1, 2, 1])
    with empty_col2:
        st.html(
            """
        <div style="
            text-align: center;
            padding: 4rem 2.5rem;
            background: rgba(15, 23, 42, 0.5);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(99,102,241,0.1);
            border-radius: 24px;
            margin: 2rem 0;
            position: relative;
            overflow: hidden;
        ">
            <!-- Animated orbs -->
            <div style="position:absolute;top:-60px;left:50%;transform:translateX(-50%);width:200px;height:200px;border-radius:50%;background:radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);animation:orbFloat1 10s ease-in-out infinite;filter:blur(40px);pointer-events:none;"></div>

            <div style="font-size: 4rem; margin-bottom: 1.2rem;animation:gentleFloat 4s ease-in-out infinite;">\U0001f4c4</div>
            <div style="
                font-family: 'Instrument Serif', 'Georgia', serif;
                font-size: 1.4rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                color: #F1F5F9;
                margin-bottom: 0.6rem;
                position: relative;
                z-index: 1;
            ">Upload a PDF to get started</div>
            <div style="
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: 0.95rem;
                color: #94A3B8;
                line-height: 1.6;
                position: relative;
                z-index: 1;
            ">Textbook chapters, class notes, study material - we'll turn it into premium study notes</div>
        </div>

        <!-- Feature cards -->
        <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:12px;margin-top:1.5rem;">
            <div style="
                background:rgba(15,23,42,0.5);
                backdrop-filter:blur(12px);
                border:1px solid rgba(59,130,246,0.1);
                border-radius:16px;
                padding:1.4rem 1rem;
                text-align:center;
                transition:all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                position:relative;
                overflow:hidden;
                animation:cardReveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
                animation-delay:0.1s;
            ">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg, transparent, rgba(59,130,246,0.3), transparent);"></div>
                <div style="font-size:1.8rem;margin-bottom:0.6rem;">\U0001f4da</div>
                <div style="font-family:'Instrument Serif','Georgia', serif;font-size:0.82rem;font-weight:600;color:#F1F5F9;letter-spacing:-0.01em;">Visual Notes</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.7rem;color:#64748B;margin-top:0.3rem;">Color-coded cards</div>
            </div>
            <div style="
                background:rgba(15,23,42,0.5);
                backdrop-filter:blur(12px);
                border:1px solid rgba(139,92,246,0.1);
                border-radius:16px;
                padding:1.4rem 1rem;
                text-align:center;
                transition:all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                position:relative;
                overflow:hidden;
                animation:cardReveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
                animation-delay:0.2s;
            ">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg, transparent, rgba(139,92,246,0.3), transparent);"></div>
                <div style="font-size:1.8rem;margin-bottom:0.6rem;">\U0001f5fa\ufe0f</div>
                <div style="font-family:'Instrument Serif','Georgia', serif;font-size:0.82rem;font-weight:600;color:#F1F5F9;letter-spacing:-0.01em;">Mind Maps</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.7rem;color:#64748B;margin-top:0.3rem;">Interactive graphs</div>
            </div>
            <div style="
                background:rgba(15,23,42,0.5);
                backdrop-filter:blur(12px);
                border:1px solid rgba(16,185,129,0.1);
                border-radius:16px;
                padding:1.4rem 1rem;
                text-align:center;
                transition:all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                position:relative;
                overflow:hidden;
                animation:cardReveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
                animation-delay:0.3s;
            ">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg, transparent, rgba(16,185,129,0.3), transparent);"></div>
                <div style="font-size:1.8rem;margin-bottom:0.6rem;">\U0001f0cf</div>
                <div style="font-family:'Instrument Serif','Georgia', serif;font-size:0.82rem;font-weight:600;color:#F1F5F9;letter-spacing:-0.01em;">Flashcards</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.7rem;color:#64748B;margin-top:0.3rem;">Tap to reveal</div>
            </div>
            <div style="
                background:rgba(15,23,42,0.5);
                backdrop-filter:blur(12px);
                border:1px solid rgba(245,158,11,0.1);
                border-radius:16px;
                padding:1.4rem 1rem;
                text-align:center;
                transition:all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                position:relative;
                overflow:hidden;
                animation:cardReveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
                animation-delay:0.4s;
            ">
                <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg, transparent, rgba(245,158,11,0.3), transparent);"></div>
                <div style="font-size:1.8rem;margin-bottom:0.6rem;">\U0001f4cb</div>
                <div style="font-family:'Instrument Serif','Georgia', serif;font-size:0.82rem;font-weight:600;color:#F1F5F9;letter-spacing:-0.01em;">PDF Export</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.7rem;color:#64748B;margin-top:0.3rem;">Print-ready notes</div>
            </div>
        </div>
        """,
        )
