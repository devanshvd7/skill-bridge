"""Gemini API client for PDF skill extraction with local fallback."""

import json
import logging
import os
import re
from typing import Literal

from google import genai
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SkillWithLevel(BaseModel):
    name: str
    level: Literal["beginner", "intermediate", "advanced"]


class SkillExtraction(BaseModel):
    """Pydantic schema for constraining Gemini's structured output."""
    skills: list[SkillWithLevel]


def extract_skills_gemini(text: str, master_list: list[str]) -> dict[str, str]:
    """Extract skills and proficiency from text using the Gemini API."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = (
        "Extract all professional skills mentioned in the following text document. "
        "For each skill, evaluate the proficiency level (beginner, intermediate, or advanced) "
        "that is either demonstrated (if it's a resume) or required (if it's a job description).\n\n"
        "CRITICAL CONSTRAINT: The skill 'name' must ONLY be one that EXACTLY matches "
        "a string in this list (case-sensitive):\n"
        f"{json.dumps(master_list)}\n\n"
        "Ignore any skills, technologies, or tools not in this list. "
        "Return an empty list if no matching skills are found.\n\n"
        f"---\n{text}\n---"
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": SkillExtraction,
        },
    )

    result = SkillExtraction.model_validate_json(response.text)
    # Return dictionary mapping skill name to level, filtered to master list
    return {s.name: s.level for s in result.skills if s.name in master_list}


def extract_skills_fallback(text: str, master_list: list[str]) -> dict[str, str]:
    """Fallback: extract skills via regex, defaulting to 'beginner'."""
    found = {}
    for skill in master_list:
        pattern = re.compile(re.escape(skill), re.IGNORECASE)
        if pattern.search(text):
            found[skill] = "beginner"
    return found


def extract_skills(text: str, master_list: list[str], context: str = "document") -> dict[str, str]:
    """Extract skills and proficiency from text: tries Gemini first, falls back to local parsing."""
    logger.info(f"Starting skill extraction for {context}...")
    try:
        logger.info(f"Attempting AI extraction (Gemini) for {context}...")
        skills = extract_skills_gemini(text, master_list)
        logger.info(f"AI extraction successful. Found {len(skills)} skills in {context}.")
        return skills
    except Exception as e:
        logger.warning(f"AI extraction failed for {context}: {e}. Running local fallback...")
        skills = extract_skills_fallback(text, master_list)
        logger.info(f"Fallback extraction successful. Found {len(skills)} skills in {context}.")
        return skills
