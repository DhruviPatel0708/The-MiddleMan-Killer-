"""
Crop Quality Models

Four separate prediction tasks:

1. quality_score
       Regression

2. quality_grade
       Classification

3. spoilage_risk_score
       Regression

4. spoilage_risk
       Classification
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier
)
from sklearn.pipeline import Pipeline


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42


# ============================================================
# COMMON PREPROCESSOR
# ============================================================

def create_preprocessor(
    numerical_features,
    categorical_features
):
    """
    Create preprocessing pipeline shared by
    all quality models.
    """

    numerical_transformer = "passthrough"

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True
    )

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

    return preprocessor


# ============================================================
# QUALITY SCORE MODEL
# ============================================================

def create_quality_score_model(
    numerical_features,
    categorical_features
):
    """
    Predict quality_score.
    """

    preprocessor = create_preprocessor(
        numerical_features,
        categorical_features
    )

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

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


# ============================================================
# QUALITY GRADE MODEL
# ============================================================

def create_quality_grade_model(
    numerical_features,
    categorical_features
):
    """
    Predict quality_grade.
    """

    preprocessor = create_preprocessor(
        numerical_features,
        categorical_features
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

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


# ============================================================
# SPOILAGE RISK SCORE MODEL
# ============================================================

def create_spoilage_risk_score_model(
    numerical_features,
    categorical_features
):
    """
    Predict spoilage_risk_score.
    """

    preprocessor = create_preprocessor(
        numerical_features,
        categorical_features
    )

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

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


# ============================================================
# SPOILAGE RISK MODEL
# ============================================================

def create_spoilage_risk_model(
    numerical_features,
    categorical_features
):
    """
    Predict spoilage_risk.
    """

    preprocessor = create_preprocessor(
        numerical_features,
        categorical_features
    )

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=20,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

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