# python_template
General purpose template for installable python projects

## Todo

- [ ] Add github actions (testing, deployment, publishing)

## Installation

```bash
micromamba create -f environment.yml
micromamba activate template

pip install .  # Basic install
pip install -e ".[dev]"  # Install in editable mode with dev dependencies
pip install ".[test]"  # Install the package and all test dependencies

demo-script  # Run the included scripts from the shell
```

## Usage

### Importing and using code

```python
# Import the package and run some included function:

from package import scripts
scripts.demo.main()
```

### Running pre-commit hooks

```bash
# Install the hooks:
pre-commit install

# Run all the hooks:
pre-commit run --all-files
```

### Running tests

```bash
# Pytest will find all files with the name "test_*.py" or "*_test.py" and run them:

pytest
```
