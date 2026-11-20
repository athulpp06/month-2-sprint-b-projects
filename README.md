# AI Documentation Assistant

Minimal RAG-based AI Documentation Assistant. Upload PDFs, ask questions, and get answers grounded in the documents with sources and similarity scores.

## Setup

1. Create and activate a Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Configure your API key in `.env`:
```text
GROQ_API_KEY=your_groq_api_key_here
```

## Running the Application

1. Start the FastAPI backend:
```powershell
uvicorn app:app --reload
```

2. Start the Streamlit frontend:
```powershell
streamlit run frontend.py
```
