# Skill-Bridge Career Navigator

AI-powered skill gap analysis and learning roadmap generator. Upload a resume and job description to get a personalized, DAG-sorted learning roadmap.

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Set your Gemini API key
#    Edit .env and replace 'your-api-key-here' with your real key

# 4. Generate sample PDFs
python data/generate_pdfs.py

# 5. Start the server
uvicorn app.main:app --reload
```

## Usage

```bash
curl -X POST http://localhost:8000/analyze-gap -F "resume=@data/sample_resume.pdf" -F "job_description=@data/sample_job.pdf"
```

## Running Tests

```bash
pytest -v
```

Tests mock all Gemini API calls — no API key required.

## Project Structure

```
skill-bridge/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app & endpoint
│   ├── graph.py           # NetworkX DAG management
│   ├── gemini_client.py   # Gemini extraction + fallback
│   └── roadmap.py         # Gap analysis, tiering, summary
├── data/
│   ├── curriculum.json    # 10-skill DAG + courses
│   └── generate_pdfs.py   # Sample PDF generator
├── tests/
│   └── test_main.py       # Happy path + fallback tests
├── AGENTS.md
├── .env / .env.example
├── pyproject.toml
└── requirements.txt
```

## License

MIT
