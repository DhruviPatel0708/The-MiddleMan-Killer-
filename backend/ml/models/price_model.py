"""
Price Prediction Model

Task:
    Predict next_modal_price_per_quintal

Problem type:
    Regression

Input:
    Price ML features prepared by price_dataset.py

Training:
    Will be handled by train_price.py

Evaluation:
    Will be handled by evaluate_price.py
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline


# ============================================================
# MODEL CONFIGURATION
# ============================================================

RANDOM_STATE = 42


# ============================================================
# CREATE PRICE MODEL
# ============================================================

def create_price_model(
    numerical_features,
    categorical_features
):
    """
    Create the complete price prediction pipeline.

    Parameters
    ----------
    numerical_features : list
        Numerical ML feature names.

    categorical_features : list
        Categorical ML feature names.

    Returns
    -------
    Pipeline
        Preprocessing + regression model.
    """

    # --------------------------------------------------------
    # Numerical preprocessing
    # --------------------------------------------------------

    numerical_transformer = "passthrough"

    # --------------------------------------------------------
    # Categorical preprocessing
    # --------------------------------------------------------

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True
    )

    # --------------------------------------------------------
    # Combined preprocessing
    # --------------------------------------------------------

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_transformer,
                numerical_features
            ),
            (
                "categorical",
                categorical_transformer,
                categorical_features
            )
        ],
        remainder="drop"
    )

    # --------------------------------------------------------
    # Regression model
    # --------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    # --------------------------------------------------------
    # Complete pipeline
    # --------------------------------------------------------

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    return pipeline