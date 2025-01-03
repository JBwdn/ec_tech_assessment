"""
Train an XGBoost classifer on the graph embeddings.
"""

# pylint: disable=unnecessary-lambda-assignment,too-many-locals

import numpy as np
import polars as pl
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold, train_test_split
from xgboost import XGBClassifier

GROUND_TRUTH_PATH = "~/scratch/everycure/data/Ground_Truth.csv"
EMBEDDINGS_PATH = "~/scratch/everycure/data/Embeddings.csv"

XGB_PARAMS = {}


def main() -> None:
    """
    Load the ground truth dataset and the embeddings, join them, and train
    and evaluate an XGBoost classifier.
    """
    # Mung and join the data:
    ground_truth_df = pl.read_csv(GROUND_TRUTH_PATH).sample(10000)
    embeddings_df = pl.read_csv(EMBEDDINGS_PATH)

    emb_mapper = lambda id: embeddings_df.filter(pl.col("id") == id)[
        "topological_embedding"
    ].first()
    eval_mapper = lambda x: np.fromstring(x.strip("[]"), sep=" ")

    ground_truth_df = ground_truth_df.with_columns(
        [
            pl.col("source").map_elements(emb_mapper).map_elements(eval_mapper),
            pl.col("target").map_elements(emb_mapper).map_elements(eval_mapper),
        ]
    )

    # Set up np arrays of the data and split:
    x = np.concatenate(
        [
            np.stack(ground_truth_df["source"].to_list()),
            np.stack(ground_truth_df["target"].to_list()),
        ],
        axis=1,
    )

    y = ground_truth_df["y"].to_numpy()

    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.2, shuffle=True)

    print(f"Train size = {x_train.shape[0]}, Val size = {x_val.shape[0]}")  # type: ignore

    # 5 fold cross validation training:
    kfolder = KFold(n_splits=5)
    scores = []

    for train_index, test_index in kfolder.split(x_train, y_train):
        model = XGBClassifier(**XGB_PARAMS)
        model.fit(x_train[train_index], y_train[train_index])
        y_pred = model.predict_proba(x_train[test_index])[:, 1]
        score = roc_auc_score(y_train[test_index], y_pred)
        scores.append(score)

    print(f"5 fold cv ROCAUC = {list(scores)} (mean = {np.mean(scores)})")

    # Final retrain on all training data:
    model = XGBClassifier(**XGB_PARAMS)
    model.fit(x_train, y_train)
    y_pred = model.predict_proba(x_val)[:, 1]
    score = roc_auc_score(y_val, y_pred)

    print(f"Val ROCAUC = {score}")


if __name__ == "__main__":
    main()
