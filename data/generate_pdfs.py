"""Generate sample PDFs for testing the Skill-Bridge Career Navigator."""

import fitz  # PyMuPDF
from pathlib import Path


def create_pdf(filepath: str, title: str, body: str) -> None:
    """Create a simple single-page PDF with the given text content."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), title, fontsize=18, fontname="helv")
    y = 120
    for line in body.strip().split("\n"):
        page.insert_text((72, y), line.strip(), fontsize=11, fontname="helv")
        y += 20
    doc.save(filepath)
    doc.close()
    print(f"Created: {filepath}")


def main():
    data_dir = Path(__file__).parent

    # --- Sample Resume ---
    resume_text = """
    DEVANSH KUMAR
    Senior Software Engineer

    SKILLS
    - Java (5 years of enterprise development)
    - Linux Basics (system administration and scripting)
    - Git (version control, branching strategies)

    EXPERIENCE
    - Built enterprise applications using Java and Spring framework
    - Managed Linux servers for development and staging environments
    - Collaborated using Git workflows (GitFlow, trunk-based development)

    EDUCATION
    - B.Tech in Computer Science, 2020
    """
    create_pdf(
        str(data_dir / "sample_resume.pdf"),
        "Resume - Devansh Kumar",
        resume_text,
    )

    # --- Sample Job Description ---
    jd_text = """
    JOB TITLE: Cloud Platform Engineer

    REQUIRED SKILLS
    - Kubernetes (container orchestration, Helm charts)
    - CI/CD Pipeline (Jenkins, GitHub Actions, ArgoCD)
    - Microservices (design, deployment, monitoring)
    - System Design (distributed systems, scalability)

    RESPONSIBILITIES
    - Design and manage Kubernetes clusters in production
    - Build and maintain CI/CD Pipeline for microservice deployments
    - Architect Microservices following domain-driven design
    - Contribute to System Design reviews and architecture decisions

    NICE TO HAVE
    - AWS Cloud certification
    - Docker experience
    """
    create_pdf(
        str(data_dir / "sample_job.pdf"),
        "Job Description - Cloud Platform Engineer",
        jd_text,
    )


if __name__ == "__main__":
    main()
