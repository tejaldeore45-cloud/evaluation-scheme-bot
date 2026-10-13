
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
import re
import pandas as pd

load_dotenv()

st.set_page_config(
    page_title="Evaluation Scheme Bot",
    page_icon="🎓",
    layout="wide"
)

# ---------- MODERN PROFESSIONAL THEME ----------
st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(135deg, #F4F7FC, #EAF1FA);
    color: #243247;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* Gradient hero header */
.hero {
    background: linear-gradient(120deg, #102A43, #1D4E89, #2563A6);
    padding: 32px;
    border-radius: 20px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 8px 25px rgba(16, 42, 67, 0.18);
    animation: fadeIn 0.7s ease-out;
}

.hero h1 {
    color: white;
    font-size: 2.3rem;
    font-weight: 750;
    margin-bottom: 8px;
}

.hero p {
    color: #E1EDFA;
    font-size: 1rem;
}

/* Cards */
.card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid #DFE8F2;
    padding: 22px;
    border-radius: 18px;
    margin-bottom: 16px;
    box-shadow: 0 4px 14px rgba(30, 58, 90, 0.05);
    transition: transform 0.25s ease,
                box-shadow 0.25s ease;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(30, 58, 90, 0.12);
}

.card h3 {
    color: #153B63;
    margin-top: 0;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius: 11px;
    border: 1px solid #C9D9EC;
    color: #174777;
    background: white;
    font-weight: 600;
    min-height: 42px;
    transition: all 0.2s ease-in-out;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #E8F1FC;
    border-color: #3478B8;
    color: #102A43;
    transform: translateY(-2px);
    box-shadow: 0 5px 12px rgba(37, 99, 166, 0.12);
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid #E1E8F0;
    border-radius: 15px;
    padding: 14px;
    margin-bottom: 10px;
    animation: fadeIn 0.35s ease-out;
}

/* Chat input */
div[data-testid="stChatInput"] {
    border-radius: 14px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #E7EEF7;
    border-right: 1px solid #D5E1EF;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #DFE8F2;
    border-radius: 15px;
    padding: 16px;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.75);
    border: 1px dashed #A9C4E3;
    border-radius: 14px;
    padding: 12px;
}

/* Section headings */
h2, h3 {
    color: #153B63;
}

/* Smooth entrance animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Responsive layout */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    .hero {
        padding: 22px;
    }

    .hero h1 {
        font-size: 1.7rem;
    }

    .card {
        padding: 16px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <h1>🎓 Evaluation Scheme Bot</h1>
    <p>Your Smart Academic Assistant</p>
    <p>
        Understand marks, exams, grading and evaluation schemes
        easily with the help of AI.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------- GEMINI CONFIGURATION ----------
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("API key not found. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are an Evaluation Scheme Bot for college students.

Explain evaluation schemes, marks distribution, exam patterns,
grading, internal and external evaluation, practicals and projects.

Use simple English or Marathi as requested.
Never invent official marks or rules.
Use the uploaded PDF when available.
If information is missing from the PDF, clearly say so.
"""

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🎓 Evaluation Bot")
    st.caption("Your Academic Assistant")
    st.divider()

    st.markdown("### 🧭 Navigation")
    st.markdown("🏠 Dashboard")
    st.markdown("📄 PDF Analyzer")
    st.markdown("💬 AI Chat")
    st.markdown("📊 Marks Analysis")
    st.markdown("📥 Download Report")

    st.divider()

    st.markdown("### ✨ Features")
    st.markdown(
        "- PDF text extraction\n"
        "- Evaluation scheme explanation\n"
        "- Marks and grading questions\n"
        "- English and Marathi support"
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("⚡ Powered by Gemini AI")

# ---------- MAIN LAYOUT ----------
left, right = st.columns([1, 1], gap="large")

# ---------- LEFT PANEL ----------
with left:
    st.markdown("""
    <div class="card">
        <h3>📄 Upload Evaluation Scheme</h3>
        <p>Upload your official college PDF to get started.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose your evaluation scheme PDF",
        type=["pdf"],
        key="scheme_pdf"
    )

    if uploaded_file is not None:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"

        if st.session_state.pdf_name != file_id:
            try:
                reader = PdfReader(uploaded_file)
                extracted = ""

                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        extracted += page_text + "\n"

                st.session_state.pdf_text = extracted
                st.session_state.pdf_name = file_id

            except Exception:
                st.error("Unable to read the PDF. Please try another file.")

    pdf_text = st.session_state.pdf_text
    
# ---------- MARKS DISTRIBUTION ANALYSIS ----------
st.divider()
st.subheader("📊 Marks Distribution Analysis")

if pdf_text.strip():
    marks_lines = []

    for line in pdf_text.splitlines():
        if re.search(
            r"\bmarks?\b|\bmaximum\s+score\b",
            line,
            re.IGNORECASE
        ):
            marks_lines.append(line.strip())

    if marks_lines:
        st.markdown("### 📋 Marks Information Found in PDF")

        for line in marks_lines:
            st.write("📌", line)

        st.info(
            "These lines were extracted from your PDF. "
            "Verify the values before using them in a chart."
        )
    else:
        st.warning(
            "No marks-related lines found in the PDF text."
        )
else:
    st.info("Please upload your evaluation scheme PDF first.")


    if uploaded_file is not None and pdf_text.strip():
        st.success(f"✅ PDF ready: {uploaded_file.name}")
        st.caption("Your document text has been extracted.")

        with st.expander("👀 Preview PDF Text"):
            st.text_area(
                "Extracted content",
                pdf_text,
                height=180,
                key="pdf_preview"
            )

    elif uploaded_file is not None:
        st.warning(
            "No readable text found. This PDF may contain scanned pages."
        )

    # Summary card
    st.markdown("""
    <div class="card">
        <h3>📊 Scheme Summary</h3>
        <p>Check your document status and extracted content.</p>
    </div>
    """, unsafe_allow_html=True)

    if pdf_text.strip():
        st.metric("Extracted Characters", f"{len(pdf_text):,}")
        st.metric("Document Status", "Ready ✅")
    else:
        st.info("Upload a readable PDF to enable document-based answers.")

    st.markdown("""
    <div class="card">
        <h3>📥 Download Summary</h3>
        <p>Download the extracted text from your evaluation scheme.</p>
    </div>
    """, unsafe_allow_html=True)

    if pdf_text.strip():
        st.download_button(
            "⬇️ Download Text Summary",
            data=pdf_text,
            file_name="evaluation_scheme_summary.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.caption("Upload a readable PDF to enable downloading.")

# ---------- RIGHT PANEL ----------
with right:
    st.markdown("""
    <div class="card">
        <h3>💬 AI Chat Assistant</h3>
        <p>Ask questions about marks, exams, practicals or grading.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ✨ Quick Questions")

    q1, q2 = st.columns(2)

    if q1.button("📊 Marks Distribution", use_container_width=True):
        st.session_state.pending_question = (
            "Explain the marks distribution using the uploaded PDF."
        )

    if q2.button("📝 Exam Pattern", use_container_width=True):
        st.session_state.pending_question = (
            "Explain the exam pattern using the uploaded PDF."
        )

    q3, q4 = st.columns(2)

    if q3.button("📚 Grading System", use_container_width=True):
        st.session_state.pending_question = (
            "Explain the grading system in simple English."
        )

    if q4.button("🌐 Explain in Marathi", use_container_width=True):
        st.session_state.pending_question = (
            "Explain the evaluation scheme in simple Marathi."
        )

    st.divider()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input(
        "Ask about your evaluation scheme..."
    )

    # Handle quick-question clicks
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = ""

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        conversation = SYSTEM_PROMPT + "\n\n"

        if pdf_text.strip():
            conversation += (
                "OFFICIAL PDF CONTENT:\n"
                + pdf_text
                + "\n\nUse this PDF as the source of truth. "
                "Do not guess missing marks or rules.\n\n"
            )
        else:
            conversation += (
                "No PDF has been uploaded. "
                "Do not invent college-specific evaluation rules.\n\n"
            )

        for msg in st.session_state.messages:
            conversation += (
                msg["role"].upper()
                + ": "
                + msg["content"]
                + "\n"
            )

        try:
            with st.chat_message("assistant"):
                with st.spinner("✨ Preparing your answer..."):
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=conversation
                    )

                    answer = response.text or "No answer received."
                    st.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        except Exception as e:
            st.error("Gemini API request failed. Please try again.")
            st.caption(str(e))

# ---------- FOOTER ----------
st.divider()

st.markdown("""
<div style="text-align:center; padding:12px; color:#62748A;">
    🎓 <b>Evaluation Scheme Bot</b><br>
    Your smart academic assistant · Powered by Gemini AI
</div>
""", unsafe_allow_html=True)
