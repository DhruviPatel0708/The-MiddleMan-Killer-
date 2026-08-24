"""
AGRICULTURE AI - MODEL ADAPTERS

Purpose:
    Prepare model-specific inputs for the 13 trained ML models.

Important:
    - Does NOT retrain models.
    - Does NOT modify saved models.
    - Does NOT modify source datasets.
    - Uses exact model feature schemas.
    - Recreates buyer engineered features required by buyer_model.joblib.

"""

from pathlib import Path

import numpy as np
import pandas as pd

from prediction_service import PredictionService


# ======================================================================
# PATHS
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_ROOT = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_ROOT / "raw"

PROCESSED_DATA_DIR = DATA_ROOT / "processed"


# ======================================================================
# MODEL ADAPTERS
# ======================================================================

class ModelAdapters:

    def __init__(self, prediction_service=None):

        print("=" * 70)
        print("MODEL ADAPTERS")
        print("=" * 70)

        if prediction_service is None:
            self.prediction_service = PredictionService()
        else:
            self.prediction_service = prediction_service

        self.datasets = {}

        self._load_datasets()

        print("\n✓ Model adapters initialized.")

    # ==================================================================
    # DATASET LOADING
    # ==================================================================

    def _load_datasets(self):

        print("\nLoading adapter datasets...")
        print("-" * 70)

        processed_files = {
            "buyers": "buyers.csv",
            "price": "price_features.csv",
            "demand": "demand_features.csv",
            "quality": "quality_features.csv",
            "logistics": "logistics_features.csv",
            "cost": "cost_features.csv",
            "transactions": "transaction_features.csv",
        }

        for name, filename in processed_files.items():

            path = PROCESSED_DATA_DIR / filename

            if not path.exists():

                print(
                    f"⚠ {name:<15} "
                    f"Missing: {filename}"
                )

                continue

            dataframe = pd.read_csv(path)

            self.datasets[name] = dataframe

            print(
                f"✓ {name:<15} "
                f"Rows: {len(dataframe):,}"
            )

        # --------------------------------------------------------------
        # Farmers are kept in RAW
        # --------------------------------------------------------------

        farmer_path = RAW_DATA_DIR / "farmers.csv"

        if farmer_path.exists():

            self.datasets["farmers"] = pd.read_csv(
                farmer_path
            )

            print(
                f"✓ {'farmers':<15} "
                f"Rows: "
                f"{len(self.datasets['farmers']):,}"
            )

        else:

            print(
                f"⚠ {'farmers':<15} "
                f"Missing: {farmer_path}"
            )

        print("-" * 70)

    # ==================================================================
    # GENERIC FEATURE CHECK
    # ==================================================================

    def _check_features(
        self,
        model_name,
        dataframe
    ):

        expected = (
            self.prediction_service
            .get_expected_features(
                model_name
            )
        )

        if expected is None:

            raise ValueError(
                f"Unable to determine feature "
                f"schema for model: {model_name}"
            )

        missing = [
            column
            for column in expected
            if column not in dataframe.columns
        ]

        if missing:

            raise ValueError(
                f"{model_name} adapter is missing "
                f"features: {missing}"
            )

        return dataframe[expected].copy()

    # ==================================================================
    # GENERIC ROW NORMALIZATION
    # ==================================================================

    def _normalize_row(
        self,
        dataframe,
        row
    ):

        if row is None:

            return dataframe.iloc[[0]].copy()

        if isinstance(row, pd.Series):

            return row.to_frame().T.copy()

        if isinstance(row, dict):

            return pd.DataFrame([row])

        if isinstance(row, pd.DataFrame):

            return row.copy()

        raise TypeError(
            "row must be None, pandas Series, "
            "pandas DataFrame, or dictionary."
        )

    # ==================================================================
    # PRICE ADAPTER
    # ==================================================================

    def build_price_input(
        self,
        row=None
    ):

        dataframe = self.datasets["price"]

        row = self._normalize_row(
            dataframe,
            row
        )

        return self._check_features(
            "price",
            row
        )

    # ==================================================================
    # DEMAND ADAPTER
    # ==================================================================

    def build_demand_input(
        self,
        row=None
    ):

        dataframe = self.datasets["demand"]

        row = self._normalize_row(
            dataframe,
            row
        )

        return self._check_features(
            "demand",
            row
        )

    # ==================================================================
    # BUYER ADAPTER
    # ==================================================================

    def build_buyer_input(
        self,
        row=None
    ):

        dataframe = self.datasets["buyers"]

        row = self._normalize_row(
            dataframe,
            row
        )

        # --------------------------------------------------------------
        # Required raw buyer columns
        # --------------------------------------------------------------

        required_raw_columns = [
            "required_quantity_kg",
            "minimum_quantity_kg",
            "maximum_quantity_kg",
            "payment_terms_days",
            "buyer_rating",
            "total_previous_transactions",
            "successful_transactions",
            "cancelled_transactions",
            "late_payments",
            "average_payment_delay_days",
        ]

        missing_raw = [
            column
            for column in required_raw_columns
            if column not in row.columns
        ]

        if missing_raw:

            raise ValueError(
                "Buyer adapter is missing raw columns: "
                f"{missing_raw}"
            )

        # --------------------------------------------------------------
        # Convert numerical fields
        # --------------------------------------------------------------

        for column in required_raw_columns:

            row[column] = pd.to_numeric(
                row[column],
                errors="coerce"
            )

        # --------------------------------------------------------------
        # Safe denominators
        # --------------------------------------------------------------

        total_transactions = (
            row["total_previous_transactions"]
            .replace(0, np.nan)
        )

        maximum_quantity = (
            row["maximum_quantity_kg"]
            .replace(0, np.nan)
        )

        payment_terms = (
            row["payment_terms_days"]
            .replace(0, np.nan)
        )

        # --------------------------------------------------------------
        # Recreate engineered buyer features
        # --------------------------------------------------------------

        row["successful_transaction_rate"] = (
            row["successful_transactions"]
            / total_transactions
        )

        row["cancellation_rate"] = (
            row["cancelled_transactions"]
            / total_transactions
        )

        row["late_payment_rate"] = (
            row["late_payments"]
            / total_transactions
        )

        row["successful_transactions_per_total"] = (
            row["successful_transactions"]
            / total_transactions
        )

        row["acceptable_quantity_range_kg"] = (
            row["maximum_quantity_kg"]
            - row["minimum_quantity_kg"]
        )

        row["required_quantity_to_max_ratio"] = (
            row["required_quantity_kg"]
            / maximum_quantity
        )

        row["payment_delay_to_terms_ratio"] = (
            row["average_payment_delay_days"]
            / payment_terms
        )

        # --------------------------------------------------------------
        # Clean engineered values
        # --------------------------------------------------------------

        engineered_columns = [
            "successful_transaction_rate",
            "cancellation_rate",
            "late_payment_rate",
            "successful_transactions_per_total",
            "acceptable_quantity_range_kg",
            "required_quantity_to_max_ratio",
            "payment_delay_to_terms_ratio",
        ]

        row[engineered_columns] = (
            row[engineered_columns]
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
            .fillna(0)
        )

        # --------------------------------------------------------------
        # Exact buyer model schema
        # --------------------------------------------------------------

        return self._check_features(
            "buyer",
            row
        )

    # ==================================================================
    # QUALITY ADAPTER
    # ==================================================================

    def build_quality_input(
        self,
        row=None
    ):

        dataframe = self.datasets["quality"]

        row = self._normalize_row(
            dataframe,
            row
        )

        return self._check_features(
            "quality_score",
            row
        )

    # ==================================================================
    # QUALITY PREDICTIONS
    # ==================================================================

    def predict_quality(
        self,
        row=None
    ):

        quality_input = (
            self.build_quality_input(
                row
            )
        )

        quality_score = (
            self.prediction_service
            .predict_one(
                "quality_score",
                quality_input
            )
        )

        quality_grade = (
            self.prediction_service
            .predict_one(
                "quality_grade",
                quality_input
            )
        )

        spoilage_score = (
            self.prediction_service
            .predict_one(
                "spoilage_score",
                quality_input
            )
        )

        spoilage_risk = (
            self.prediction_service
            .predict_one(
                "spoilage_risk",
                quality_input
            )
        )

        return {
            "quality_score": float(
                quality_score
            ),

            "quality_grade": str(
                quality_grade
            ),

            "spoilage_risk_score": float(
                spoilage_score
            ),

            "spoilage_risk": str(
                spoilage_risk
            ),
        }

    # ==================================================================
    # LOGISTICS ADAPTER
    # ==================================================================

    def build_logistics_input(
        self,
        row=None
    ):

        dataframe = self.datasets["logistics"]

        row = self._normalize_row(
            dataframe,
            row
        )

        return self._check_features(
            "transport_cost",
            row
        )

    # ==================================================================
    # LOGISTICS PREDICTIONS
    # ==================================================================

    def predict_logistics(
        self,
        row=None
    ):

        logistics_input = (
            self.build_logistics_input(
                row
            )
        )

        transport_cost = (
            self.prediction_service
            .predict_one(
                "transport_cost",
                logistics_input
            )
        )

        delay_hours = (
            self.prediction_service
            .predict_one(
                "delay_hours",
                logistics_input
            )
        )

        damage_percentage = (
            self.prediction_service
            .predict_one(
                "damage_percentage",
                logistics_input
            )
        )

        return {
            "transport_cost": float(
                transport_cost
            ),

            "delay_hours": float(
                delay_hours
            ),

            "damage_percentage": float(
                damage_percentage
            ),
        }

    # ==================================================================
    # COST ADAPTER
    # ==================================================================

    def build_cost_input(
        self,
        row=None
    ):

        dataframe = self.datasets["cost"]

        row = self._normalize_row(
            dataframe,
            row
        )

        return self._check_features(
            "cost",
            row
        )

    # ==================================================================
    # COST PREDICTION
    # ==================================================================

    def predict_cost(
        self,
        row=None
    ):

        cost_input = (
            self.build_cost_input(
                row
            )
        )

        prediction = (
            self.prediction_service
            .predict_one(
                "cost",
                cost_input
            )
        )

        return {
            "estimated_total_cost": float(
                prediction
            )
        }

    # ==================================================================
    # RISK ADAPTER
    # ==================================================================

    def build_risk_input(
        self,
        row=None
    ):

        dataframe = self.datasets["transactions"]

        row = self._normalize_row(
            dataframe,
            row
        )

        payment_input = (
            self._check_features(
                "payment_risk",
                row
            )
        )

        delivery_input = (
            self._check_features(
                "delivery_risk",
                row
            )
        )

        return (
            payment_input,
            delivery_input
        )

    # ==================================================================
    # RISK PREDICTIONS
    # ==================================================================

    def predict_risk(
        self,
        row=None
    ):

        (
            payment_input,
            delivery_input
        ) = self.build_risk_input(
            row
        )

        payment_risk = (
            self.prediction_service
            .predict_one(
                "payment_risk",
                payment_input
            )
        )

        delivery_risk = (
            self.prediction_service
            .predict_one(
                "delivery_risk",
                delivery_input
            )
        )

        return {
            "payment_risk": str(
                payment_risk
            ),

            "delivery_risk": str(
                delivery_risk
            ),
        }

    # ==================================================================
    # BUYER PREDICTION
    # ==================================================================

    def predict_buyer(
        self,
        row=None
    ):

        buyer_input = (
            self.build_buyer_input(
                row
            )
        )

        prediction = (
            self.prediction_service
            .predict_one(
                "buyer",
                buyer_input
            )
        )

        return {
            "buyer_reliability": str(
                prediction
            )
        }

    # ==================================================================
    # OPERATIONAL PREDICTIONS
    # ==================================================================

    def predict_operational_models(
        self,
        quality_row=None,
        logistics_row=None,
        cost_row=None,
        risk_row=None,
        buyer_row=None
    ):

        results = {}

        results["quality"] = (
            self.predict_quality(
                quality_row
            )
        )

        results["logistics"] = (
            self.predict_logistics(
                logistics_row
            )
        )

        results["cost"] = (
            self.predict_cost(
                cost_row
            )
        )

        results["risk"] = (
            self.predict_risk(
                risk_row
            )
        )

        results["buyer"] = (
            self.predict_buyer(
                buyer_row
            )
        )

        return results

    # ==================================================================
    # VALIDATE ALL ADAPTERS
    # ==================================================================

    def validate_all_adapters(self):

        print("\n" + "=" * 70)
        print("VALIDATING MODEL ADAPTERS")
        print("=" * 70)

        results = {}

        # --------------------------------------------------------------
        # Price
        # --------------------------------------------------------------

        try:

            self.build_price_input()

            results["price"] = True

            print("✓ price adapter")

        except Exception as error:

            results["price"] = False

            print(
                f"✗ price adapter: {error}"
            )

        # --------------------------------------------------------------
        # Demand
        # --------------------------------------------------------------

        try:

            self.build_demand_input()

            results["demand"] = True

            print("✓ demand adapter")

        except Exception as error:

            results["demand"] = False

            print(
                f"✗ demand adapter: {error}"
            )

        # --------------------------------------------------------------
        # Buyer
        # --------------------------------------------------------------

        try:

            self.build_buyer_input()

            results["buyer"] = True

            print("✓ buyer adapter")

        except Exception as error:

            results["buyer"] = False

            print(
                f"✗ buyer adapter: {error}"
            )

        # --------------------------------------------------------------
        # Quality
        # --------------------------------------------------------------

        try:

            self.build_quality_input()

            results["quality"] = True

            print("✓ quality adapter")

        except Exception as error:

            results["quality"] = False

            print(
                f"✗ quality adapter: {error}"
            )

        # --------------------------------------------------------------
        # Logistics
        # --------------------------------------------------------------

        try:

            self.build_logistics_input()

            results["logistics"] = True

            print("✓ logistics adapter")

        except Exception as error:

            results["logistics"] = False

            print(
                f"✗ logistics adapter: {error}"
            )

        # --------------------------------------------------------------
        # Cost
        # --------------------------------------------------------------

        try:

            self.build_cost_input()

            results["cost"] = True

            print("✓ cost adapter")

        except Exception as error:

            results["cost"] = False

            print(
                f"✗ cost adapter: {error}"
            )

        # --------------------------------------------------------------
        # Risk
        # --------------------------------------------------------------

        try:

            self.build_risk_input()

            results["risk"] = True

            print("✓ risk adapter")

        except Exception as error:

            results["risk"] = False

            print(
                f"✗ risk adapter: {error}"
            )

        # --------------------------------------------------------------
        # Summary
        # --------------------------------------------------------------

        passed = sum(
            results.values()
        )

        total = len(results)

        print("\n" + "-" * 70)

        print(
            f"Adapters passed: "
            f"{passed}/{total}"
        )

        if passed == total:

            print(
                "✓ ALL MODEL ADAPTERS PASSED"
            )

        else:

            print(
                "⚠ Some adapters require attention."
            )

        return results


# ======================================================================
# TEST
# ======================================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("MODEL ADAPTER TEST")
    print("=" * 70)

    try:

        adapters = ModelAdapters()

        validation = (
            adapters.validate_all_adapters()
        )

        if all(validation.values()):

            print("\n" + "=" * 70)
            print("RUNNING SAMPLE MODEL PREDICTIONS")
            print("=" * 70)

            # ----------------------------------------------------------
            # Buyer
            # ----------------------------------------------------------

            buyer_result = (
                adapters.predict_buyer()
            )

            print("\nBuyer:")

            for key, value in (
                buyer_result.items()
            ):

                print(
                    f"  {key:<30}: "
                    f"{value}"
                )

            # ----------------------------------------------------------
            # Quality
            # ----------------------------------------------------------

            quality_result = (
                adapters.predict_quality()
            )

            print("\nQuality / Spoilage:")

            for key, value in (
                quality_result.items()
            ):

                print(
                    f"  {key:<30}: "
                    f"{value}"
                )

            # ----------------------------------------------------------
            # Logistics
            # ----------------------------------------------------------

            logistics_result = (
                adapters.predict_logistics()
            )

            print("\nLogistics:")

            for key, value in (
                logistics_result.items()
            ):

                print(
                    f"  {key:<30}: "
                    f"{value:.4f}"
                )

            # ----------------------------------------------------------
            # Cost
            # ----------------------------------------------------------

            cost_result = (
                adapters.predict_cost()
            )

            print("\nCost:")

            for key, value in (
                cost_result.items()
            ):

                print(
                    f"  {key:<30}: "
                    f"{value:.2f}"
                )

            # ----------------------------------------------------------
            # Risk
            # ----------------------------------------------------------

            risk_result = (
                adapters.predict_risk()
            )

            print("\nRisk:")

            for key, value in (
                risk_result.items()
            ):

                print(
                    f"  {key:<30}: "
                    f"{value}"
                )

            print("\n" + "=" * 70)
            print(
                "✓ MODEL ADAPTER TEST COMPLETED"
            )
            print("=" * 70)

            print(
                "\n✓ All 7 model adapters passed."
            )

            print(
                "✓ Real dataset rows were used."
            )

            print(
                "✓ No fake prediction values generated."
            )

            print(
                "✓ Existing ML models remain unchanged."
            )

        else:

            print("\n" + "=" * 70)
            print(
                "⚠ SAMPLE PREDICTIONS NOT RUN"
            )
            print("=" * 70)

            print(
                "\nFix failed adapter schemas first."
            )

    except Exception as error:

        print("\n" + "=" * 70)
        print(
            "✗ MODEL ADAPTER TEST FAILED"
        )
        print("=" * 70)

        print(
            f"\nError: {error}"
        )