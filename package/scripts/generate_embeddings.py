"""
Using FastRP generate node embeddings for the graph.
"""

import csv

from neo4j import GraphDatabase

NEO4J_URI = "neo4j://localhost:7687"
EMBEDDINGS_FILE = "embeddings.csv"

GRAPH_PROJECTION_CQL = """
MATCH (p)-[r]->(s)
RETURN gds.graph.project(
    "projection",
    p,
    s,
    {},
    { directedRelationshipTypes: ['*'] }
)
"""

MEMORY_CHECK_CQL = """
CALL gds.fastRP.stream.estimate('projection', {embeddingDimension: 128})
YIELD requiredMemory
"""

DELETE_PROJECTION_CQL = """
CALL gds.graph.drop("projection")
YIELD graphName
"""

FASTRP_CQL = """
CALL gds.fastRP.write(
    "projection",
    {{
      embeddingDimension: {dim},
      writeProperty: "fastrp_vector"
    }}
)
YIELD nodePropertiesWritten
"""

FETCH_EMBEDDING_CQL = """
MATCH (n)
RETURN n.id AS id, n.fastrp_vector AS fastrp_vector
"""


class EmbeddingGenerator:
    """Manage loading data into Neo4j."""

    def __init__(self, uri) -> None:
        self.driver = GraphDatabase.driver(uri)
        self.session = self.driver.session()

    def close(self) -> None:
        """End the session and close the driver."""
        self.session.close()

    def project_graph(self) -> None:
        """Project the graph into a GDS Cypher representation."""
        self.session.run(GRAPH_PROJECTION_CQL)

    def delete_projection(self) -> None:
        """Delete the projection."""
        self.session.run(DELETE_PROJECTION_CQL)

    def estimate_memory(self) -> None:
        """Estimate the memory required to generate embeddings."""
        result = self.session.run(MEMORY_CHECK_CQL)
        print(f"Estimated memory required: {result.single()['requiredMemory']}")  # type: ignore

    def fastrp(self, dim: int) -> None:
        """Generate embeddings and write as node data."""
        self.session.run(FASTRP_CQL.format(dim=dim))  # type: ignore

    def write_embeddings(self, path: str) -> None:
        """Write embeddings to a file."""
        result = self.session.run(FETCH_EMBEDDING_CQL)

        with open(path, mode="w", newline="", encoding="utf8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "fastrp_vector"])

            for record in result:
                writer.writerow([record["id"], record["fastrp_vector"]])


def main() -> None:
    """Project the graph and generate embeddings."""
    driver = EmbeddingGenerator(NEO4J_URI)
    driver.delete_projection()
    driver.project_graph()
    driver.estimate_memory()
    driver.fastrp(dim=128)
    driver.write_embeddings(EMBEDDINGS_FILE)
    driver.close()


if __name__ == "__main__":
    pass
