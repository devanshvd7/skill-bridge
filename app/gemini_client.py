"""LLM client for skill extraction with local fallback.

Uses Groq (via OpenAI-compatible SDK) for AI extraction,
with regex-based fallback when the API is unavailable.
"""

import json
import logging
import os
import re
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SkillWithLevel(BaseModel):
    name: str
    level: Literal["beginner", "intermediate", "advanced"]


class SkillExtraction(BaseModel):
    """Pydantic schema for constraining LLM structured output."""
    skills: list[SkillWithLevel]


def _get_groq_client() -> OpenAI:
    """Create an OpenAI-compatible client pointed at Groq."""
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )


def extract_skills_groq(text: str, master_list: list[str]) -> dict[str, str]:
    """Extract skills and proficiency from text using the Groq API."""
    client = _get_groq_client()

    prompt = (
        "Extract all professional skills mentioned in the following text document. "
        "For each skill, evaluate the proficiency level (beginner, intermediate, or advanced) "
        "that is either demonstrated (if it's a resume) or required (if it's a job description).\n\n"
        "CRITICAL CONSTRAINT: The skill 'name' must ONLY be one that EXACTLY matches "
        "a string in this list (case-sensitive):\n"
        f"{json.dumps(master_list)}\n\n"
        "Ignore any skills, technologies, or tools not in this list. "
        "Return an empty skills array if no matching skills are found.\n\n"
        "Respond with ONLY valid JSON matching this schema:\n"
        '{"skills": [{"name": "<exact skill name>", "level": "beginner|intermediate|advanced"}]}\n\n'
        f"---\n{text}\n---"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a precise skill extraction assistant. Only output valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    result = SkillExtraction.model_validate_json(raw)
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
    """Extract skills and proficiency from text: tries Groq first, falls back to local parsing."""
    logger.info(f"Starting skill extraction for {context}...")
    try:
        logger.info(f"Attempting AI extraction (Groq) for {context}...")
        skills = extract_skills_groq(text, master_list)
        logger.info(f"AI extraction successful. Found {len(skills)} skills in {context}.")
        return skills
    except Exception as e:
        logger.warning(f"AI extraction failed for {context}: {e}. Running local fallback...")
        skills = extract_skills_fallback(text, master_list)
        logger.info(f"Fallback extraction successful. Found {len(skills)} skills in {context}.")
        return skills
