from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for Word docs
from feedback import generate_feedback
import logging
import markdown

# === Load environment variables ===
load_dotenv()
app = Flask(__name__)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

if not HF_API_TOKEN:
    raise EnvironmentError("HF_API_TOKEN is not set in the environment.")

logging.basicConfig(level=logging.ERROR)

# Limit the maximum content length to 2 MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB

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
        return round(result[0] * 100, 2)
    else:
        logging.error(f"Unexpected API response: {result}")
        raise ValueError("Unexpected API response format.")

# === Jinja Filter for Markdown Conversion ===
@app.template_filter('markdownify')
def markdownify(text):
    if text:
        return markdown.markdown(text)
    return ''

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    job_desc = request.form.get('job_description', '').strip()
    resume_text = request.form.get('resume_text', '').strip()
    feedback_text = ""

    # Try reading from uploaded file if no resume text is provided
    if not resume_text and 'resume_file' in request.files:
        file = request.files['resume_file']
        if file and file.filename:
            if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
                return "Error: Unsupported file type.", 400
            resume_text = extract_text_from_file(file)

    if not resume_text or not job_desc:
        return "Error: Resume and job description required.", 400

    try:
        score = get_similarity_score(job_desc, resume_text)
    except Exception as e:
        logging.error(f"Similarity calculation error: {str(e)}")
        return "An error occurred while processing your request. Please try again later.", 500

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
