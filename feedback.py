import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY is not set in the environment.")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def generate_feedback(resume_text, job_desc=None):
    if not resume_text:
        return "No resume text provided."

    messages = [
        {"role": "system", "content": "You are a helpful assistant that reviews resumes and gives suggestions to improve them."},
        {"role": "user", "content": f"Here is a resume:\n\n{resume_text.strip()}"},
    ]

    if job_desc:
        messages.append({"role": "user", "content": f"Here is the job description:\n\n{job_desc.strip()}"})

    messages.append({"role": "user", "content": "Give constructive feedback on how to improve the resume."})

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
        if response.status_code != 200:
            raise Exception(f"Groq API error {response.status_code}: {response.text}")

        result = response.json()
        return result['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"(Feedback unavailable: {str(e)})"
