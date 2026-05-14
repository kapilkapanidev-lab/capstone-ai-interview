"""
Backend module: Parses a resume and uses OpenAI to generate interview questions.
"""

import os
import io
import PyPDF2
import docx
from openai import OpenAI


def extract_text_from_file(uploaded_file) -> str:
    """
    Extracts plain text from a PDF or DOCX uploaded file.
    Returns the extracted text as a string.
    """
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    if filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join(para.text for para in doc.paragraphs)

    else:
        # Assume plain text
        text = file_bytes.decode("utf-8", errors="ignore")

    return text.strip()


def generate_interview_questions(resume_text: str, api_key: str) -> list[str]:
    """
    Calls the OpenRouter API with the resume as context.
    Returns a list of 5 tailored interview questions.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = (
        "You are an expert technical recruiter and interviewer. "
        "Your job is to read a candidate's resume carefully and craft exactly 5 "
        "insightful, role-specific interview questions. "
        "The questions should probe the candidate's real depth of experience, "
        "highlight potential gaps, and explore the most interesting parts of their background. "
        "Return ONLY a numbered list of 5 questions, one per line. No preamble, no explanation."
    )

    user_prompt = (
        f"Here is the candidate's resume:\n\n"
        f"{resume_text}\n\n"
        f"Generate the 5 best interview questions to ask this candidate."
    )

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()

    # Parse the numbered list into clean question strings
    questions = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading "1. " "2. " etc.
        if line[0].isdigit() and len(line) > 2 and line[1] in ".):":
            line = line[2:].strip()
        elif line[:2].isdigit() and len(line) > 3 and line[2] in ".):":
            line = line[3:].strip()
        if line:
            questions.append(line)

    return questions[:5]
