"""
Base ML Training Utilities

Provides common utilities used by all ML models.
"""

from pathlib import Path

import joblib


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SAVED_MODELS_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

def ensure_model_directory():
    """
    Create the saved_models directory if it does not exist.
    """

    SAVED_MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    return SAVED_MODELS_DIR


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model,
    filename
):
    """
    Save a trained ML model using joblib.

    Parameters
    ----------
    model:
        Trained machine learning model.

    filename:
        Filename including .joblib extension.

    Returns
    -------
    Path
        Path of saved model.
    """

    ensure_model_directory()

    if not filename.endswith(".joblib"):
        filename = f"{filename}.joblib"

    model_path = (
        SAVED_MODELS_DIR
        / filename
    )

    joblib.dump(
        model,
        model_path
    )

    print(
        f"\nModel saved successfully:"
    )

    print(
        model_path
    )

    return model_path


# ============================================================
# LOAD MODEL
# ============================================================

def load_model(filename):
    """
    Load a previously saved ML model.
    """

    if not filename.endswith(".joblib"):
        filename = f"{filename}.joblib"

    model_path = (
        SAVED_MODELS_DIR
        / filename
    )

    if not model_path.exists():

        raise FileNotFoundError(
            f"Saved model not found:\n"
            f"{model_path}"
        )

    model = joblib.load(
        model_path
    )

    print(
        f"\nModel loaded successfully:"
    )

    print(
        model_path
    )

    return model