"""
Load the nodes and relationships from CSV files into Neo4j.
"""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j://localhost:7687"

LOAD_NODES_CQL = """
LOAD CSV WITH HEADERS FROM 'file:///{path}' AS row
WITH row LIMIT 100
CREATE (:Node {{
    id: row.id,
    name: row.name,
    category: row.category,
    all_names: split(row.all_names, 'ǂ'),
    all_categories: split(row.all_categories, 'ǂ'),
    iri: row.iri,
    description: row.description,
    equivalent_curies: split(row.equivalent_curies, 'ǂ'),
    publications: split(row.publications, 'ǂ'),
    label: row.label
}});
"""

UPDATE_LABELS_CQL = """
MATCH (n)
WHERE n.category IS NOT NULL
WITH n, labels(n) AS currentLabels, n.category AS newLabel
CALL apoc.create.setLabels(n, [newLabel]) YIELD node
RETURN count(node) AS updatedNodes;
"""

# WITH row LIMIT 100
LOAD_EDGES_CQL = """
LOAD CSV WITH HEADERS FROM 'file:///{path}' AS row
MATCH (a:Node {{id: row.subject}}), (b:Node {{id: row.object}})
MERGE (a)-[:RELATION {{
    id: row.id,
    predicate: row.predicate,
    relation: row.relation,
    publications: split(row.publications, 'ǂ'),
    label: row.label
}}]->(b);
"""


class DataLoader:
    """Manage loading data into Neo4j."""

    def __init__(self, uri) -> None:
        self.driver = GraphDatabase.driver(uri)
        self.session = self.driver.session()

    def close(self) -> None:
        """End the session and close the driver."""
        self.session.close()

    def clear(self) -> None:
        """Clear the database."""
        self.session.run("MATCH (n) DETACH DELETE n")  # type: ignore

    def status(self) -> None:
        """Count the number of nodes and relationships."""
        result = self.session.run("MATCH (n) RETURN count(n)")  # type: ignore
        print(f"Nodes: {result.single()[0]}")  # type: ignore
        result = self.session.run("MATCH ()-[r]->() RETURN count(r)")  # type: ignore
        print(f"Relationships: {result.single()[0]}")  # type: ignore

    def load_nodes(self, path: str) -> None:
        """Load nodes from a CSV file."""
        self.session.run(LOAD_NODES_CQL.format(path=path))  # type: ignore
        self.session.run(UPDATE_LABELS_CQL)  # type: ignore

    def load_edges(self, path: str) -> None:
        """Load edges from a CSV file."""
        self.session.run(LOAD_EDGES_CQL.format(path=path))  # type: ignore


def main() -> None:
    """Clear the database, load the data and show the status."""
    loader = DataLoader(NEO4J_URI)
    loader.clear()
    loader.load_nodes("Nodes.csv")
    loader.load_edges("Edges.csv")
    loader.status()
    loader.close()


if __name__ == "__main__":
    pass
