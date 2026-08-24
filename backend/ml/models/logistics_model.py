"""
Logistics Prediction Models

Three separate regression tasks:

1. transport_cost
2. delay_hours
3. damage_percentage
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
# COMMON PREPROCESSOR
# ============================================================

def create_preprocessor(
    numerical_features,
    categorical_features
):
    """
    Create the preprocessing pipeline shared by
    all logistics models.
    """

    numerical_transformer = "passthrough"

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True
    )

    return ColumnTransformer(
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


# ============================================================
# TRANSPORT COST MODEL
# ============================================================

def create_transport_cost_model(
    numerical_features,
    categorical_features
):
    """
    Predict transport_cost.
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

    return Pipeline(
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


# ============================================================
# DELAY HOURS MODEL
# ============================================================

def create_delay_hours_model(
    numerical_features,
    categorical_features
):
    """
    Predict delay_hours.
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

    return Pipeline(
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


# ============================================================
# DAMAGE PERCENTAGE MODEL
# ============================================================

def create_damage_percentage_model(
    numerical_features,
    categorical_features
):
    """
    Predict damage_percentage.
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

    return Pipeline(
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