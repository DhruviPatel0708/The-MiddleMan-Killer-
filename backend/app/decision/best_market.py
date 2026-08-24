"""
BEST MARKET RECOMMENDATION ENGINE

Memory-efficient version.

Purpose:
    Find and rank the best markets for a selected crop.

Uses:
    - price_features.csv
    - demand_features.csv
    - trained price model
    - trained demand model

No model retraining.
No fake predictions.
No full dataset printing.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ======================================================================
# PATHS
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "ml"
    / "saved_models"
)

PRICE_DATASET = PROCESSED_DIR / "price_features.csv"
DEMAND_DATASET = PROCESSED_DIR / "demand_features.csv"

PRICE_MODEL = MODEL_DIR / "price_model.joblib"
DEMAND_MODEL = MODEL_DIR / "demand_model.joblib"


# ======================================================================
# REQUIRED FEATURES
# ======================================================================

PRICE_FEATURES = [
    "district",
    "market",
    "crop",
    "variety",
    "min_price_per_quintal",
    "max_price_per_quintal",
    "modal_price_per_quintal",
    "arrival_quantity_tonnes",
    "price_lag_1",
    "price_lag_3",
    "price_lag_7",
    "price_lag_14",
    "price_lag_30",
    "rolling_mean_7",
    "rolling_std_7",
    "rolling_mean_14",
    "rolling_std_14",
    "rolling_mean_30",
    "rolling_std_30",
    "price_change_1d_pct",
    "price_change_7d_pct",
    "price_change_30d_pct",
    "price_volatility_30d",
    "price_trend",
    "year",
    "month",
    "day",
    "day_of_week",
    "day_of_year",
    "week_of_year",
    "is_weekend",
    "price_range",
    "price_range_percentage",
    "modal_price_position",
    "price_per_arrival",
]


DEMAND_FEATURES = [
    "district",
    "market",
    "crop",
    "arrival_quantity_tonnes",
    "estimated_demand_tonnes",
    "demand_supply_ratio",
    "demand_index",
    "market_pressure",
    "demand_lag_1",
    "demand_lag_7",
    "arrival_lag_1",
    "arrival_lag_7",
    "arrival_change_1d_pct",
    "arrival_change_7d_pct",
    "demand_change_7d_pct",
    "current_demand_tonnes",
    "demand_rolling_mean_3",
    "demand_rolling_mean_7",
    "demand_rolling_std_7",
    "demand_rolling_mean_14",
    "year",
    "month",
    "day",
    "day_of_week",
    "day_of_year",
    "week_of_year",
    "is_weekend",
    "demand_minus_arrival",
    "demand_to_arrival_ratio",
    "demand_lag_difference",
    "arrival_lag_difference",
    "demand_change_1d_pct",
    "demand_pressure_score",
]


# ======================================================================
# HELPERS
# ======================================================================

def safe_float(value, default=0.0):

    try:

        value = float(value)

        if np.isfinite(value):
            return value

        return default

    except (TypeError, ValueError):

        return default


def normalize(values):

    values = np.asarray(
        values,
        dtype=float
    )

    if len(values) == 0:
        return values

    minimum = np.min(values)
    maximum = np.max(values)

    if maximum - minimum <= 1e-12:

        return np.ones(
            len(values)
        ) * 50.0

    return (
        (values - minimum)
        /
        (maximum - minimum)
        * 100.0
    )


# ======================================================================
# BEST MARKET OPTIMIZER
# ======================================================================

class BestMarketOptimizer:

    def __init__(self):

        print("\n")
        print("=" * 70)
        print("BEST MARKET OPTIMIZER")
        print("=" * 70)

        # --------------------------------------------------------------
        # File validation
        # --------------------------------------------------------------

        required_files = [
            PRICE_DATASET,
            DEMAND_DATASET,
            PRICE_MODEL,
            DEMAND_MODEL,
        ]

        for file_path in required_files:

            if not file_path.exists():

                raise FileNotFoundError(
                    f"Required file not found:\n{file_path}"
                )

        # --------------------------------------------------------------
        # Load models
        # --------------------------------------------------------------

        print("\nLoading trained models...")

        self.price_model = joblib.load(
            PRICE_MODEL
        )

        self.demand_model = joblib.load(
            DEMAND_MODEL
        )

        print("✓ Price model loaded")
        print("✓ Demand model loaded")

        # --------------------------------------------------------------
        # DO NOT load datasets here
        #
        # This saves memory.
        # --------------------------------------------------------------

        self.price_df = None
        self.demand_df = None

        print(
            "\n✓ Memory-efficient optimizer initialized."
        )

    # ==================================================================
    # LOAD PRICE DATA
    # ==================================================================

    def _load_price_data(self, crop):

        columns = list(
            dict.fromkeys(
                PRICE_FEATURES + ["date"]
            )
        )

        print("\nLoading price data...")

        df = pd.read_csv(
            PRICE_DATASET,
            usecols=columns,
            low_memory=True
        )

        print(
            f"✓ Price data loaded: "
            f"{len(df):,} rows"
        )

        # --------------------------------------------------------------
        # Crop filtering immediately
        # --------------------------------------------------------------

        df = df[
            df["crop"]
            .astype(str)
            .str.lower()
            ==
            str(crop).strip().lower()
        ].copy()

        print(
            f"✓ Rows for crop '{crop}': "
            f"{len(df):,}"
        )

        if df.empty:

            raise ValueError(
                f"No price data found for crop: {crop}"
            )

        # --------------------------------------------------------------
        # Date conversion
        # --------------------------------------------------------------

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

            df = df.sort_values(
                "date"
            )

        # --------------------------------------------------------------
        # Latest row per market
        # --------------------------------------------------------------

        df = (
            df
            .drop_duplicates(
                subset=[
                    "district",
                    "market"
                ],
                keep="last"
            )
            .reset_index(drop=True)
        )

        print(
            f"✓ Unique current markets: "
            f"{len(df):,}"
        )

        return df

    # ==================================================================
    # LOAD DEMAND DATA
    # ==================================================================

    def _load_demand_data(
        self,
        crop,
        markets
    ):

        columns = list(
            dict.fromkeys(
                DEMAND_FEATURES + ["date"]
            )
        )

        print("\nLoading demand data...")

        df = pd.read_csv(
            DEMAND_DATASET,
            usecols=columns,
            low_memory=True
        )

        print(
            f"✓ Demand data loaded: "
            f"{len(df):,} rows"
        )

        # --------------------------------------------------------------
        # Crop filtering
        # --------------------------------------------------------------

        df = df[
            df["crop"]
            .astype(str)
            .str.lower()
            ==
            str(crop).strip().lower()
        ].copy()

        # --------------------------------------------------------------
        # Keep only candidate markets
        # --------------------------------------------------------------

        market_pairs = set(
            zip(
                markets["district"].astype(str),
                markets["market"].astype(str)
            )
        )

        df["_market_key"] = list(
            zip(
                df["district"].astype(str),
                df["market"].astype(str)
            )
        )

        df = df[
            df["_market_key"].isin(
                market_pairs
            )
        ].copy()

        df.drop(
            columns=["_market_key"],
            inplace=True
        )

        if df.empty:

            print(
                "⚠ No matching demand rows found."
            )

            return df

        # --------------------------------------------------------------
        # Date
        # --------------------------------------------------------------

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

            df = df.sort_values(
                "date"
            )

        # --------------------------------------------------------------
        # Latest demand row per market
        # --------------------------------------------------------------

        df = (
            df
            .drop_duplicates(
                subset=[
                    "district",
                    "market"
                ],
                keep="last"
            )
            .reset_index(drop=True)
        )

        print(
            f"✓ Current demand markets: "
            f"{len(df):,}"
        )

        return df

    # ==================================================================
    # PREDICT PRICE
    # ==================================================================

    def _predict_prices(
        self,
        price_df
    ):

        X = price_df[
            PRICE_FEATURES
        ].copy()

        predictions = (
            self.price_model.predict(X)
        )

        return np.asarray(
            predictions,
            dtype=float
        )

    # ==================================================================
    # PREDICT DEMAND
    # ==================================================================

    def _predict_demands(
        self,
        demand_df
    ):

        if demand_df.empty:

            return np.zeros(0)

        X = demand_df[
            DEMAND_FEATURES
        ].copy()

        predictions = (
            self.demand_model.predict(X)
        )

        return np.asarray(
            predictions,
            dtype=float
        )

    # ==================================================================
    # RECOMMEND MARKET
    # ==================================================================

    def recommend(
        self,
        crop,
        district=None,
        top_n=5
    ):

        print("\n")
        print("=" * 70)
        print("BEST MARKET RECOMMENDATION")
        print("=" * 70)

        # --------------------------------------------------------------
        # Validate crop
        # --------------------------------------------------------------

        if not crop:

            raise ValueError(
                "Crop is required."
            )

        if (
            str(crop)
            .strip()
            .upper()
            ==
            "UNKNOWN"
        ):

            raise ValueError(
                "Valid crop is required."
            )

        # --------------------------------------------------------------
        # Load price data
        # --------------------------------------------------------------

        price_df = self._load_price_data(
            crop
        )

        # --------------------------------------------------------------
        # Optional district filtering
        # --------------------------------------------------------------

        if district:

            district_df = price_df[
                price_df["district"]
                .astype(str)
                .str.lower()
                ==
                str(district)
                .strip()
                .lower()
            ].copy()

            if not district_df.empty:

                price_df = district_df

                print(
                    f"✓ District filter applied: "
                    f"{district}"
                )

        # --------------------------------------------------------------
        # Limit candidates
        #
        # We don't need hundreds of markets.
        # Keep a reasonable number for decision making.
        # --------------------------------------------------------------

        MAX_CANDIDATES = 30

        if len(price_df) > MAX_CANDIDATES:

            price_df = (
                price_df
                .sort_values(
                    "modal_price_per_quintal",
                    ascending=False
                )
                .head(MAX_CANDIDATES)
                .reset_index(drop=True)
            )

        print(
            f"\nMarkets evaluated: "
            f"{len(price_df)}"
        )

        # --------------------------------------------------------------
        # PRICE PREDICTION
        #
        # Batch prediction = much faster.
        # --------------------------------------------------------------

        print(
            "\nGenerating price predictions..."
        )

        price_predictions = (
            self._predict_prices(
                price_df
            )
        )

        print(
            "✓ Price predictions completed"
        )

        price_df[
            "predicted_price_per_quintal"
        ] = price_predictions

        # --------------------------------------------------------------
        # DEMAND DATA
        # --------------------------------------------------------------

        demand_df = self._load_demand_data(
            crop=crop,
            markets=price_df
        )

        # --------------------------------------------------------------
        # DEMAND PREDICTION
        # --------------------------------------------------------------

        if not demand_df.empty:

            print(
                "\nGenerating demand predictions..."
            )

            demand_predictions = (
                self._predict_demands(
                    demand_df
                )
            )

            demand_df[
                "predicted_demand_tonnes"
            ] = demand_predictions

            print(
                "✓ Demand predictions completed"
            )

        else:

            demand_df[
                "predicted_demand_tonnes"
            ] = []

        # --------------------------------------------------------------
        # Merge price + demand
        # --------------------------------------------------------------

        demand_columns = [
            "district",
            "market",
            "predicted_demand_tonnes",
        ]

        result = price_df.merge(
            demand_df[
                demand_columns
            ],
            on=[
                "district",
                "market"
            ],
            how="left"
        )

        result[
            "predicted_demand_tonnes"
        ] = result[
            "predicted_demand_tonnes"
        ].fillna(0.0)

        # --------------------------------------------------------------
        # Normalize
        # --------------------------------------------------------------

        price_score = normalize(
            result[
                "predicted_price_per_quintal"
            ].values
        )

        demand_score = normalize(
            result[
                "predicted_demand_tonnes"
            ].values
        )

        # --------------------------------------------------------------
        # Market score
        #
        # Price = 60%
        # Demand = 40%
        # --------------------------------------------------------------

        result[
            "market_score"
        ] = (

            0.60 * price_score
            +
            0.40 * demand_score

        )

        # --------------------------------------------------------------
        # Rank
        # --------------------------------------------------------------

        result = (
            result
            .sort_values(
                "market_score",
                ascending=False
            )
            .reset_index(drop=True)
        )

        result[
            "rank"
        ] = result.index + 1

        # --------------------------------------------------------------
        # Top markets
        # --------------------------------------------------------------

        top_markets = result.head(
            top_n
        ).copy()

        # --------------------------------------------------------------
        # PRINT ONLY TOP RESULTS
        # --------------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("TOP MARKET RECOMMENDATIONS")
        print("=" * 70)

        for _, row in top_markets.iterrows():

            print(
                f"\n#{int(row['rank'])} "
                f"{row['market']}"
            )

            print(
                f"  District : "
                f"{row['district']}"
            )

            print(
                f"  Price    : "
                f"₹{row['predicted_price_per_quintal']:,.2f}/quintal"
            )

            print(
                f"  Demand   : "
                f"{row['predicted_demand_tonnes']:,.2f} tonnes"
            )

            print(
                f"  Score    : "
                f"{row['market_score']:.2f}/100"
            )

        # --------------------------------------------------------------
        # BEST MARKET
        # --------------------------------------------------------------

        best = top_markets.iloc[0]

        print("\n")
        print("=" * 70)
        print("BEST MARKET")
        print("=" * 70)

        print(
            f"\n✓ Market : "
            f"{best['market']}"
        )

        print(
            f"✓ District : "
            f"{best['district']}"
        )

        print(
            f"✓ Predicted price : "
            f"₹{best['predicted_price_per_quintal']:,.2f}/quintal"
        )

        print(
            f"✓ Predicted demand : "
            f"{best['predicted_demand_tonnes']:,.2f} tonnes"
        )

        print(
            f"✓ Market score : "
            f"{best['market_score']:.2f}/100"
        )

        return {
            "best_market":
                best["market"],

            "best_district":
                best["district"],

            "predicted_price_per_quintal":
                safe_float(
                    best[
                        "predicted_price_per_quintal"
                    ]
                ),

            "predicted_demand_tonnes":
                safe_float(
                    best[
                        "predicted_demand_tonnes"
                    ]
                ),

            "market_score":
                safe_float(
                    best[
                        "market_score"
                    ]
                ),

            "ranked_markets":
                top_markets[
                    [
                        "rank",
                        "district",
                        "market",
                        "predicted_price_per_quintal",
                        "predicted_demand_tonnes",
                        "market_score",
                    ]
                ].to_dict(
                    orient="records"
                ),
        }


# ======================================================================
# TEST
# ======================================================================

def main():

    print("\n")
    print("=" * 70)
    print("BEST MARKET OPTIMIZER TEST")
    print("=" * 70)

    optimizer = BestMarketOptimizer()

    # --------------------------------------------------------------
    # Select a real crop from the dataset.
    #
    # Only reads the crop column here.
    # --------------------------------------------------------------

    crop_df = pd.read_csv(
        PRICE_DATASET,
        usecols=["crop"],
        low_memory=True
    )

    crop_df = crop_df.dropna()

    if crop_df.empty:

        raise RuntimeError(
            "No crops found in price dataset."
        )

    crop = str(
        crop_df.iloc[0]["crop"]
    )

    del crop_df

    print(
        f"\n✓ Test crop selected: {crop}"
    )

    # --------------------------------------------------------------
    # Run recommendation
    # --------------------------------------------------------------

    result = optimizer.recommend(
        crop=crop,
        top_n=5
    )

    # --------------------------------------------------------------
    # Final status
    # --------------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("BEST MARKET TEST COMPLETED")
    print("=" * 70)

    print(
        f"\n✓ Best market : "
        f"{result['best_market']}"
    )

    print(
        f"✓ Score : "
        f"{result['market_score']:.2f}/100"
    )

    print(
        f"✓ Markets returned : "
        f"{len(result['ranked_markets'])}"
    )

    print(
        "\n✓ Real market data used."
    )

    print(
        "✓ Real demand data used."
    )

    print(
        "✓ Existing trained models used."
    )

    print(
        "✓ Batch predictions used."
    )

    print(
        "✓ Memory-efficient processing used."
    )

    print(
        "✓ No model retraining."
    )

    print(
        "✓ No fake predictions."
    )


# ======================================================================
# RUN
# ======================================================================

if __name__ == "__main__":

    main()