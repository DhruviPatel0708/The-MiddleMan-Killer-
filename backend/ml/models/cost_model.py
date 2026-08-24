"""
Cost Estimation Model

Target:
    estimated_total_cost

Problem:
    Regression
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42


# ============================================================
# CREATE COST MODEL
# ============================================================

def create_cost_model(
    numerical_features,
    categorical_features
):
    """
    Create the Cost Estimation regression pipeline.

    Numerical features:
        Passed through without scaling.

    Categorical features:
        One-hot encoded.

    Model:
        RandomForestRegressor
    """

    # --------------------------------------------------------
    # NUMERICAL PREPROCESSING
    # --------------------------------------------------------

    numerical_transformer = "passthrough"

    # --------------------------------------------------------
    # CATEGORICAL PREPROCESSING
    # --------------------------------------------------------

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True
    )

    # --------------------------------------------------------
    # COMBINED PREPROCESSOR
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
    # RANDOM FOREST REGRESSOR
    # --------------------------------------------------------

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    # --------------------------------------------------------
    # COMPLETE PIPELINE
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