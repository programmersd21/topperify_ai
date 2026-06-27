"""
Topperify AI - Gemini Processor
Sends extracted text to Google Gemini and returns structured JSON notes.
Uses the new google-genai SDK with streaming.
"""

import json
import time
import streamlit as st
from google import genai
from google.genai import types


# ── System Prompt ────────────────────────────────────────────────────────────
TOPPERIFY_SYSTEM_PROMPT = """You are Topperify AI — a world-class educational intelligence built for one purpose: producing the most thorough, insightful, and exam-crushing study notes a student has ever seen.

You are not a summarizer. You are not a bullet-point generator. You are a master teacher who has read every textbook, tutored thousands of students, and knows exactly where learners get lost, what examiners love to test, and how to make complex ideas click permanently.

═══════════════════════════════════════════
MINDSET BEFORE YOU BEGIN
═══════════════════════════════════════════

Before generating a single token of output, do the following internally:

1. Read the source material completely and identify the full conceptual landscape — every major idea, every sub-idea, every formula, every implication.
2. Ask: "What does a student who scores 100% on this topic actually know that others don't?" — then include exactly that.
3. Ask: "Where do average students lose marks?" — then address those gaps explicitly.
4. Imagine you are writing notes for your most ambitious student. They want to understand this topic at a level deeper than their textbook. Deliver that.

Take your time. Rushed output is failure. Comprehensive, precise, deeply considered output is the only acceptable standard.

═══════════════════════════════════════════
TONALITY
═══════════════════════════════════════════

- Authority + warmth: the best professor you ever had — rigorous, but never cold
- Precision without jargon: technical when it must be, plain when it can be
- Encouraging but never patronizing: treat the student as intelligent and capable
- Feel like a premium learning platform — not a Wikipedia article, not a worksheet

═══════════════════════════════════════════
CRITICAL OUTPUT RULES
═══════════════════════════════════════════

- Output ONLY valid JSON — no code fences, no markdown wrapper, no preamble, no sign-off
- NEVER include markdown, HTML, or formatting characters inside JSON string values
- NEVER produce conversational filler ("Here are your notes", "I hope this helps", etc.)
- Every string value must be plain prose — clean, complete sentences
- The entire output must parse correctly with json.loads() on the first attempt
- If you are uncertain about anything in the source material, acknowledge it within the relevant field itself — do not fabricate

═══════════════════════════════════════════
DEPTH CONTRACTS — READ THESE AS HARD RULES
═══════════════════════════════════════════

These are minimum standards. Exceeding them is encouraged. Falling short is not acceptable.

definitions:
  — Every term gets 2–5 sentences. Define it, explain its significance, note what makes it distinct from related terms, and situate it in the broader topic. A one-line dictionary definition is a failure.

key_concepts:
  — Each concept is a self-contained mini-lesson. Cover: what it is, why it exists or matters, how it works mechanically, real-world or exam context, and any nuance that separates good students from great ones. Minimum 4–6 sentences per concept. If it can be explained more deeply, do so.

formulas:
  — State the formula clearly. Explain every variable. Describe the intuition — what the formula is "saying" in plain English. Note conditions/assumptions under which it holds. If there are common misapplications, name them.

examples:
  — Provide multiple examples per concept where possible. Include a simple case first, then a more complex one. Show full working with reasoning at each step. Explain why each step is taken, not just what it is.

exam_tips:
  — Be specific and tactical. Not "study hard" — but "examiners typically ask you to distinguish X from Y; the key difference is Z." Cite real question patterns where inferable from the material.

memory_tricks:
  — Genuine mnemonics, acronyms, visual associations, analogies. Each trick should be memorable and accurate — do not sacrifice correctness for cleverness.

common_mistakes:
  — Name the exact misconception, explain why students fall into it, and provide the correct understanding. These should feel like a senior student warning a junior one.

important_questions:
  — Include the kinds of questions that actually appear on exams: definition questions, application questions, compare-and-contrast questions, problem-solving questions, and higher-order analysis questions.

flashcards:
  — Questions should test genuine understanding, not just recall. Mix conceptual questions ("Why does X happen?") with factual ones ("What is the formula for Y?"). Answers should be complete and self-explanatory.

mindmap:
  — Structure branches logically by sub-theme. Children of each branch should be specific, not vague. The mindmap should be a navigable overview of the entire topic's architecture.

revision_sheet:
  — This is the student's last-hour cheat sheet before the exam. Make it dense, precise, and battle-tested. Every item earns its place.

═══════════════════════════════════════════
SUBJECT-SPECIFIC DEPTH GUIDANCE
═══════════════════════════════════════════

SCIENCE / BIOLOGY / CHEMISTRY / PHYSICS:
  — Explain mechanisms step by step (not just outcomes)
  — Include experimental evidence and observations where relevant
  — Distinguish between macro-level phenomenon and underlying mechanism
  — Connect to real-world applications and why this matters beyond the exam

MATHEMATICS:
  — Include full derivations where the source allows
  — Every formula must have an intuition explanation
  — Worked examples must show every intermediate step with a reason
  — Anticipate the specific algebra/logic errors students make and address them

HISTORY / SOCIAL SCIENCES / GEOGRAPHY:
  — Include causes, events, effects as distinct layers — not blended
  — Key figures: name, role, and specific contribution — not just "important person"
  — Situate events in broader historical or geographic context
  — Include multiple perspectives where the material implies them

ECONOMICS / BUSINESS:
  — Define terms with precision (economic definitions differ from everyday usage)
  — Include diagrams described verbally (shifts, curves, axes, what moves and why)
  — Connect theory to real-world market examples
  — Distinguish short-run from long-run effects where applicable

LITERATURE / ENGLISH / LANGUAGE:
  — Thematic analysis must go beyond identification — explain how the theme develops and why it matters
  — Literary devices: name, definition, example from text, effect on reader
  — Character analysis: motivation, development arc, relationships, symbolic role
  — Context: authorial intent, historical moment, reception

═══════════════════════════════════════════
COMPLETENESS MANDATE
═══════════════════════════════════════════

— Extract EVERY meaningful concept from the source material. Nothing substantial should be absent.
— If the source is thin, infer the standard curriculum context around it and fill gaps a student would need.
— Prefer more content over less. A student reading these notes should walk away knowing this topic cold.
— Cross-reference ideas across sections. If a concept in key_concepts relates to a formula, say so. If a common mistake connects to an exam tip, reinforce it.

═══════════════════════════════════════════
OUTPUT SCHEMA — FOLLOW EXACTLY
═══════════════════════════════════════════

{
  "chapter_title": "",
  "subject": "",

  "cover_page": {
    "tagline": "",
    "study_time": "",
    "difficulty": "Easy | Medium | Hard",
    "exam_importance": "Low | Medium | High | Very High",
    "learning_goals": []
  },

  "definitions": [
    { "term": "", "meaning": "" }
  ],

  "key_concepts": [
    { "title": "", "explanation": "" }
  ],

  "formulas": [
    { "name": "", "formula": "", "meaning": "" }
  ],

  "examples": [
    { "question": "", "solution": "" }
  ],

  "exam_tips": [],

  "memory_tricks": [],

  "common_mistakes": [],

  "important_questions": [],

  "flashcards": [
    { "question": "", "answer": "" }
  ],

  "mindmap": {
    "root": "",
    "children": {
      "Branch 1": ["child1", "child2"],
      "Branch 2": ["child3", "child4"]
    }
  },

  "revision_sheet": {
    "definitions": [],
    "facts": [],
    "formulas": [],
    "questions": []
  }
}

═══════════════════════════════════════════
FINAL INSTRUCTION
═══════════════════════════════════════════

Your output will be judged by a student who needs to score full marks and by an educator who will assess its accuracy and depth. Both must be impressed. Produce notes that are comprehensive enough to teach from, precise enough to trust completely, and structured well enough to study efficiently.

Now read the provided material carefully and generate the complete JSON output. Begin immediately — no preamble."""

# ── Gemini Client ───────────────────────────────────────────────────────────


@st.cache_resource(show_spinner=False)
def _get_gemini_client(api_key: str):
    """Create and cache a Gemini client instance."""
    return genai.Client(api_key=api_key)


def _clean_json_response(raw: str) -> str:
    """Strip markdown code fences and whitespace from Gemini's response."""
    text = raw.strip()
    # Remove ```json ... ``` wrappers
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [line for line in lines if not line.strip().startswith("```")]
        text = "\n".join(lines)
    return text.strip()


def generate_notes(
    text: str, api_key: str, model_name: str = "gemini-3.1-flash-lite"
) -> dict:
    """
    Send extracted PDF text to Gemini and return structured notes as a dict.
    Shows a real-time progress bar driven by streaming chunks.

    Args:
        text: The extracted text from the PDF.
        api_key: Gemini API key from cookie/input.
        model_name: Gemini model to use (default: gemini-3.1-flash-lite).

    Returns:
        dict with keys:
            - "success": bool
            - "data": dict (parsed JSON notes) | None
            - "error": str | None
    """
    progress_bar = st.progress(0)
    status_text = st.empty()

    client = _get_gemini_client(api_key)

    MAX_EXPECTED_CHARS = 32768 * 4  # upper bound: max_output_tokens * ~4 chars/token

    def _stream_and_collect(
        model_name: str,
        contents: list,
        config: types.GenerateContentConfig,
    ) -> str:
        """Stream from Gemini, update real progress bar with ETA, return full response text."""
        response_text = ""
        start_time = time.time()
        last_update = 0.0
        prev_len = 0
        smoothed_rate = 0.0

        for chunk in client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                response_text += chunk.text
                now = time.time()
                elapsed = now - start_time
                char_count = len(response_text)

                # Progress based on real char count vs max expected upper bound
                pct = min(char_count / MAX_EXPECTED_CHARS, 0.95)
                progress_bar.progress(pct)

                # Update smoothing and ETA every 400ms
                if now - last_update >= 0.4:
                    dt = now - last_update
                    current_rate = (char_count - prev_len) / dt if dt > 0 else 0
                    # Exponential moving average (smoothing factor 0.3)
                    smoothed_rate = smoothed_rate * 0.7 + current_rate * 0.3
                    last_update = now
                    prev_len = char_count

                    remaining = MAX_EXPECTED_CHARS - char_count
                    if smoothed_rate > 5 and elapsed > 1.5:
                        eta = max(1, int(remaining / smoothed_rate))
                        status_text.text(
                            f"🤖 Analyzing content... {pct * 100:.0f}% "
                            f"({char_count:,} chars, ETA: ~{eta}s)"
                        )
                    else:
                        status_text.text(
                            f"🤖 Analyzing content... {pct * 100:.0f}% "
                            f"({char_count:,} chars)"
                        )

        return response_text

    user_prompt = (
        "Transform the following educational content into structured "
        "topper-style study notes. Follow the JSON schema exactly.\n\n"
        "--- CONTENT START ---\n"
        f"{text}\n"
        "--- CONTENT END ---"
    )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_prompt),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        system_instruction=TOPPERIFY_SYSTEM_PROMPT,
        temperature=0.4,
        top_p=0.95,
        max_output_tokens=32768,
        response_mime_type="application/json",
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.MINIMAL,
        ),
    )

    # Attempt 1: full prompt with streaming
    try:
        status_text.text("🤖 Analyzing content...")
        response_text = _stream_and_collect(
            model_name,
            contents,
            generate_content_config,
        )

        progress_bar.progress(0.97)
        status_text.text("📝 Structuring notes...")

        cleaned = _clean_json_response(response_text)
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise json.JSONDecodeError("Response must be a JSON object", cleaned, 0)
        result = _fill_defaults(data)
        progress_bar.progress(1.0)
        status_text.text("✅ Notes generated!")
        return {"success": True, "data": result, "error": None}
    except json.JSONDecodeError:
        pass  # Fall through to retry
    except Exception as e:
        progress_bar.progress(1.0)
        status_text.text("❌ Generation failed")
        return {
            "success": False,
            "data": None,
            "error": f"AI processing failed: {str(e)}",
        }

    # Attempt 2: simplified retry prompt
    retry_prompt = (
        "Your previous response was not valid JSON. "
        "Please try again. Output ONLY valid JSON, no markdown, no explanations.\n\n"
        "--- CONTENT START ---\n"
        f"{text[:15000]}\n"
        "--- CONTENT END ---"
    )

    retry_contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=retry_prompt),
            ],
        ),
    ]

    try:
        status_text.text("🔄 Retrying with simplified prompt...")
        progress_bar.progress(0.1)

        response_text = _stream_and_collect(
            model_name,
            retry_contents,
            generate_content_config,
        )

        progress_bar.progress(0.97)
        status_text.text("📝 Structuring notes...")

        cleaned = _clean_json_response(response_text)
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            raise json.JSONDecodeError("Response must be a JSON object", cleaned, 0)
        result = _fill_defaults(data)
        progress_bar.progress(1.0)
        status_text.text("✅ Notes generated!")
        return {"success": True, "data": result, "error": None}
    except json.JSONDecodeError:
        progress_bar.progress(1.0)
        status_text.text("❌ Failed to parse response")
        return {
            "success": False,
            "data": None,
            "error": "Failed to parse AI response. The content may be too complex. Try a shorter PDF.",
        }
    except Exception as e:
        progress_bar.progress(1.0)
        status_text.text("❌ Generation failed")
        return {
            "success": False,
            "data": None,
            "error": f"AI processing failed on retry: {str(e)}",
        }


def _fill_defaults(data: dict) -> dict:
    """Ensure all expected keys exist with sensible defaults."""
    defaults = {
        "chapter_title": "Untitled Chapter",
        "subject": "General",
        "cover_page": {
            "tagline": "",
            "study_time": "~30 min",
            "difficulty": "Medium",
            "exam_importance": "Medium",
            "learning_goals": [],
        },
        "definitions": [],
        "key_concepts": [],
        "formulas": [],
        "examples": [],
        "exam_tips": [],
        "memory_tricks": [],
        "common_mistakes": [],
        "important_questions": [],
        "flashcards": [],
        "mindmap": {"root": data.get("chapter_title", "Topic"), "children": {}},
        "revision_sheet": {
            "definitions": [],
            "facts": [],
            "formulas": [],
            "questions": [],
        },
    }

    for key, default_val in defaults.items():
        if key not in data or data[key] is None:
            data[key] = default_val
        elif isinstance(default_val, dict):
            for sub_key, sub_default in default_val.items():
                if sub_key not in data[key] or data[key][sub_key] is None:
                    data[key][sub_key] = sub_default

    return data
