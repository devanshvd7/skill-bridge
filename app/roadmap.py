"""Roadmap generation: gap analysis, DAG tiering, and summary."""

import json
import os

from openai import OpenAI
import networkx as nx

LEVEL_WEIGHTS = {"beginner": 1, "intermediate": 2, "advanced": 3}

def compute_gap(user_skills: dict[str, str], required_skills: dict[str, str]) -> dict[str, str]:
    """Compute missing skills and their required tiers. No LLM involved.
    
    A gap exists if the user completely lacks the skill, or if their 
    current proficiency is lower than the required proficiency.
    """
    missing = {}
    for skill, req_level in required_skills.items():
        user_level = user_skills.get(skill)
        if not user_level:
            missing[skill] = req_level
        elif LEVEL_WEIGHTS.get(req_level, 1) > LEVEL_WEIGHTS.get(user_level, 1):
            missing[skill] = req_level
            
    return missing


def build_tiered_roadmap(
    dag: nx.DiGraph,
    missing_skills: dict[str, str],
    courses: list[dict],
    user_skills: dict[str, str] | None = None,
) -> dict:
    """Build a tiered learning roadmap from missing skills using topological sorting."""
    user_has = user_skills or {}
    all_needed = missing_skills.copy()

    # Pre-compute max available course level per skill for smart defaults
    max_course_level: dict[str, str] = {}
    for c in courses:
        skill_name = c["teaches"]
        c_level = c.get("level", "beginner")
        if skill_name not in max_course_level or \
           LEVEL_WEIGHTS.get(c_level, 1) > LEVEL_WEIGHTS.get(max_course_level[skill_name], 1):
            max_course_level[skill_name] = c_level

    # Add transitive prerequisites the user doesn't already have
    for skill, target_level in list(all_needed.items()):
        for ancestor in nx.ancestors(dag, skill):
            if ancestor not in user_has:
                if ancestor not in all_needed:
                    # Use max available course level so courses actually match
                    all_needed[ancestor] = max_course_level.get(ancestor, "beginner")

    if not all_needed:
        return {"tiers": []}

    # Build subgraph of only the skills we need to learn
    subgraph = dag.subgraph(all_needed.keys()).copy()

    tiers = []
    remaining = subgraph.copy()

    while remaining.number_of_nodes() > 0:
        zero_in = [n for n, d in remaining.in_degree() if d == 0]
        if not zero_in:
            break

        tier_courses = []
        for skill in sorted(zero_in):
            target_level_str = all_needed.get(skill, "beginner")
            target_level = LEVEL_WEIGHTS.get(target_level_str, 1)
            user_level_str = user_has.get(skill)
            user_level = LEVEL_WEIGHTS.get(user_level_str, 0) if user_level_str else 0
            
            # Use the max of target level and max available course level
            # This prevents "Self-study recommended" when fallback sets
            # target to "beginner" but only advanced courses exist
            max_avail = LEVEL_WEIGHTS.get(max_course_level.get(skill, "beginner"), 1)
            effective_target = max(target_level, max_avail)
            
            matching = [
                c for c in courses 
                if c["teaches"] == skill 
                and LEVEL_WEIGHTS.get(c.get("level", "beginner"), 1) > user_level
                and LEVEL_WEIGHTS.get(c.get("level", "beginner"), 1) <= effective_target
            ]
            
            # Sort courses by level to ensure logical progression Order
            matching.sort(key=lambda x: LEVEL_WEIGHTS.get(x.get("level", "beginner"), 1))
            tier_courses.extend(matching)

        tiers.append({
            "phase": len(tiers) + 1,
            "skills": sorted(zero_in),
            "courses": tier_courses,
        })

        remaining.remove_nodes_from(zero_in)

    return {"tiers": tiers}


def generate_summary_groq(roadmap: dict) -> str:
    """Ask Groq (Llama) to write an encouraging summary of the learning roadmap."""
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )

    prompt = (
        "You are an encouraging career coach. Based on this learning roadmap, "
        "write a short (3-4 sentences) motivational summary for the learner. "
        "Explicitly mention which courses can be learned in parallel to save time.\n\n"
        f"Roadmap:\n{json.dumps(roadmap, indent=2)}"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an encouraging career coach."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def generate_summary_fallback(roadmap: dict) -> str:
    """Generate a plain-text summary without calling any LLM."""
    tiers = roadmap.get("tiers", [])
    total_skills = sum(len(t["skills"]) for t in tiers)
    total_courses = sum(len(t["courses"]) for t in tiers)
    parallel_phases = [t for t in tiers if len(t["skills"]) > 1]

    lines = [
        f"Your personalized roadmap covers {total_skills} skill(s) "
        f"across {len(tiers)} phase(s), with {total_courses} recommended course(s)."
    ]

    if parallel_phases:
        for t in parallel_phases:
            skills_str = " and ".join(t["skills"])
            lines.append(
                f"In Phase {t['phase']}, you can learn {skills_str} in parallel "
                "to save time."
            )

    lines.append(
        "Follow the phases in order for the most efficient learning path. "
        "You've got this!"
    )
    return " ".join(lines)


def generate_summary(roadmap: dict) -> str:
    """Generate a roadmap summary: tries Groq first, falls back to plain text."""
    try:
        return generate_summary_groq(roadmap)
    except Exception:
        return generate_summary_fallback(roadmap)
