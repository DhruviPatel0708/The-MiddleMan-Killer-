"""
LOGISTICS OPTIMIZATION

EXECUTION & MATCHING ARCHITECTURE
----------------------------------------------------------------------

Buyer Matching
      ↓
AI Auction
      ↓
Risk-Aware Bidding
      ↓
Net Profit Optimization
      ↓
LOGISTICS OPTIMIZATION
      ↓
Best Transport / Market Option

USES ONLY:
----------------------------------------------------------------------
✓ Existing transport_cost_model.joblib
✓ Existing delay_hours_model.joblib
✓ Existing damage_percentage_model.joblib
✓ Existing logistics_features.csv
✓ Existing buyer / market information

NO:
----------------------------------------------------------------------
✗ New ML model
✗ Model retraining
✗ New dataset
✗ Dataset modification
✗ Fake predictions
✗ AI Agent
✗ Architecture change
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd


# ======================================================================
# PATHS
# ======================================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)

LOGISTICS_DATASET = (
    DATA_DIR
    / "logistics_features.csv"
)

TRANSPORT_MODEL = (
    MODEL_DIR
    / "transport_cost_model.joblib"
)

DELAY_MODEL = (
    MODEL_DIR
    / "delay_hours_model.joblib"
)

DAMAGE_MODEL = (
    MODEL_DIR
    / "damage_percentage_model.joblib"
)


# ======================================================================
# ENGINE
# ======================================================================

class LogisticsOptimizationEngine:

    def __init__(self):

        print()
        print("=" * 70)
        print("LOGISTICS OPTIMIZATION ENGINE")
        print("=" * 70)

        self.transport_model = None
        self.delay_model = None
        self.damage_model = None

        self.logistics_df = None

        self.transport_features = None
        self.delay_features = None
        self.damage_features = None

        self._load_existing_resources()

        print()
        print("✓ Logistics Optimization Engine initialized.")
        print("✓ Existing Logistics models loaded.")
        print("✓ Existing Logistics dataset loaded.")
        print("✓ No new ML model.")
        print("✓ No new dataset.")
        print("✓ No AI Agent.")

    # ==================================================================
    # SAFE NUMBER
    # ==================================================================

    @staticmethod
    def number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            value = float(value)

            if not np.isfinite(value):

                return default

            return value

        except Exception:

            return default

    # ==================================================================
    # FIND COLUMN
    # ==================================================================

    @staticmethod
    def find_column(
        df: pd.DataFrame,
        candidates: List[str],
    ) -> Optional[str]:

        # Exact match
        for candidate in candidates:

            if candidate in df.columns:

                return candidate

        # Case-insensitive match
        normalized = {

            str(column)
            .strip()
            .lower()
            .replace(" ", "_"):
                column

            for column in df.columns

        }

        for candidate in candidates:

            key = (
                str(candidate)
                .strip()
                .lower()
                .replace(" ", "_")
            )

            if key in normalized:

                return normalized[key]

        return None

    # ==================================================================
    # MODEL FEATURES
    # ==================================================================

    @staticmethod
    def get_model_features(
        model,
    ) -> Optional[List[str]]:

        features = getattr(
            model,
            "feature_names_in_",
            None,
        )

        if features is not None:

            return list(features)

        try:

            for _, step in model.steps:

                features = getattr(
                    step,
                    "feature_names_in_",
                    None,
                )

                if features is not None:

                    return list(features)

        except Exception:

            pass

        return None

    # ==================================================================
    # LOAD RESOURCES
    # ==================================================================

    def _load_existing_resources(self):

        print()
        print("Loading existing Logistics resources...")
        print("-" * 70)

        # --------------------------------------------------------------
        # Dataset
        # --------------------------------------------------------------

        if not LOGISTICS_DATASET.exists():

            raise FileNotFoundError(
                "Logistics dataset not found:\n"
                f"{LOGISTICS_DATASET}"
            )

        self.logistics_df = pd.read_csv(
            LOGISTICS_DATASET
        )

        print(
            f"✓ logistics_features.csv "
            f"({len(self.logistics_df):,} rows, "
            f"{len(self.logistics_df.columns)} columns)"
        )

        # --------------------------------------------------------------
        # Models
        # --------------------------------------------------------------

        if not TRANSPORT_MODEL.exists():

            raise FileNotFoundError(
                "Transport Cost model not found:\n"
                f"{TRANSPORT_MODEL}"
            )

        if not DELAY_MODEL.exists():

            raise FileNotFoundError(
                "Delay Hours model not found:\n"
                f"{DELAY_MODEL}"
            )

        if not DAMAGE_MODEL.exists():

            raise FileNotFoundError(
                "Damage Percentage model not found:\n"
                f"{DAMAGE_MODEL}"
            )

        self.transport_model = joblib.load(
            TRANSPORT_MODEL
        )

        print(
            "✓ transport_cost_model.joblib"
        )

        self.delay_model = joblib.load(
            DELAY_MODEL
        )

        print(
            "✓ delay_hours_model.joblib"
        )

        self.damage_model = joblib.load(
            DAMAGE_MODEL
        )

        print(
            "✓ damage_percentage_model.joblib"
        )

        # --------------------------------------------------------------
        # Feature names
        # --------------------------------------------------------------

        self.transport_features = (
            self.get_model_features(
                self.transport_model
            )
        )

        self.delay_features = (
            self.get_model_features(
                self.delay_model
            )
        )

        self.damage_features = (
            self.get_model_features(
                self.damage_model
            )
        )

        print()

        if self.transport_features:

            print(
                f"✓ Transport model features: "
                f"{len(self.transport_features)}"
            )

        if self.delay_features:

            print(
                f"✓ Delay model features: "
                f"{len(self.delay_features)}"
            )

        if self.damage_features:

            print(
                f"✓ Damage model features: "
                f"{len(self.damage_features)}"
            )

    # ==================================================================
    # PREPARE MODEL INPUT
    # ==================================================================

    def prepare_features(
        self,
        record: pd.Series,
        feature_names: Optional[List[str]],
    ) -> pd.DataFrame:

        row = pd.DataFrame(
            [record.to_dict()]
        )

        if feature_names:

            missing = [

                feature

                for feature in feature_names

                if feature not in row.columns

            ]

            if missing:

                raise ValueError(
                    "Logistics record is missing "
                    f"required features: {missing}"
                )

            return row[
                feature_names
            ]

        return row

    # ==================================================================
    # PREDICT
    # ==================================================================

    def predict(
        self,
        model,
        record: pd.Series,
        feature_names: Optional[List[str]],
    ):

        X = self.prepare_features(
            record,
            feature_names,
        )

        prediction = model.predict(
            X
        )

        if len(prediction) == 0:

            raise RuntimeError(
                "Existing Logistics model returned "
                "no prediction."
            )

        value = self.number(
            prediction[0],
            np.nan,
        )

        if not np.isfinite(value):

            raise RuntimeError(
                "Existing Logistics model returned "
                "an invalid prediction."
            )

        return value

    # ==================================================================
    # FIND CANDIDATE MARKET / ROUTE COLUMNS
    # ==================================================================

    def get_location_columns(self):

        df = self.logistics_df

        origin_column = self.find_column(

            df,

            [
                "origin_district",
                "origin",
                "source",
                "source_district",
                "from_district",
                "origin_location",
            ],

        )

        destination_column = self.find_column(

            df,

            [
                "destination_market",
                "destination",
                "market",
                "market_name",
                "destination_district",
                "to_market",
                "destination_location",
            ],

        )

        return (
            origin_column,
            destination_column,
        )

    # ==================================================================
    # CREATE CONTEXT RECORD
    # ==================================================================

    def build_context_record(
        self,
        row: pd.Series,
        quantity_kg: float,
        origin_district: Optional[str] = None,
        destination_market: Optional[str] = None,
    ) -> pd.Series:

        record = row.copy()

        # --------------------------------------------------------------
        # Override contextual fields where they exist.
        # --------------------------------------------------------------

        for column in (
            "quantity_kg",
            "quantity",
            "load_quantity_kg",
        ):

            if column in record.index:

                record[column] = (
                    quantity_kg
                )

        if origin_district:

            for column in (
                "origin_district",
                "origin",
                "source",
                "source_district",
                "from_district",
            ):

                if column in record.index:

                    record[column] = (
                        origin_district
                    )

        if destination_market:

            for column in (
                "destination_market",
                "destination",
                "market",
                "market_name",
                "to_market",
            ):

                if column in record.index:

                    record[column] = (
                        destination_market
                    )

        return record

    # ==================================================================
    # CALCULATE LOGISTICS RISK
    # ==================================================================

    @staticmethod
    def calculate_logistics_risk(
        delay_hours: float,
        damage_percentage: float,
    ) -> float:

        """
        Logistics risk:

            Delay contribution  : 40%
            Damage contribution : 60%

        Delay is normalized against 24 hours.
        Damage is normalized against 10%.

        Both are capped at 100.
        """

        delay_score = (

            max(
                0.0,
                min(
                    100.0,
                    delay_hours
                    / 24.0
                    * 100.0,
                ),
            )

        )

        damage_score = (

            max(
                0.0,
                min(
                    100.0,
                    damage_percentage
                    / 10.0
                    * 100.0,
                ),
            )

        )

        risk = (

            delay_score * 0.40

            + damage_score * 0.60

        )

        return max(
            0.0,
            min(
                100.0,
                risk,
            ),
        )

    # ==================================================================
    # LOGISTICS SCORE
    # ==================================================================

    @staticmethod
    def calculate_logistics_score(
        transport_cost: float,
        delay_hours: float,
        damage_percentage: float,
        risk: float,
    ) -> float:

        """
        Lower logistics cost, delay, damage and risk are better.

        Cost is normalized relative to the candidate set later.
        This method receives normalized cost score.
        """

        cost_score = (
            transport_cost
        )

        return max(
            0.0,
            min(
                100.0,

                cost_score * 0.40

                + (
                    100.0
                    - min(
                        100.0,
                        delay_hours
                        / 24.0
                        * 100.0,
                    )
                ) * 0.20

                + (
                    100.0
                    - min(
                        100.0,
                        damage_percentage
                        / 10.0
                        * 100.0,
                    )
                ) * 0.20

                + (
                    100.0
                    - risk
                ) * 0.20

            ),
        )

    # ==================================================================
    # EVALUATE CANDIDATE
    # ==================================================================

    def evaluate_candidate(
        self,
        row: pd.Series,
        quantity_kg: float,
        origin_district: Optional[str],
        destination_market: Optional[str],
    ) -> Dict[str, Any]:

        record = self.build_context_record(

            row,

            quantity_kg,

            origin_district,

            destination_market,

        )

        # --------------------------------------------------------------
        # Transport Cost
        # --------------------------------------------------------------

        transport_cost = self.predict(

            self.transport_model,

            record,

            self.transport_features,

        )

        # --------------------------------------------------------------
        # Delay
        # --------------------------------------------------------------

        delay_hours = self.predict(

            self.delay_model,

            record,

            self.delay_features,

        )

        # --------------------------------------------------------------
        # Damage
        # --------------------------------------------------------------

        damage_percentage = self.predict(

            self.damage_model,

            record,

            self.damage_features,

        )

        # --------------------------------------------------------------
        # Safety bounds
        # --------------------------------------------------------------

        transport_cost = max(
            0.0,
            transport_cost,
        )

        delay_hours = max(
            0.0,
            delay_hours,
        )

        damage_percentage = max(
            0.0,
            damage_percentage,
        )

        # --------------------------------------------------------------
        # Risk
        # --------------------------------------------------------------

        logistics_risk = (
            self.calculate_logistics_risk(

                delay_hours,

                damage_percentage,

            )
        )

        return {

            "origin_district":
                origin_district,

            "destination_market":
                destination_market,

            "quantity_kg":
                quantity_kg,

            "transport_cost":
                transport_cost,

            "delay_hours":
                delay_hours,

            "damage_percentage":
                damage_percentage,

            "logistics_risk":
                logistics_risk,

        }

    # ==================================================================
    # OPTIMIZE
    # ==================================================================

    def optimize(
        self,
        quantity_kg: float,
        origin_district: Optional[str] = None,
        candidate_markets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        print()
        print("=" * 70)
        print("RUNNING LOGISTICS OPTIMIZATION")
        print("=" * 70)

        quantity_kg = max(
            0.0,
            self.number(
                quantity_kg
            ),
        )

        if quantity_kg <= 0:

            raise ValueError(
                "Quantity must be greater than zero."
            )

        origin_column, destination_column = (
            self.get_location_columns()
        )

        print()

        if origin_column:

            print(
                f"✓ Origin column      : "
                f"{origin_column}"
            )

        if destination_column:

            print(
                f"✓ Destination column : "
                f"{destination_column}"
            )

        df = self.logistics_df.copy()

        # --------------------------------------------------------------
        # Candidate selection
        # --------------------------------------------------------------

        if candidate_markets:

            if destination_column:

                requested = {
                    str(x).strip().lower()
                    for x in candidate_markets
                }

                mask = (

                    df[destination_column]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(requested)

                )

                candidates_df = df[
                    mask
                ].copy()

            else:

                candidates_df = df.copy()

        else:

            candidates_df = df.copy()

        # --------------------------------------------------------------
        # If origin exists, prefer matching origin.
        # If no matching rows exist, don't fabricate anything.
        # --------------------------------------------------------------

        if (
            origin_district
            and
            origin_column
        ):

            origin_mask = (

                candidates_df[
                    origin_column
                ]
                .astype(str)
                .str.strip()
                .str.lower()
                ==
                str(
                    origin_district
                )
                .strip()
                .lower()

            )

            origin_candidates = (
                candidates_df[
                    origin_mask
                ].copy()
            )

            if len(origin_candidates) > 0:

                candidates_df = (
                    origin_candidates
                )

        if len(candidates_df) == 0:

            raise RuntimeError(
                "No existing Logistics candidate "
                "records available."
            )

        # --------------------------------------------------------------
        # Limit duplicate locations.
        # --------------------------------------------------------------

        if destination_column:

            candidates_df = (
                candidates_df
                .drop_duplicates(
                    subset=[
                        destination_column
                    ]
                )
            )

        # --------------------------------------------------------------
        # Evaluate candidates
        # --------------------------------------------------------------

        evaluated = []

        print()
        print(
            f"✓ Candidate logistics options: "
            f"{len(candidates_df)}"
        )

        for _, row in candidates_df.iterrows():

            destination = None

            if destination_column:

                destination = str(
                    row[
                        destination_column
                    ]
                )

            origin = origin_district

            if origin is None and origin_column:

                origin = str(
                    row[
                        origin_column
                    ]
                )

            try:

                result = (
                    self.evaluate_candidate(

                        row,

                        quantity_kg,

                        origin,

                        destination,

                    )
                )

                evaluated.append(
                    result
                )

            except Exception:
                # Skip records that cannot be evaluated
                # by the existing model schema.
                continue

        if not evaluated:

            raise RuntimeError(
                "No Logistics candidate could be "
                "evaluated using the existing models."
            )

        # --------------------------------------------------------------
        # Cost normalization
        # --------------------------------------------------------------

        costs = np.array([

            item[
                "transport_cost"
            ]

            for item in evaluated

        ])

        min_cost = float(
            costs.min()
        )

        max_cost = float(
            costs.max()
        )

        cost_range = (
            max_cost
            - min_cost
        )

        for item in evaluated:

            if cost_range > 0:

                # Lower cost = higher score.
                cost_score = (

                    (
                        max_cost
                        - item[
                            "transport_cost"
                        ]
                    )
                    / cost_range
                    * 100.0

                )

            else:

                cost_score = 100.0

            item[
                "cost_score"
            ] = cost_score

            item[
                "logistics_score"
            ] = (

                cost_score * 0.40

                + (
                    100.0
                    - min(
                        100.0,
                        item[
                            "delay_hours"
                        ]
                        / 24.0
                        * 100.0,
                    )
                ) * 0.20

                + (
                    100.0
                    - min(
                        100.0,
                        item[
                            "damage_percentage"
                        ]
                        / 10.0
                        * 100.0,
                    )
                ) * 0.20

                + (
                    100.0
                    - item[
                        "logistics_risk"
                    ]
                ) * 0.20

            )

            item[
                "cost_score"
            ] = round(
                item[
                    "cost_score"
                ],
                2,
            )

            item[
                "logistics_score"
            ] = round(
                item[
                    "logistics_score"
                ],
                2,
            )

            item[
                "transport_cost"
            ] = round(
                item[
                    "transport_cost"
                ],
                2,
            )

            item[
                "delay_hours"
            ] = round(
                item[
                    "delay_hours"
                ],
                2,
            )

            item[
                "damage_percentage"
            ] = round(
                item[
                    "damage_percentage"
                ],
                2,
            )

            item[
                "logistics_risk"
            ] = round(
                item[
                    "logistics_risk"
                ],
                2,
            )

        # --------------------------------------------------------------
        # Rank
        # --------------------------------------------------------------

        evaluated.sort(

            key=lambda item: (

                item[
                    "logistics_score"
                ],

                -item[
                    "logistics_risk"
                ],

                -item[
                    "transport_cost"
                ],

            ),

            reverse=True,

        )

        for rank, item in enumerate(

            evaluated,

            start=1,

        ):

            item[
                "logistics_rank"
            ] = rank

        recommended = (
            evaluated[0]
        )

        # --------------------------------------------------------------
        # Display
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("LOGISTICS OPTIMIZATION RANKING")
        print("=" * 70)

        for item in evaluated[:10]:

            print()
            print(
                f"#{item['logistics_rank']} "
                f"{item.get('destination_market', 'Unknown')}"
            )

            print(
                f"  Transport Cost     : "
                f"₹{item['transport_cost']:,.2f}"
            )

            print(
                f"  Delay              : "
                f"{item['delay_hours']:.2f} hours"
            )

            print(
                f"  Damage             : "
                f"{item['damage_percentage']:.2f}%"
            )

            print(
                f"  Logistics Risk     : "
                f"{item['logistics_risk']:.2f}/100"
            )

            print(
                f"  Logistics Score    : "
                f"{item['logistics_score']:.2f}/100"
            )

        # --------------------------------------------------------------
        # Recommendation
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("BEST LOGISTICS OPTION")
        print("=" * 70)

        print(
            f"✓ Origin             : "
            f"{recommended.get('origin_district')}"
        )

        print(
            f"✓ Destination        : "
            f"{recommended.get('destination_market')}"
        )

        print(
            f"✓ Transport Cost     : "
            f"₹{recommended['transport_cost']:,.2f}"
        )

        print(
            f"✓ Delay              : "
            f"{recommended['delay_hours']:.2f} hours"
        )

        print(
            f"✓ Damage             : "
            f"{recommended['damage_percentage']:.2f}%"
        )

        print(
            f"✓ Logistics Risk     : "
            f"{recommended['logistics_risk']:.2f}/100"
        )

        print(
            f"✓ Logistics Score    : "
            f"{recommended['logistics_score']:.2f}/100"
        )

        return {

            "status":
                "COMPLETED",

            "recommended_option":
                recommended,

            "best_market":
                recommended[
                    "destination_market"
                ],

            "transport_cost":
                recommended[
                    "transport_cost"
                ],

            "delay_hours":
                recommended[
                    "delay_hours"
                ],

            "damage_percentage":
                recommended[
                    "damage_percentage"
                ],

            "logistics_risk":
                recommended[
                    "logistics_risk"
                ],

            "logistics_score":
                recommended[
                    "logistics_score"
                ],

            "evaluated_options":
                evaluated,

            "candidate_count":
                len(evaluated),

            "models_verified":
                True,

        }


# ======================================================================
# TEST
# ======================================================================

def main():

    print()
    print("=" * 70)
    print("LOGISTICS OPTIMIZATION TEST")
    print("=" * 70)

    try:

        # ==============================================================
        # ENGINE
        # ==============================================================

        engine = (
            LogisticsOptimizationEngine()
        )

        # ==============================================================
        # CURRENT TRANSACTION
        # ==============================================================

        quantity_kg = 887.0

        origin_district = (
            "Kheda"
        )

        # --------------------------------------------------------------
        # Use existing logistics dataset candidates.
        # No market is fabricated.
        # --------------------------------------------------------------

        result = (
            engine.optimize(

                quantity_kg=
                quantity_kg,

                origin_district=
                origin_district,

            )
        )

        # ==============================================================
        # FINAL STATUS
        # ==============================================================

        print()
        print("=" * 70)
        print("LOGISTICS OPTIMIZATION FINAL STATUS")
        print("=" * 70)

        winner = (
            result[
                "recommended_option"
            ]
        )

        print(
            "✓ LOGISTICS OPTIMIZATION COMPLETED"
        )

        print(
            f"✓ Best Destination : "
            f"{winner.get('destination_market')}"
        )

        print(
            f"✓ Transport Cost   : "
            f"₹{winner['transport_cost']:,.2f}"
        )

        print(
            f"✓ Delay            : "
            f"{winner['delay_hours']:.2f} hours"
        )

        print(
            f"✓ Damage           : "
            f"{winner['damage_percentage']:.2f}%"
        )

        print(
            f"✓ Logistics Risk   : "
            f"{winner['logistics_risk']:.2f}/100"
        )

        print(
            f"✓ Logistics Score  : "
            f"{winner['logistics_score']:.2f}/100"
        )

        print()
        print(
            "✓ Existing Transport Cost model used"
        )

        print(
            "✓ Existing Delay Hours model used"
        )

        print(
            "✓ Existing Damage Percentage model used"
        )

        print(
            "✓ Existing logistics_features.csv used"
        )

        print(
            "✓ No new ML model"
        )

        print(
            "✓ No new dataset"
        )

        print(
            "✓ No dataset modification"
        )

        print(
            "✓ No AI Agent"
        )

    except Exception as exc:

        print()
        print("=" * 70)
        print("✗ LOGISTICS OPTIMIZATION TEST FAILED")
        print("=" * 70)

        print(
            f"{type(exc).__name__}: {exc}"
        )

        raise


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()