from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for Word docs
from feedback import generate_feedback
from markupsafe import Markup


# === Load environment variables ===
load_dotenv()
app = Flask(__name__)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL="https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


# === Text extraction from uploaded file ===
def extract_text_from_file(file):
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    elif filename.endswith('.docx'):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    elif filename.endswith('.txt'):
        return file.read().decode('utf-8')
    return ""


# === Use sentence-transformers API to compute similarity ===
def get_similarity_score(sentence1, sentence2):
    if not sentence1 or not sentence2:
        raise ValueError("Both sentences must be non-empty.")

    payload = {
        "inputs": {
            "source_sentence": sentence1,
            "sentences": [sentence2]
        }
    }

    response = requests.post(HF_API_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")

    result = response.json()
    if isinstance(result, list) and len(result) == 1:
        return round(result[0] * 100, 2)  # Convert to percentage
    else:
        raise ValueError("Unexpected API response format.")


# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.template_filter('nl2br')
def nl2br(s):
    if s:
        return Markup(s.replace('\n', '<br>\n'))
    else:
        return ''

@app.route('/analyze', methods=['POST'])
def analyze():
    job_desc = request.form.get('job_description', '').strip()
    resume_text = request.form.get('resume_text', '').strip()
    feedback_text = ""

    # Try reading from uploaded file if no resume text is provided
    if not resume_text and 'resume_file' in request.files:
        file = request.files['resume_file']
        if file and file.filename:
            resume_text = extract_text_from_file(file)

    if not resume_text or not job_desc:
        return "Error: Resume and job description required.", 400

    try:
        score = get_similarity_score(job_desc, resume_text)
    except Exception as e:
        return f"Error occurred while calculating similarity: {str(e)}", 500

    try:
        feedback_text = generate_feedback(resume_text, job_desc)
    except Exception as e:
        feedback_text = f"(Feedback unavailable: {str(e)})"

    return render_template('result.html',
                           match_score=score,
                           resume_preview=resume_text[:300],
                           job_preview=job_desc[:300],
                           feedback=feedback_text)


if __name__ == '__main__':
    app.run(debug=True)
