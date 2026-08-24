"""
Transaction Risk Models

Targets:
    payment_status
    delivery_status

Problem:
    Multiclass classification
"""

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline


RANDOM_STATE = 42


# ============================================================
# COMMON PREPROCESSOR
# ============================================================

def create_preprocessor(
    numerical_features,
    categorical_features
):

    return ColumnTransformer(
        transformers=[
            (
                "numerical",
                "passthrough",
                numerical_features
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True
                ),
                categorical_features
            )
        ],
        remainder="drop"
    )


# ============================================================
# PAYMENT RISK MODEL
# ============================================================

def create_payment_risk_model(
    numerical_features,
    categorical_features
):

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

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )


# ============================================================
# DELIVERY RISK MODEL
# ============================================================

def create_delivery_risk_model(
    numerical_features,
    categorical_features
):

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

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )