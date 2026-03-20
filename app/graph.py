"""Curriculum graph management using NetworkX."""

import json
from pathlib import Path

import networkx as nx


def load_curriculum(path: str = "data/curriculum.json") -> dict:
    """Load the curriculum data from a JSON file."""
    with open(path) as f:
        return json.load(f)


def build_dag(curriculum: dict) -> nx.DiGraph:
    """Build a Directed Acyclic Graph from curriculum skills and dependencies.

    Edge direction: dependency -> skill (must learn the dependency first).
    """
    dag = nx.DiGraph()
    for skill in curriculum["skills"]:
        dag.add_node(skill["name"])
        for dep in skill["depends_on"]:
            dag.add_edge(dep, skill["name"])

    if not nx.is_directed_acyclic_graph(dag):
        raise ValueError("Curriculum contains circular dependencies!")

    return dag


def get_master_skill_list(dag: nx.DiGraph) -> list[str]:
    """Return the Golden Master List — all skill names in the graph, sorted."""
    return sorted(dag.nodes)
