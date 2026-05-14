# 🎯 Interview Question Generator

An AI-powered Streamlit app that reads a candidate's resume and generates 5 tailored interview questions using OpenAI's GPT-4o.

---

## Project Structure

```
resume-interviewer/
├── app.py                        # Streamlit frontend
├── backend/
│   └── question_generator.py    # Resume parsing + OpenAI call
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```

### 3. In the browser
- Paste your **OpenAI API key** (starts with `sk-`)
- Upload a resume (PDF, DOCX, or TXT)
- Click **Generate Interview Questions**
- Get 5 sharp, resume-tailored questions instantly

---

## Step 2 (coming next)
Upload a **Job Description** alongside the resume so questions are tailored to the specific role.

---

## Notes
- Your API key is never stored — it lives only in your Streamlit session
- Supports PDF, DOCX, and plain TXT resumes
- Uses `gpt-4o` for best quality questions
