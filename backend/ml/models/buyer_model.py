"""
Buyer Reliability Classification Model

Target:
    buyer_reliability_label

Problem:
    Multiclass classification

Classes:
    RELIABLE
    MODERATE
    UNRELIABLE

Important:
    The dataset is highly imbalanced, so class_weight='balanced'
    is used during training.
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42


# ============================================================
# CREATE BUYER MODEL
# ============================================================

def create_buyer_model(
    numerical_features,
    categorical_features
):
    """
    Create the buyer reliability classification pipeline.

    Parameters
    ----------
    numerical_features : list
        Numerical feature names.

    categorical_features : list
        Categorical feature names.

    Returns
    -------
    Pipeline
        Preprocessing + Random Forest classifier.
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
    # Random Forest classifier
    # --------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=400,
        max_depth=18,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
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