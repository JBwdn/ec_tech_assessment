# EveryCure tech assessment

## Overview/Plan

1. Set up project and dev environment (github, docker etc.)
2. Load data into a Neo4j graph
3. Generate embeddings for downstream ML
4. Build predictive model to predict disease-drug response

## Key files

1. [launch_neo4j.py](/package/scripts/launch_neo4j.py) - Neo4j container configuration
2. [load_data.py](/package/scripts/load_data.py) - Load the nodes and edges into Neo4j
3. [generate_embeddings.py](/package/scripts/generate_embeddings.py) - Run FastRP, write embeddings to nodes and output to a csv
4. [train_xgb.py](/package/scripts/train_xgb.py) - Train an XGBoost classifier on the embeddings and evaluate using ROC AUC score

The FastRP embeddings can be downloaded from Drive [here](https://drive.google.com/file/d/16Randy7chdKWJVRHluKWLntbNuEIwXVj/view?usp=sharing)

## Notes

1. I have used a previously made python template to structure the repo making it pip installable [link](https://github.com/JBwdn/python_template). This is pre-configured to use a few tools including: 
    - micromamba - manage the virtual python env
    - pre-commit - hooks for formatting and linting python 
2. I am using podman for managing the Neo4J docker container, which is called using `subprocess` from the `launch_n4j` script. The port mapping, mapped volume and container max memory are configured using CLI arguments and Neo4j plugins are configured by passing environment variables to the container.
    - This needs to be run from within the `data/` directory containing the provided data files.
3. The data loading script works well for the nodes but is very slow for the relationships (due to looking up the id for each `from_id` and `to_id` field). Previously I have used the Neo4j admin import command to load large lists of edges, but this requires some data preprocessing and is probably beyond the scope for now.
    - All provided fields are loaded into the graph, but I will probably only use the topology to generate embeddings as augmenting the graph with features from the cross-referenced databases will be take a while...
4. I have chosen to use FastRP for generating node embeddings from the graph. At least for the number of edges I have loaded this seems to run fast enough that calculating these for ALL node types is not a big deal. Then I will pull the required embeddings from the `generated_embeddings.csv` output file using the ids in `Ground Truth.csv`.
    - FastRP is better for use with undirected relationships but it is what I am more familiar with from GDS so have used that here.
5. In my previous role XGBoost has performed well on tasks involving graph embeddings (though primarily this was regression problems). Here we will just use the default parameters, however a logical next stage would be to perform a hyperparameter sweep against the embeddings.
    - Using the ground truth dataset we can join embeddings for corresponding `Disease` and `treatment` nodes and use these to predict against the `y` column.
    - Here we run 5-fold cross validated evaluation of the model against an 80% training dataset, then validate the performance against a held-out 20% split. 
    - In testing against 10 000 randomly sampled rows of the ground truth dataset and using the provided embeddings, the `XGBoostClassifer` reaches ROC AUC scores of **0.9196 (mean of 5xCV) and 0.9137 (20% reserved validation).** 
        - This shows some overfitting (kind of expected with XGB) but will likely scale as we use more of the dataset. 
6. I have left Neo4J loading the edges overnight and will check the performance of XGBoost against my embeddings tomorrow... This has worked but took around 12 hours - there are optimisations for the edge loading CQL query such as batching and multiprocessing (another sensible option would be to run Neo4j on something more powerful than my laptop)
7. Using the FastRP embeddings, the classifier achieves ROC AUC scores of:
    - (with 10000 samples) **0.8102 (mean of 5xCV) and 0.7984 (20% reserved validation)**
    - (with the whole ground truth dataset) **0.8386 (mean of 5xCV) and 0.8504 (20% reserved validation)**
8.  My embeddings therefore are useful in predicting against this dataset! They are of lower quality than those provided, however, it would be simple to evaluate the other algorithms available in GDS (eg. GraphSAGE and Node2Vec) and test how increasing the embedding dimension changes performance.

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
