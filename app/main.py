"""Skill-Bridge Career Navigator — FastAPI Application."""

import logging
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.gemini_client import extract_skills
from app.graph import build_dag, get_master_skill_list, load_curriculum
from app.parsers import extract_text_from_file
from app.roadmap import build_tiered_roadmap, compute_gap, generate_summary

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Setup directories for static files and templates based on the app path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Ensure directories exist (they will be created shortly)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load curriculum and build the skill DAG on startup."""
    curriculum = load_curriculum()
    dag = build_dag(curriculum)

    app.state.curriculum = curriculum
    app.state.dag = dag
    app.state.master_list = get_master_skill_list(dag)

    yield  # App runs here
    # Shutdown: nothing to clean up


app = FastAPI(
    title="Skill-Bridge Career Navigator",
    description=(
        "Upload a resume and job description to get a personalized, "
        "DAG-sorted learning roadmap that closes your skill gap."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root(request: Request):
    """Serve the frontend HTML template."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze-gap")
async def analyze_gap(
    resume: UploadFile = File(...),
    job_description: UploadFile | None = File(None),
    jd_text: str | None = Form(None),
):
    """Analyze the skill gap between a resume and a job description.

    Returns the extracted skills, missing skills, a tiered learning roadmap,
    and an AI-generated (or fallback) summary.
    """
    logger.info("Received request for /analyze-gap")
    
    if not job_description and not jd_text:
        raise HTTPException(status_code=400, detail="Must provide either job_description file or jd_text")

    # Read and parse Resume
    resume_bytes = await resume.read()
    resume_text = extract_text_from_file(resume_bytes, resume.filename)
    
    # Read and parse Job Description
    if jd_text:
        jd_final_text = jd_text
    else:
        jd_bytes = await job_description.read()
        jd_final_text = extract_text_from_file(jd_bytes, job_description.filename)

    master_list = app.state.master_list
    dag = app.state.dag
    courses = app.state.curriculum["courses"]

    # Phase 2: Extract skills from both documents
    logger.info("Phase 2: Extracting skills from documents...")
    user_skills = extract_skills(resume_text, master_list, context="Resume")
    required_skills = extract_skills(jd_final_text, master_list, context="Job Description")

    # Phase 3: Compute the gap (pure set math — no LLM)
    logger.info("Phase 3: Computing skill gap...")
    missing_skills = compute_gap(user_skills, required_skills)

    # Phase 4: Build tiered roadmap from the DAG
    logger.info("Phase 4: Building tiered learning roadmap...")
    roadmap = build_tiered_roadmap(dag, missing_skills, courses, user_skills)

    # Phase 5: Generate human-readable summary
    logger.info("Phase 5: Generating roadmap summary...")
    summary = generate_summary(roadmap)

    logger.info("Analysis complete! Returning response.")
    return {
        "user_skills": user_skills,
        "required_skills": required_skills,
        "missing_skills": missing_skills,
        "roadmap": roadmap,
        "summary": summary,
        "all_skills": list(dag.nodes),
        "graph_edges": list(dag.edges),
    }
