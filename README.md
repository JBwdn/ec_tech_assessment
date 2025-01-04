# EveryCure tech assessment

## Overview/Plan

1. Set up project and dev environment (github, docker etc.)
2. Load data into a Neo4j graph
3. Generate embeddings for downstream ML
4. Build predictive model to predict disease-drug response

## Notes

1. I have used a previously made python template to structure the repo making it pip installable [link](https://github.com/JBwdn/python_template). This is pre-configured to use a few tools including: 
    - micromamba - manage the virtual python env
    - pre-commit - hooks for formatting and linting python 
2. I am using podman for managing the Neo4J docker container, which is called using `subprocess` from the `launch_n4j` script. The port mapping, mapped volume and container max memory are configured using CLI arguments and Neo4j plugins are configured by passing environment variables to the container.
    - This needs to be run from within the `data/` directory containing the provided data files.
3. The data loading script works well for the nodes but is very slow for the relationships (due to looking up the id for each `from_id` and `to_id` field). Previously I have used the Neo4j admin import command to load large lists of edges, but this requires some data preprocessing and is probably beyond the scope for now.
    - All provided fields are loaded into the graph, but I will probably only use the topology to generate embeddings as augmenting the graph with features from the cross-referenced databases will be take a while...
4. I have chosen to use FastRP for generating node embeddings from the graph. At least for the number of edges I have loaded this seems to run fast enough that calculating these for ALL node types is not a big deal. Then I will pull the required embeddings from the `embeddings.csv` output file using the ids in `Ground Truth.csv`.
    - FastRP is better for use with undirected relationships but it is what I am more familiar with from GDS so have used that here.
    - I have selected an embedding size of 128 based on the size of the graph and projected memory usage on my machine.
5. In my previous role XGBoost has performed well on tasks involving graph embeddings (though primarily this was regression problems). Here we will just use the default parameters, however a logical next stage would be to perform a hyperparameter sweep against the embeddings.
    - Using the ground truth dataset we can join embeddings for corresponding `Disease` and `treatment` nodes and use these to predict against the `y` column.
    - Here we run 5-fold cross validated evaluation of the model against an 80% training dataset, then validate the performance against a held-out 20% split. 
    - In testing against 10 000 randomly sampled rows of the ground truth dataset and using the provided embeddings, the `XGBoostClassifer` reaches ROC AUC scores of 0.9196 (mean of 5xCV) and 0.9137 (20% reserved validation). 
        - This shows some overfitting (kind of expected with XGB) but will likely scale as we use more of the dataset. 
6. I have left Neo4J loading the edges overnight and will check the performance of XGBoost against my embeddings tomorrow...
## Usage

```bash
git clone https://github.com/JBwdn/ec_tech_assesment.git
cd ec_tech_assesment

# Create virtual python env
micromamba create -f environment.yml
micromamba activate ec_tech

# Install package (contains the 4 scripts)
pip install .

# Download the provided files (Nodes.csv etc..) from drive into `data/`
# Launch Neo4J (calls `podman pull ...` and `podman run ...`)
cd data/
launch_n4j

# Load nodes and edges into Neo4J
load_data

# Run FastRP
generate_embeddings

# Train an XGBoost classifier on the embeddings
train_xgb
```

## Dev installation

```bash
micromamba create -f environment.yml
micromamba activate ec_tech

pip install .  # Basic install
pip install -e ".[dev]"  # Install in editable mode with dev dependencies
pip install ".[test]"  # Install the package and all test dependencies
```

### Running pre-commit hooks

```bash
# Install the hooks:
pre-commit install

# Run all the hooks:
pre-commit run --all-files
```
