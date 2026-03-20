# Skill-Bridge Career Navigator — Agent Context

## Project Overview

Single-endpoint FastAPI PoC for an internal learning platform's AI-powered career skill gap analysis. Accepts a resume PDF + job description PDF, extracts skills (Gemini with fallback), computes the gap via set math, and returns a DAG-sorted tiered learning roadmap mapped to internal synthetic courses.

## Architecture

| Module               | Responsibility                                          |
|----------------------|---------------------------------------------------------|
| `app/main.py`        | FastAPI app, lifespan startup, `POST /analyze-gap`      |
| `app/graph.py`       | NetworkX DAG from `curriculum.json`, Golden Master List  |
| `app/gemini_client.py` | Gemini PDF extraction + PyMuPDF fallback               |
| `app/roadmap.py`     | Set-math gap analysis, topological tiering, summary gen  |

## Graph State

- **10 skill nodes** in a Directed Acyclic Graph
- Edges represent `depends_on` relationships (prerequisite → skill)
- **Root skills** (no deps): Java, Linux Basics, Git
- **Leaf skills** (no dependents): CI/CD Pipeline, Kubernetes, System Design

```
Java ──────────► Spring Boot ──┬──► Kubernetes
                               ├──► Microservices ──► System Design
Linux Basics ──► Docker ───────┤                       ▲
               ▲               └──► CI/CD Pipeline     │
               │                    ▲                   │
               └──► AWS Cloud ─────────────────────────┘
Git ────────────────────────────────┘
```

## API Endpoints

| Method | Path            | Description                                      |
|--------|-----------------|--------------------------------------------------|
| GET    | `/`             | Health check                                     |
| POST   | `/analyze-gap`  | Accepts resume + JD PDFs, returns tiered roadmap |

## Pending Tasks

- Add synthetic internal URLs to all courses in `curriculum.json` and render them as clickable links in the frontend.
