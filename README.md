# ResumeFit

ResumeFit is a Python-based application designed to analyze resumes and provide constructive feedback to improve them. It uses AI-powered tools to compare resumes against job descriptions and generate suggestions for any improvement.

## Features

- **AI Feedback**: Provides constructive feedback to improve resumes.
- **Job Matching**: Compares resumes with job descriptions to assess compatibility.
- **User-Friendly**: Simple interface for uploading resumes and job descriptions.

## Technologies Used

- **Python**: Main programming language.
- **Hugging Face API**: Used for semantic analysis and feedback generation.
- **Groq API**: AI-powered resume review and suggestions.
- **dotenv**: For managing environment variables.

## How It Works

1. **Input**: Users upload or paste their resume and job description.
2. **Processing**: The application uses AI models to analyze the resume.
3. **Output**: Provides a match score and actionable feedback.

### Env File Structure
```bash
HF_API_TOKEN=<your_huggingface_api_token>
GROQ_API_KEY=<your_groq_api_key>
GROQ_MODEL=llama3-8b-8192
```



