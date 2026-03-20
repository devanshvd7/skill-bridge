Candidate Name: Devansh Vimlesh Desai
Video Link: https://screenrec.com/share/78ZtEHSGdn 
Scenario Chosen: Skill-Bridge Career Navigator  
Estimated Time Spent: 4-6 hours  
Quick Start: 
● Prerequisites: Python 3.11+, Groq API Key
● Run Commands: `python -m venv .venv` && `.\.venv\Scripts\activate` && `pip install -r requirements.txt` && `python data/generate_pdfs.py` && `uvicorn app.main:app --reload`
● Test Commands: `pytest -v`

AI Disclosure:  
● Did you use an AI assistant (Copilot, ChatGPT, etc.)? Yes
● How did you verify the suggestions? Automated test suites (pytest), manual API testing via Postman/cURL, and manual UI validation. Traced logical bugs (like LLM dictionary output causing JS errors) back to the source to manually verify fixes.
● Give one example of a suggestion you rejected or changed: Copilot initially suggested a basic flat-list subsetting algorithm for skill gap generation. I rejected this and implemented a Directed Acyclic Graph (DAG) with NetworkX to handle complex transitive prerequisite chains natively instead.

Tradeoffs & Prioritization:  
● What did you cut to stay within the 4–6 hour limit? Persistent database storage (PostgreSQL/MongoDB) and user authentication (OAuth). Reverted to stateful session data and local memory structures for speed.
● What would you build next if you had more time? Real-time live web scraping of job boards (LinkedIn, Indeed) rather than relying on PDF uploads, and expanding the single-graph Master List into domain-specific subgraphs.
● Known limitations: The system currently relies on a statically defined internal synthetic curriculum (`curriculum.json`). The Regex local fallback extraction cannot accurately gauge proficiency levels, defaulting everything to "beginner" if the API drops.
