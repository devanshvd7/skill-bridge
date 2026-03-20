# Backend System Design Document

## 1. System Overview
The **Skill-Bridge Career Navigator** backend is a single-endpoint Proof of Concept (PoC) built in **Python 3.11+ using FastAPI**. Its primary responsibility is to accept two unstructured documents (a user's Resume and a Job Description), extract professional skills along with their proficiency levels, compute the gap between the two, and generate a logically ordered learning roadmap mapped to an internal database of courses.

## 2. Core Architecture
The backend is highly modularised, separating responsibilities across several core modules:
* `app/main.py`: The FastAPI application entry point, routing, HTTP request handling, and lifecycle orchestration.
* `app/parsers.py`: Utility functions for extracting raw text from PDFs and DOCX files.
* `app/gemini_client.py`: The LLM inference client (currently configured to use Llama-3.3-70b via Groq's OpenAI-compatible SDK) responsible for intelligent entity extraction. It includes a robust regex-based fallback.
* `app/graph.py`: Manages the Curriculum Directed Acyclic Graph (DAG) using the `NetworkX` library.
* `app/roadmap.py`: Performs pure mathematical gap analysis and utilizes topological sorting algorithms to generate tiered course recommendations.

## 3. Workflow & Logic Data Flow
The core logic triggered by the `/analyze-gap` POST endpoint follows a strict, sequential 5-phase pipeline:

### Phase 1: Ingestion & Parsing
The backend receives file uploads via multi-part form data. It routes the binary streams to `app/parsers.py` (which uses `PyMuPDF` or `python-docx`) to extract clean, raw UTF-8 text from the unstructured inputs.

### Phase 2: Skill & Proficiency Extraction (AI layer)
The raw text is sent to the LLM (Groq API). Crucially, the prompt is constrained by the `SkillExtraction` Pydantic model (`list[SkillWithLevel]`) and a hardcoded "Master List" of supported skills. 
The LLM acts as an intelligent classifier, identifying skills and evaluating their context to assign a structured proficiency: `{"beginner", "intermediate", "advanced"}`.
*If the LLM API fails, the backend seamlessly degrades to a local regex parser that guarantees a response, albeit defaulting the proficiency string to "beginner".*

### Phase 3: Gap Computation (Set Theory)
The gap computation is deliberately isolated from the LLM to prevent hallucinations and enforce deterministic logic. 
The backend maps categorical levels to integer weights (`beginner=1, intermediate=2, advanced=3`). A skill is logged as a "Gap" if:
1. The user lacks the skill entirely (`weight = 0`).
2. The user possesses the skill, but their proficiency weight is strictly lower than the required weight from the Job Description.

### Phase 4: Subgraph Extraction & Course Tiering (Graph Theory)
The application loads a global Curriculum DAG. 
1. **Transitive Dependency Resolution:** For every identified gap, the engine uses `nx.ancestors()` to crawl backwards up the DAG, fetching all foundational prerequisites the user might be missing.
2. **Subgraph Isolation:** It constructs a highly optimized `subgraph` containing *only* the skills the user needs to learn, detaching unused branches of the curriculum entirely.
3. **Topological Tiering:** It runs Kahn's Algorithm for Topological Generation (`nx.topological_generations()`) over the subgraph. Because it is acyclic, it cleanly slices the missing skills into sequential "phases" (Tiers), mathematically guaranteeing no advanced topic is scheduled before its foundational prerequisite.
4. **Course Mathematical Mapping:** Courses strictly map to the matrix. A course is only assigned into a phase if `user_weight < course_weight <= target_weight`.

### Phase 5: Synthesis
The resulting logically sequenced JSON roadmap is fed *back* into the LLM, which uses a secondary prompt to generate a 3-4 sentence encouraging synthesis summarizing the user's upcoming journey, highlighting phases that can be learned in parallel to save time.

## 4. Design Tradeoffs
* **In-Memory Graph State:** The curriculum graph is loaded into application memory globally at startup (`app.state`) rather than querying a graph database like Neo4j. This optimizes for extreme low-latency and simplicity within the 4-6 hr time limit.
* **Abstracted Proficiencies:** Levels are simplified to 3 tiers to match common corporate learning paths, avoiding 1-10 numbering scales which LLMs struggle to accurately assess from resume text.
