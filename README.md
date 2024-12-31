# EveryCure tech assessment

## Overview

1. Set up project and dev environment (github, docker etc.)
2. Load data into a Neo4j graph
3. Generate embeddings for downstream ML
4. Build predictive model to predict disease-drug response

## python_template

General purpose template for installable python projects - [link](https://github.com/JBwdn/python_template)

### Installation

```bash
micromamba create -f environment.yml
micromamba activate template

pip install .  # Basic install
pip install -e ".[dev]"  # Install in editable mode with dev dependencies
pip install ".[test]"  # Install the package and all test dependencies

demo-script  # Run the included scripts from the shell
```

### Running pre-commit hooks

```bash
# Install the hooks:
pre-commit install

# Run all the hooks:
pre-commit run --all-files
```
