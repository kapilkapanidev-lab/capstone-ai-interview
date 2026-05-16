import os
from openai import OpenAI

def get_client(api_key: str):
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def interviewer_chat(api_key, history, job_description, resume_text, current_question_count, stream=False):
    """
    OpenAI (GPT-4o) as the Interviewer.
    """
    client = get_client(api_key)
    
    system_prompt = f"""
    You are an expert, empathetic, and positive interviewer named 'Alex' (Male).
    
    CONTEXT:
    Job Description: {job_description}
    Candidate Resume: {resume_text}
    
    OBJECTIVE:
    - You are currently in a deep-dive conversation for ONE question.
    - Provide immediate, encouraging feedback.
    - CRITICAL: Avoid infinite 'thank you' loops. If the candidate says thank you or goodbye, acknowledge it once and then END THE INTERVIEW with your final rating and summary.
    - If you are ready to conclude, explicitly state 'This concludes our interview' followed by the rating and summary.
    - Do not repeat pleasantries if they have already been exchanged.
    
    CURRENT PROGRESS:
    Questions asked so far: {current_question_count}.
    """

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "system", "content": system_prompt}] + history,
        temperature=0.7,
        stream=stream
    )
    return response

def candidate_chat(api_key, history, resume_text, job_description, stream=False):
    """
    Llama (via OpenRouter) as the Candidate.
    """
    client = get_client(api_key)
    
    system_prompt = f"""
    You are a candidate named 'Jordan' (Female) applying for a job.
    
    MY RESUME:
    {resume_text}
    
    TARGET JOB DESCRIPTION:
    {job_description}
    
    GOAL:
    - Respond naturally and CONCISELY to the interviewer.
    - CRITICAL: Your response MUST NOT exceed 2 paragraphs, and each paragraph must be maximum 4 lines.
    - Avoid infinite loops of pleasantries. If the interviewer says goodbye or thank you, acknowledge it simply and do not start a new cycle of thanks.
    - If the interviewer provides a final rating/summary, simply thank them and stop.
    """

    response = client.chat.completions.create(
        model="meta-llama/llama-3.1-70b-instruct",
        messages=[{"role": "system", "content": system_prompt}] + history,
        temperature=0.7,
        stream=stream
    )
    return response
