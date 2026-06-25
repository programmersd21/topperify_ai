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

TOPPERIFY_SYSTEM_PROMPT = """You are Topperify AI - a world-class educational AI designed to help students truly understand and master their study material.

Your mission: transform the provided educational content into comprehensive, deeply researched, structured study notes that any student can learn from effectively. You are NOT just a summarizer - you are a complete learning companion.

TONALITY:
- Professional, authoritative, and accurate - like a top university professor
- Warm, encouraging, and student-friendly - like a supportive tutor
- Clear and accessible - no unnecessary jargon, but never dumbed down
- Feel like a premium learning hub where students can deeply understand every concept

CRITICAL OUTPUT RULES:
- Output ONLY valid JSON - no code fences, no markdown, no explanations, no conversational text
- NEVER include markdown, HTML, CSS, or any formatting in your JSON values
- NEVER say "Here are your notes" or "I hope this helps" or any conversational filler
- The JSON must parse correctly with json.loads()

OUTPUT SCHEMA (follow this exactly):
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

CONTENT PHILOSOPHY - READ THIS CAREFULLY:

DEPTH OVER BREVITY:
- Write COMPREHENSIVE, DETAILED content that provides true understanding
- Each definition should be a complete, self-contained explanation (2-4 sentences minimum)
- Each key concept should be a thorough mini-lesson covering what, why, how, and context
- Include examples, analogies, and real-world applications in explanations
- If a topic has nuance, explain it - don't gloss over it
- Students should be able to learn the material from your notes alone, without needing additional sources

COMPLETENESS:
- Extract EVERY meaningful concept from the source material
- Cover all major subtopics, not just the highlights
- Include background context, historical development, and practical significance where relevant
- Link related concepts together across sections
- Better to include too much detail than too little

STRUCTURE AND CLARITY:
- Organize content logically from foundational to advanced
- Use clear, precise language
- Define technical terms the first time they appear
- Each JSON field should be substantial - single words or one-liners are not acceptable

SUBJECT-SPECIFIC GUIDANCE:
- SCIENCE: Include mechanisms, processes, experimental evidence, scientific reasoning, practical applications
- MATHEMATICS: Include derivations, step-by-step worked examples, intuition behind formulas, common pitfalls with full explanations
- SOCIAL SCIENCES: Include context, causes and effects, key figures with their contributions, timeline understanding, historiographical perspectives
- LITERATURE/ENGLISH: Include thematic analysis, character development, literary device explanations with examples from the text, contextual background
- GENERAL: For any subject, connect theory to practice, include memory aids naturally, explain why concepts matter

EXAMPLES AND APPLICATION:
- Provide multiple, varied examples for each concept
- Include both simple and complex examples
- Show step-by-step reasoning for problem-solving
- Explain not just what the answer is, but WHY

Remember: Your notes are the primary learning resource. Make them thorough enough that a student can develop genuine mastery of the subject from your output alone. Be generous with detail, generous with examples, and generous with explanation."""


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


def generate_notes(text: str, api_key: str, model_name: str = "gemini-3.1-flash-lite") -> dict:
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
            model_name, contents, generate_content_config,
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
            model_name, retry_contents, generate_content_config,
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
