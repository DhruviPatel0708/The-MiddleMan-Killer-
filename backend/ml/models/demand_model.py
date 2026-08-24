"""
Demand Forecasting Model

Task:
    Predict next_day_demand_tonnes

Problem type:
    Regression

Approach:
    HistGradientBoostingRegressor
    Log-transformed target
"""

import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import TransformedTargetRegressor


RANDOM_STATE = 42


def create_demand_model(
    numerical_features,
    categorical_features
):
    """
    Create demand forecasting pipeline.
    """

    # ========================================================
    # CATEGORICAL ENCODING
    # ========================================================

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False
    )

    # ========================================================
    # PREPROCESSOR
    # ========================================================

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                "passthrough",
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

    # ========================================================
    # HISTOGRAM GRADIENT BOOSTING
    # ========================================================

    base_model = HistGradientBoostingRegressor(
        max_iter=500,
        learning_rate=0.05,
        max_leaf_nodes=31,
        max_depth=None,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=RANDOM_STATE
    )

    # ========================================================
    # LOG TARGET TRANSFORMATION
    # ========================================================

    model = TransformedTargetRegressor(
        regressor=base_model,
        func=np.log1p,
        inverse_func=np.expm1
    )

    # ========================================================
    # COMPLETE PIPELINE
    # ========================================================

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