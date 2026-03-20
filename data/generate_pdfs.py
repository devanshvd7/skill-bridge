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
    # Candidate has: Java (intermediate), Git (intermediate),
    # Linux Basics (beginner), Spring Boot (beginner), Docker (beginner)
    # Missing entirely: Kubernetes, CI/CD Pipeline, AWS Cloud,
    # Microservices, System Design
    resume_text = """
    DEVANSH KUMAR
    Software Engineer | 3 Years Experience

    TECHNICAL SKILLS
    - Java: 3 years of backend development, built REST APIs and
      data processing pipelines. Comfortable with OOP, collections,
      and multithreading.
    - Spring Boot: Built two REST APIs using Spring Boot for
      internal tooling. Basic knowledge of Spring MVC and JPA.
    - Git: Daily use for version control. Experienced with branching,
      pull requests, rebasing, and resolving merge conflicts.
    - Linux Basics: Comfortable with the command line, file
      navigation, and basic shell scripting on Ubuntu.
    - Docker: Familiar with writing Dockerfiles and running
      containers locally for development.

    EXPERIENCE
    Software Engineer, Acme Corp (2022 - Present)
    - Developed Java-based backend services processing 10K+
      requests/day
    - Maintained Spring Boot REST APIs for the analytics dashboard
    - Used Docker for local development environments
    - Collaborated via Git using feature branch workflows

    Junior Developer, StartupXYZ (2021 - 2022)
    - Built internal tools using Java and Spring Boot
    - Wrote shell scripts for automating deployment tasks on Linux
    - Managed code repositories using Git

    EDUCATION
    B.Tech in Computer Science, IIIT Delhi, 2021
    """
    create_pdf(
        str(data_dir / "sample_resume.pdf"),
        "Resume - Devansh Kumar",
        resume_text,
    )

    # --- Sample Job Description ---
    # Requires: Kubernetes (advanced), CI/CD Pipeline (advanced),
    # Microservices (advanced), System Design (advanced),
    # AWS Cloud (intermediate), Docker (advanced),
    # Spring Boot (advanced), Java (advanced)
    jd_text = """
    JOB TITLE: Senior Cloud Platform Engineer
    COMPANY: TechScale Solutions
    LOCATION: Bangalore, India (Hybrid)
    EXPERIENCE: 5+ Years

    ABOUT THE ROLE
    We are looking for a Senior Cloud Platform Engineer to lead
    the design and operation of our cloud-native platform.
    You will architect scalable microservices, manage Kubernetes
    clusters, and build world-class CI/CD pipelines.

    REQUIRED SKILLS
    - Kubernetes: Expert-level container orchestration, Helm
      charts, service mesh, and cluster management
    - CI/CD Pipeline: Design and maintain production-grade
      pipelines using Jenkins, GitHub Actions, and ArgoCD
    - Microservices: Architect and deploy distributed
      microservices following domain-driven design principles
    - System Design: Lead architecture reviews for distributed
      systems, handle scalability and reliability
    - AWS Cloud: Deploy and manage services on AWS (EC2, ECS,
      Lambda, S3, RDS, CloudFormation)
    - Docker: Advanced containerization, multi-stage builds,
      image optimization, and container security
    - Spring Boot: Build production-grade Spring Boot services
      with security, monitoring, and observability
    - Java: Expert-level Java development with performance
      tuning and concurrency patterns

    NICE TO HAVE
    - Git: Advanced workflows (monorepo, trunk-based development)
    - Linux Basics: System administration and performance tuning

    RESPONSIBILITIES
    - Design and manage production Kubernetes clusters
    - Build and maintain CI/CD pipelines for 50+ microservices
    - Conduct System Design reviews and architecture decisions
    - Mentor junior engineers on cloud-native best practices
    """
    create_pdf(
        str(data_dir / "sample_job.pdf"),
        "Job Description - Senior Cloud Platform Engineer",
        jd_text,
    )


if __name__ == "__main__":
    main()
