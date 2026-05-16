import streamlit as st
import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from question_generator import extract_text_from_file
from simulation_engine import interviewer_chat, candidate_chat

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Simulation",
    page_icon="🎙️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

    .stApp {
        background-color: #0c0c0c !important;
        color: #FFFFFF !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    [data-testid="stHeader"], [data-testid="stSidebar"], .main, .block-container {
        background-color: #0c0c0c !important;
    }

    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-bottom: 2rem;
    }

    .message-row {
        display: flex;
        margin-bottom: 32px;
        width: 100%;
        align-items: flex-start;
    }

    .interviewer-row {
        justify-content: flex-start;
    }

    .candidate-row {
        justify-content: flex-end;
    }

    /* Stick Figure & Floating Name Styling */
    .figure-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 80px;
        margin: 0 15px;
        position: sticky;
        top: 20px;
    }

    .stick-figure {
        font-size: 2.2rem;
        line-height: 1;
        margin-bottom: 5px;
    }

    .floating-name {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .interviewer-color { color: #FF00FF !important; }
    .candidate-color { color: #00FF00 !important; }

    /* Apple-style Liquid Bubbles (Invisible Outline) */
    .chat-bubble {
        padding: 8px 0;
        font-size: 1.05rem;
        line-height: 1.6;
        background: transparent !important;
        max-width: 75%;
        border: none !important;
    }

    .interviewer-bubble {
        color: #FF00FF !important;
        text-align: left;
    }

    .candidate-bubble {
        color: #00FF00 !important;
        text-align: right;
    }

    .stButton > button {
        background: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid #333 !important;
        border-radius: 20px !important;
    }

    .stButton > button:hover {
        border-color: #FF00FF !important;
        color: #FF00FF !important;
    }

    div[data-testid="stStatusWidget"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ─────────────────────────────────────────────────────────
def stream_response(role, response_gen):
    """Streams the response slowly to simulate human reading speed."""
    full_response = ""
    message_placeholder = st.empty()
    
    role_class = "interviewer-bubble" if role == "interviewer" else "candidate-bubble"
    row_class = "interviewer-row" if role == "interviewer" else "candidate-row"
    color_class = "interviewer-color" if role == "interviewer" else "candidate-color"
    
    name = "Alex" if role == "interviewer" else "Jordan"
    figure = "👨‍💼" if role == "interviewer" else "👩‍💼"

    for chunk in response_gen:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            for char in content:
                full_response += char
                
                if role == "interviewer":
                    content_html = f"""
                    <div class="message-row {row_class}">
                        <div class="figure-container">
                            <div class="stick-figure">{figure}</div>
                            <div class="floating-name {color_class}">{name}</div>
                        </div>
                        <div class="chat-bubble {role_class}">{full_response}</div>
                    </div>
                    """
                else:
                    content_html = f"""
                    <div class="message-row {row_class}">
                        <div class="chat-bubble {role_class}">{full_response}</div>
                        <div class="figure-container">
                            <div class="stick-figure">{figure}</div>
                            <div class="floating-name {color_class}">{name}</div>
                        </div>
                    </div>
                    """
                message_placeholder.markdown(content_html, unsafe_allow_html=True)
                time.sleep(0.02)
    
    st.session_state.messages.append({"role": role, "content": full_response})
    message_placeholder.empty()

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "turn" not in st.session_state:
    st.session_state.turn = "interviewer"
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">AI Interview Chat</h1>', unsafe_allow_html=True)

# ── API Key ───────────────────────────────────────────────────────────────────
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")

# ── Main Layout ───────────────────────────────────────────────────────────────
col_left, col_center, col_right = st.columns([1, 2, 1], gap="medium")

with col_left:
    st.markdown('<p class="sidebar-title">Interviewer (Alex)</p>', unsafe_allow_html=True)
    jd_file = st.file_uploader("Job Description", type=["pdf", "docx", "txt"], key="jd_upload")
    if jd_file:
        st.session_state.jd_text = extract_text_from_file(jd_file)

with col_right:
    st.markdown('<p class="sidebar-title">Candidate (Jordan)</p>', unsafe_allow_html=True)
    resume_file = st.file_uploader("Resume", type=["pdf", "docx", "txt"], key="resume_upload", disabled=not st.session_state.jd_text)
    if resume_file:
        st.session_state.resume_text = extract_text_from_file(resume_file)

# ── Conversation ──────────────────────────────────────────────────────────────
with col_center:
    # Initial Start
    if st.session_state.jd_text and st.session_state.resume_text and not st.session_state.interview_started:
        if st.button("🚀 Begin Conversation"):
            st.session_state.interview_started = True
            history = [{"role": "user", "content": "Start the interview. Welcome me, ask about my background briefly to start the conversation."}]
            resp = interviewer_chat(api_key, history, st.session_state.jd_text, st.session_state.resume_text, 0, stream=True)
            stream_response("interviewer", resp)
            st.session_state.turn = "candidate"
            st.rerun()

    # Display History
    for msg in st.session_state.messages:
        role = msg["role"]
        role_class = "interviewer-bubble" if role == "interviewer" else "candidate-bubble"
        row_class = "interviewer-row" if role == "interviewer" else "candidate-row"
        color_class = "interviewer-color" if role == "interviewer" else "candidate-color"
        
        name = "Alex" if role == "interviewer" else "Jordan"
        figure = "👨‍💼" if role == "interviewer" else "👩‍💼"
        
        if role == "interviewer":
            st.markdown(f"""
                <div class="message-row {row_class}">
                    <div class="figure-container">
                        <div class="stick-figure">{figure}</div>
                        <div class="floating-name {color_class}">{name}</div>
                    </div>
                    <div class="chat-bubble {role_class}">{msg['content']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="message-row {row_class}">
                    <div class="chat-bubble {role_class}">{msg['content']}</div>
                    <div class="figure-container">
                        <div class="stick-figure">{figure}</div>
                        <div class="floating-name {color_class}">{name}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Auto-play Simulation
    if st.session_state.interview_started:
        # Determine history for the LLM
        llm_history = []
        for m in st.session_state.messages:
            # Map roles correctly for the specific LLM being called
            if st.session_state.turn == "interviewer":
                role = "assistant" if m["role"] == "interviewer" else "user"
            else:
                role = "assistant" if m["role"] == "candidate" else "user"
            llm_history.append({"role": role, "content": m["content"]})

        if st.session_state.turn == "interviewer":
            time.sleep(1.5) # Slight pause for realism
            resp = interviewer_chat(api_key, llm_history, st.session_state.jd_text, st.session_state.resume_text, 1, stream=True)
            stream_response("interviewer", resp)
            st.session_state.turn = "candidate"
            st.rerun()
            
        elif st.session_state.turn == "candidate":
            # 10 second wait as requested
            placeholder = st.empty()
            for i in range(10, 0, -1):
                placeholder.markdown(f"<p style='text-align:right; color:#00FF00; font-size:0.8rem;'>Jordan is typing... {i}s</p>", unsafe_allow_html=True)
                time.sleep(1)
            placeholder.empty()
            
            resp = candidate_chat(api_key, llm_history, st.session_state.resume_text, st.session_state.jd_text, stream=True)
            stream_response("candidate", resp)
            st.session_state.turn = "interviewer"
            st.rerun()

    # Reset
    if st.session_state.interview_started and st.sidebar.button("Reset Interview"):
        st.session_state.messages = []
        st.session_state.interview_started = False
        st.session_state.turn = "interviewer"
        st.rerun()
