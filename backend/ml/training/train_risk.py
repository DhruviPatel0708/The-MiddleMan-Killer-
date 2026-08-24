"""
Transaction Risk Model Training

Models:
    payment_status
    delivery_status
"""

import sys
from pathlib import Path

from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.ml.datasets.transaction_dataset import (
    prepare_transaction_dataset
)

from backend.ml.models.risk_model import (
    create_payment_risk_model,
    create_delivery_risk_model
)

from backend.ml.training.base_trainer import (
    save_model
)


RANDOM_STATE = 42
TEST_SIZE = 0.20


def train_risk_models():

    print("=" * 70)
    print("RISK PREDICTION MODEL TRAINING")
    print("=" * 70)

    dataset = prepare_transaction_dataset()

    X = dataset["X"]

    numerical_features = (
        dataset["numerical_columns"]
    )

    categorical_features = (
        dataset["categorical_columns"]
    )

    targets = dataset["targets"]

    required_targets = [
        "payment_status",
        "delivery_status"
    ]

    missing_targets = [
        target
        for target in required_targets
        if target not in targets
    ]

    if missing_targets:
        raise ValueError(
            f"Missing risk targets: {missing_targets}"
        )

    print("\nDataset ready for training.")

    print(
        f"Rows    : {len(X):,}"
    )

    print(
        f"Features: {X.shape[1]}"
    )

    # --------------------------------------------------------
    # COMMON SPLIT
    # --------------------------------------------------------

    train_indices, test_indices = train_test_split(
        range(len(X)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=targets["payment_status"]
    )

    train_indices = list(train_indices)
    test_indices = list(test_indices)

    X_train = (
        X.iloc[train_indices]
        .reset_index(drop=True)
    )

    X_test = (
        X.iloc[test_indices]
        .reset_index(drop=True)
    )

    print("\nTraining:")
    print(f"X_train: {X_train.shape}")

    print("\nTesting:")
    print(f"X_test : {X_test.shape}")

    # --------------------------------------------------------
    # MODELS
    # --------------------------------------------------------

    models = {
        "payment_status":
            create_payment_risk_model(
                numerical_features,
                categorical_features
            ),

        "delivery_status":
            create_delivery_risk_model(
                numerical_features,
                categorical_features
            )
    }

    saved_models = {}

    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    for target_name, model in models.items():

        print("\n" + "=" * 70)
        print(f"TRAINING: {target_name}")
        print("=" * 70)

        y_train = (
            targets[target_name]
            .iloc[train_indices]
            .reset_index(drop=True)
        )

        print("\nTarget distribution:")
        print(
            y_train.value_counts().to_string()
        )

        print("\nTraining started...")

        model.fit(
            X_train,
            y_train
        )

        print(
            f"{target_name} training completed."
        )

        model_file = (
            "payment_risk_model.joblib"
            if target_name == "payment_status"
            else "delivery_risk_model.joblib"
        )

        saved_models[target_name] = save_model(
            model,
            model_file
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RISK MODEL TRAINING COMPLETED")
    print("=" * 70)

    for target_name, model_path in saved_models.items():

        print(
            f"\n{target_name}:"
        )

        print(
            f"  {model_path}"
        )

    return saved_models


if __name__ == "__main__":

    try:

        train_risk_models()

        print(
            "\n✓ Risk model training completed successfully."
        )

    except Exception as error:

        print("\n" + "=" * 70)
        print("RISK MODEL TRAINING FAILED")
        print("=" * 70)

        print(
            f"\nError: {error}"
        )

        sys.exit(1)