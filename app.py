"""
Frontend: Streamlit UI for Resume Interview Question Generator (Step 1)
"""

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Make sure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from question_generator import extract_text_from_file, generate_interview_questions

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Interview Question Generator",
    page_icon="🎯",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  .main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0f0f0f;
    line-height: 1.1;
    margin-bottom: 0.2rem;
  }

  .subtitle {
    font-size: 1.05rem;
    color: #6b7280;
    font-weight: 300;
    margin-bottom: 2.5rem;
  }

  .section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 0.5rem;
  }

  .question-card {
    background: #f9fafb;
    border-left: 3px solid #111827;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.85rem;
    font-size: 0.97rem;
    color: #1f2937;
    line-height: 1.6;
    animation: slideIn 0.4s ease forwards;
    opacity: 0;
  }

  .question-card:nth-child(1) { animation-delay: 0.05s; }
  .question-card:nth-child(2) { animation-delay: 0.15s; }
  .question-card:nth-child(3) { animation-delay: 0.25s; }
  .question-card:nth-child(4) { animation-delay: 0.35s; }
  .question-card:nth-child(5) { animation-delay: 0.45s; }

  @keyframes slideIn {
    from { opacity: 0; transform: translateX(-12px); }
    to   { opacity: 1; transform: translateX(0); }
  }

  .q-number {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    color: #9ca3af;
    letter-spacing: 0.05em;
    display: block;
    margin-bottom: 0.3rem;
  }

  .resume-preview {
    background: #f3f4f6;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    font-size: 0.82rem;
    color: #6b7280;
    max-height: 140px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.5;
    font-family: 'DM Mono', monospace;
    border: 1px solid #e5e7eb;
  }

  .stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    background: #111827 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 2rem !important;
    width: 100%;
    transition: background 0.2s;
  }

  .stButton > button:hover {
    background: #374151 !important;
  }

  .stFileUploader {
    border-radius: 10px;
  }

  .divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 2rem 0;
  }

  .badge {
    display: inline-block;
    background: #ecfdf5;
    color: #065f46;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.2rem 0.55rem;
    border-radius: 99px;
    margin-bottom: 1.2rem;
    letter-spacing: 0.03em;
  }

  .step-note {
    font-size: 0.8rem;
    color: #9ca3af;
    text-align: center;
    margin-top: 2.5rem;
    font-style: italic;
  }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">Interview Question<br>Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload a resume. Get 5 sharp, tailored questions instantly.</p>', unsafe_allow_html=True)
st.markdown('<span class="badge">✦ Step 1 of 2 — Resume Only</span>', unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
env_api_key = os.getenv("OPENAI_API_KEY")

if not env_api_key or env_api_key == "your_api_key_here":
    st.markdown('<p class="section-label">OpenRouter API Key</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        label="",
        type="password",
        placeholder="sk-or-v1-...",
        help="Your key is never stored. It's used only for this session.",
    )
else:
    api_key = env_api_key
    st.success("OpenRouter API Key loaded from environment.")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown('<p class="section-label">Candidate Resume</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="",
    type=["pdf", "docx", "txt"],
    help="Supported formats: PDF, DOCX, TXT",
)

resume_text = ""
if uploaded_file:
    with st.spinner("Reading resume..."):
        resume_text = extract_text_from_file(uploaded_file)

    if resume_text:
        st.markdown('<p class="section-label" style="margin-top:1rem;">Preview</p>', unsafe_allow_html=True)
        preview = resume_text[:600] + ("…" if len(resume_text) > 600 else "")
        st.markdown(f'<div class="resume-preview">{preview}</div>', unsafe_allow_html=True)
    else:
        st.warning("Could not extract text from this file. Please try a different format.")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Generate ──────────────────────────────────────────────────────────────────
generate_btn = st.button("✦ Generate Interview Questions", disabled=not (resume_text and api_key))

if generate_btn:
    if not api_key.startswith("sk-or-"):
        st.error("That doesn't look like a valid OpenRouter key (should start with `sk-or-`).")
    else:
        with st.spinner("Analysing resume and crafting questions…"):
            try:
                questions = generate_interview_questions(resume_text, api_key)

                st.markdown('<p class="section-label" style="margin-top:1rem;">5 Interview Questions</p>', unsafe_allow_html=True)

                cards_html = ""
                for i, q in enumerate(questions, 1):
                    cards_html += f"""
                    <div class="question-card">
                        <span class="q-number">Q{i}</span>
                        {q}
                    </div>
                    """
                st.markdown(cards_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="step-note">Step 2 coming soon — upload a Job Description to tailor questions further.</p>',
    unsafe_allow_html=True,
)
