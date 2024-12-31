"""
Pull and run the latest version of the Neo4j podman image using podman.
"""

import os
import subprocess

PULL_CMD = "podman pull neo4j:latest"
RUN_CMD = f"""podman run \
--publish 7474:7474 \
--publish 7687:7687 \
--volume {os.getcwd()}:/var/lib/neo4j/import/ \
--env NEO4J_AUTH=none \
--env NEO4J_server_memory_heap_max__size=4G \
--env NEO4J_PLUGINS=["apoc","graph-data-science"] \
--memory 5g \
neo4j"""


def main() -> None:
    """
    Pull and run the Neo4j docker image.
    """
    subprocess.run(PULL_CMD.split(" "), check=True)
    subprocess.run(RUN_CMD.split(" "), check=True)


if __name__ == "__main__":
    pass
