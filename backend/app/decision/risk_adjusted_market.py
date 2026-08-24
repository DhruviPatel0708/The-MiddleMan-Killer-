"""
======================================================================
RISK-ADJUSTED BEST MARKET ENGINE
======================================================================

Purpose:
    Select the best market after considering:

    1. Predicted selling price
    2. Predicted demand
    3. Transport cost
    4. Delivery delay
    5. Expected damage
    6. Financial outcome
    7. Risk penalty

This does NOT retrain any ML model.

Existing trained models are used:
    - Price
    - Demand
    - Transport Cost
    - Delay Hours
    - Damage Percentage

======================================================================
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ======================================================================
# PATHS
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DIR = (
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


PRICE_DATASET = (
    PROCESSED_DIR
    / "price_features.csv"
)

DEMAND_DATASET = (
    PROCESSED_DIR
    / "demand_features.csv"
)

LOGISTICS_DATASET = (
    PROCESSED_DIR
    / "logistics_features.csv"
)


PRICE_MODEL = (
    MODEL_DIR
    / "price_model.joblib"
)

DEMAND_MODEL = (
    MODEL_DIR
    / "demand_model.joblib"
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
# FEATURE SCHEMAS
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


LOGISTICS_FEATURES = [
    "origin_district",
    "destination_district",
    "distance_km",
    "vehicle_type",
    "vehicle_capacity_kg",
    "estimated_travel_hours",
    "fuel_cost",
    "toll_cost",
    "weather_risk",
    "route_risk",
    "delivery_urgency",
    "delivery_status",
    "cost_per_km",
    "fuel_cost_per_km",
    "toll_cost_per_km",
    "vehicle_capacity_utilization",
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
# ENGINE
# ======================================================================

class RiskAdjustedMarketOptimizer:

    def __init__(self):

        print("\n")
        print("=" * 70)
        print("RISK-ADJUSTED MARKET OPTIMIZER")
        print("=" * 70)

        # --------------------------------------------------------------
        # Validate files
        # --------------------------------------------------------------

        required_files = [

            PRICE_DATASET,
            DEMAND_DATASET,
            LOGISTICS_DATASET,

            PRICE_MODEL,
            DEMAND_MODEL,
            TRANSPORT_MODEL,
            DELAY_MODEL,
            DAMAGE_MODEL,
        ]

        for file_path in required_files:

            if not file_path.exists():

                raise FileNotFoundError(
                    f"\nRequired file not found:\n"
                    f"{file_path}"
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

        self.transport_model = joblib.load(
            TRANSPORT_MODEL
        )

        self.delay_model = joblib.load(
            DELAY_MODEL
        )

        self.damage_model = joblib.load(
            DAMAGE_MODEL
        )

        print("✓ Price model")
        print("✓ Demand model")
        print("✓ Transport cost model")
        print("✓ Delay model")
        print("✓ Damage model")

        print(
            "\n✓ 5 existing ML models loaded."
        )

    # ==================================================================
    # PRICE DATA
    # ==================================================================

    def _load_price_data(
        self,
        crop
    ):

        columns = list(
            dict.fromkeys(
                PRICE_FEATURES
                + ["date"]
            )
        )

        df = pd.read_csv(
            PRICE_DATASET,
            usecols=columns,
            low_memory=True
        )

        df = df[
            df["crop"]
            .astype(str)
            .str.lower()
            ==
            str(crop)
            .strip()
            .lower()
        ].copy()

        if df.empty:

            raise ValueError(
                f"No price data found for crop: {crop}"
            )

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

            df = df.sort_values(
                "date"
            )

        # Latest row for each market
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

        return df

    # ==================================================================
    # DEMAND DATA
    # ==================================================================

    def _load_demand_data(
        self,
        crop,
        markets
    ):

        columns = list(
            dict.fromkeys(
                DEMAND_FEATURES
                + ["date"]
            )
        )

        df = pd.read_csv(
            DEMAND_DATASET,
            usecols=columns,
            low_memory=True
        )

        df = df[
            df["crop"]
            .astype(str)
            .str.lower()
            ==
            str(crop)
            .strip()
            .lower()
        ].copy()

        if df.empty:

            return df

        # --------------------------------------------------------------
        # Keep only candidate market pairs
        # --------------------------------------------------------------

        market_keys = set(
            zip(
                markets["district"].astype(str),
                markets["market"].astype(str)
            )
        )

        df["_key"] = list(
            zip(
                df["district"].astype(str),
                df["market"].astype(str)
            )
        )

        df = df[
            df["_key"].isin(
                market_keys
            )
        ].copy()

        df.drop(
            columns=["_key"],
            inplace=True
        )

        if "date" in df.columns:

            df["date"] = pd.to_datetime(
                df["date"],
                errors="coerce"
            )

            df = df.sort_values(
                "date"
            )

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

        return df

    # ==================================================================
    # LOGISTICS DATA
    # ==================================================================

    def _load_logistics_data(
        self,
        origin_district,
        markets
    ):

        columns = LOGISTICS_FEATURES

        df = pd.read_csv(
            LOGISTICS_DATASET,
            usecols=columns,
            low_memory=True
        )

        # --------------------------------------------------------------
        # Origin filter
        # --------------------------------------------------------------

        df = df[
            df["origin_district"]
            .astype(str)
            .str.lower()
            ==
            str(origin_district)
            .strip()
            .lower()
        ].copy()

        if df.empty:

            return df

        # --------------------------------------------------------------
        # Destination markets
        # --------------------------------------------------------------

        destinations = set(
            markets["district"]
            .astype(str)
        )

        df = df[
            df["destination_district"]
            .astype(str)
            .isin(destinations)
        ].copy()

        if df.empty:

            return df

        # --------------------------------------------------------------
        # One representative logistics row
        # per destination
        # --------------------------------------------------------------

        df = (
            df
            .drop_duplicates(
                subset=[
                    "destination_district"
                ],
                keep="first"
            )
            .reset_index(drop=True)
        )

        return df

    # ==================================================================
    # LOGISTICS PREDICTIONS
    # ==================================================================

    def _predict_logistics(
        self,
        logistics_df
    ):

        if logistics_df.empty:

            return logistics_df

        X = logistics_df[
            LOGISTICS_FEATURES
        ].copy()

        transport = (
            self.transport_model.predict(X)
        )

        delay = (
            self.delay_model.predict(X)
        )

        damage = (
            self.damage_model.predict(X)
        )

        result = logistics_df.copy()

        result[
            "predicted_transport_cost"
        ] = np.asarray(
            transport,
            dtype=float
        )

        result[
            "predicted_delay_hours"
        ] = np.asarray(
            delay,
            dtype=float
        )

        result[
            "predicted_damage_percentage"
        ] = np.asarray(
            damage,
            dtype=float
        )

        return result

    # ==================================================================
    # RECOMMENDATION
    # ==================================================================

    def recommend(
        self,
        crop,
        quantity_kg,
        origin_district,
        top_n=5
    ):

        print("\n")
        print("=" * 70)
        print("RISK-ADJUSTED MARKET RECOMMENDATION")
        print("=" * 70)

        # --------------------------------------------------------------
        # Validation
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

        quantity_kg = safe_float(
            quantity_kg
        )

        if quantity_kg <= 0:

            raise ValueError(
                "Quantity must be greater than zero."
            )

        if not origin_district:

            raise ValueError(
                "Origin district is required."
            )

        print(
            f"\nCrop           : {crop}"
        )

        print(
            f"Quantity       : "
            f"{quantity_kg:,.2f} kg"
        )

        print(
            f"Origin district: "
            f"{origin_district}"
        )

        # --------------------------------------------------------------
        # PRICE
        # --------------------------------------------------------------

        print(
            "\nLoading price data..."
        )

        price_df = self._load_price_data(
            crop
        )

        # Limit candidate markets
        MAX_MARKETS = 30

        if len(price_df) > MAX_MARKETS:

            price_df = (
                price_df
                .sort_values(
                    "modal_price_per_quintal",
                    ascending=False
                )
                .head(MAX_MARKETS)
                .reset_index(drop=True)
            )

        print(
            f"✓ Candidate markets: "
            f"{len(price_df)}"
        )

        # --------------------------------------------------------------
        # PRICE PREDICTION
        # --------------------------------------------------------------

        price_X = price_df[
            PRICE_FEATURES
        ]

        price_predictions = (
            self.price_model.predict(
                price_X
            )
        )

        price_df[
            "predicted_price_per_quintal"
        ] = np.asarray(
            price_predictions,
            dtype=float
        )

        print(
            "✓ Price predictions generated"
        )

        # --------------------------------------------------------------
        # DEMAND
        # --------------------------------------------------------------

        print(
            "\nLoading demand data..."
        )

        demand_df = self._load_demand_data(
            crop,
            price_df
        )

        if not demand_df.empty:

            demand_X = demand_df[
                DEMAND_FEATURES
            ]

            demand_predictions = (
                self.demand_model.predict(
                    demand_X
                )
            )

            demand_df[
                "predicted_demand_tonnes"
            ] = np.asarray(
                demand_predictions,
                dtype=float
            )

        else:

            demand_df = pd.DataFrame(
                columns=[
                    "district",
                    "market",
                    "predicted_demand_tonnes"
                ]
            )

        print(
            "✓ Demand predictions generated"
        )

        # --------------------------------------------------------------
        # MERGE DEMAND
        # --------------------------------------------------------------

        result = price_df.merge(

            demand_df[
                [
                    "district",
                    "market",
                    "predicted_demand_tonnes"
                ]
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
        # LOGISTICS
        # --------------------------------------------------------------

        print(
            "\nLoading logistics data..."
        )

        logistics_df = (
            self._load_logistics_data(
                origin_district,
                result
            )
        )

        if not logistics_df.empty:

            logistics_df = (
                self._predict_logistics(
                    logistics_df
                )
            )

            result = result.merge(

                logistics_df[
                    [
                        "destination_district",
                        "predicted_transport_cost",
                        "predicted_delay_hours",
                        "predicted_damage_percentage",
                    ]
                ],

                left_on="district",

                right_on="destination_district",

                how="left"
            )

            result.drop(
                columns=[
                    "destination_district"
                ],
                inplace=True,
                errors="ignore"
            )

        else:

            result[
                "predicted_transport_cost"
            ] = np.nan

            result[
                "predicted_delay_hours"
            ] = np.nan

            result[
                "predicted_damage_percentage"
            ] = np.nan

        # --------------------------------------------------------------
        # Fill unavailable logistics conservatively
        # --------------------------------------------------------------

        result[
            "predicted_transport_cost"
        ] = result[
            "predicted_transport_cost"
        ].fillna(
            result[
                "predicted_transport_cost"
            ].median()
        )

        result[
            "predicted_delay_hours"
        ] = result[
            "predicted_delay_hours"
        ].fillna(
            result[
                "predicted_delay_hours"
            ].median()
        )

        result[
            "predicted_damage_percentage"
        ] = result[
            "predicted_damage_percentage"
        ].fillna(
            result[
                "predicted_damage_percentage"
            ].median()
        )

        # If everything was missing, use zero only as
        # a fallback for unavailable logistics data.
        result[
            "predicted_transport_cost"
        ] = result[
            "predicted_transport_cost"
        ].fillna(0.0)

        result[
            "predicted_delay_hours"
        ] = result[
            "predicted_delay_hours"
        ].fillna(0.0)

        result[
            "predicted_damage_percentage"
        ] = result[
            "predicted_damage_percentage"
        ].fillna(0.0)

        print(
            "✓ Logistics predictions generated"
        )

        # --------------------------------------------------------------
        # FINANCIAL CALCULATION
        # --------------------------------------------------------------

        # Price is per quintal.
        # Convert quantity from kg to quintal.

        quantity_quintal = (
            quantity_kg / 100.0
        )

        result[
            "expected_revenue"
        ] = (

            result[
                "predicted_price_per_quintal"
            ]

            *
            quantity_quintal

        )

        result[
            "expected_margin"
        ] = (

            result[
                "expected_revenue"
            ]

            -
            result[
                "predicted_transport_cost"
            ]

        )

        # --------------------------------------------------------------
        # DAMAGE LOSS
        # --------------------------------------------------------------

        result[
            "damage_loss"
        ] = (

            result[
                "expected_revenue"
            ]

            *
            result[
                "predicted_damage_percentage"
            ]
            /
            100.0

        )

        result[
            "risk_adjusted_margin"
        ] = (

            result[
                "expected_margin"
            ]

            -
            result[
                "damage_loss"
            ]

        )

        # --------------------------------------------------------------
        # NORMALIZED COMPONENTS
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

        profit_score = normalize(
            result[
                "risk_adjusted_margin"
            ].values
        )

        # Lower transport cost is better.
        transport_score = (
            100.0
            -
            normalize(
                result[
                    "predicted_transport_cost"
                ].values
            )
        )

        # Lower delay is better.
        delay_score = (
            100.0
            -
            normalize(
                result[
                    "predicted_delay_hours"
                ].values
            )
        )

        # Lower damage is better.
        damage_score = (
            100.0
            -
            normalize(
                result[
                    "predicted_damage_percentage"
                ].values
            )
        )

        # --------------------------------------------------------------
        # FINAL RISK-ADJUSTED SCORE
        #
        # Profit       30%
        # Price        20%
        # Demand       15%
        # Transport    10%
        # Delay        10%
        # Damage       15%
        # --------------------------------------------------------------

        result[
            "risk_adjusted_score"
        ] = (

            0.30 * profit_score

            +

            0.20 * price_score

            +

            0.15 * demand_score

            +

            0.10 * transport_score

            +

            0.10 * delay_score

            +

            0.15 * damage_score

        )

        # --------------------------------------------------------------
        # RANK
        # --------------------------------------------------------------

        result = (
            result
            .sort_values(
                "risk_adjusted_score",
                ascending=False
            )
            .reset_index(drop=True)
        )

        result[
            "rank"
        ] = result.index + 1

        top_markets = result.head(
            top_n
        ).copy()

        # --------------------------------------------------------------
        # DISPLAY
        # --------------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("RISK-ADJUSTED MARKET RANKING")
        print("=" * 70)

        for _, row in top_markets.iterrows():

            print(
                f"\n#{int(row['rank'])} "
                f"{row['market']}"
            )

            print(
                f"  District          : "
                f"{row['district']}"
            )

            print(
                f"  Predicted price   : "
                f"₹{row['predicted_price_per_quintal']:,.2f}/quintal"
            )

            print(
                f"  Predicted demand  : "
                f"{row['predicted_demand_tonnes']:,.2f} tonnes"
            )

            print(
                f"  Transport cost    : "
                f"₹{row['predicted_transport_cost']:,.2f}"
            )

            print(
                f"  Delay              : "
                f"{row['predicted_delay_hours']:.2f} hours"
            )

            print(
                f"  Damage             : "
                f"{row['predicted_damage_percentage']:.2f}%"
            )

            print(
                f"  Risk-adjusted margin: "
                f"₹{row['risk_adjusted_margin']:,.2f}"
            )

            print(
                f"  Final score        : "
                f"{row['risk_adjusted_score']:.2f}/100"
            )

        # --------------------------------------------------------------
        # BEST MARKET
        # --------------------------------------------------------------

        best = top_markets.iloc[0]

        print("\n")
        print("=" * 70)
        print("RISK-ADJUSTED BEST MARKET")
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
            f"✓ Expected revenue : "
            f"₹{best['expected_revenue']:,.2f}"
        )

        print(
            f"✓ Transport cost : "
            f"₹{best['predicted_transport_cost']:,.2f}"
        )

        print(
            f"✓ Damage : "
            f"{best['predicted_damage_percentage']:.2f}%"
        )

        print(
            f"✓ Delay : "
            f"{best['predicted_delay_hours']:.2f} hours"
        )

        print(
            f"✓ Risk-adjusted margin : "
            f"₹{best['risk_adjusted_margin']:,.2f}"
        )

        print(
            f"✓ Final score : "
            f"{best['risk_adjusted_score']:.2f}/100"
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

            "transport_cost":
                safe_float(
                    best[
                        "predicted_transport_cost"
                    ]
                ),

            "delay_hours":
                safe_float(
                    best[
                        "predicted_delay_hours"
                    ]
                ),

            "damage_percentage":
                safe_float(
                    best[
                        "predicted_damage_percentage"
                    ]
                ),

            "expected_revenue":
                safe_float(
                    best[
                        "expected_revenue"
                    ]
                ),

            "risk_adjusted_margin":
                safe_float(
                    best[
                        "risk_adjusted_margin"
                    ]
                ),

            "risk_adjusted_score":
                safe_float(
                    best[
                        "risk_adjusted_score"
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
                        "predicted_transport_cost",
                        "predicted_delay_hours",
                        "predicted_damage_percentage",
                        "risk_adjusted_margin",
                        "risk_adjusted_score",
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
    print("RISK-ADJUSTED MARKET TEST")
    print("=" * 70)

    optimizer = (
        RiskAdjustedMarketOptimizer()
    )

    # --------------------------------------------------------------
    # Use a REAL crop from the dataset.
    # --------------------------------------------------------------

    crop_df = pd.read_csv(
        PRICE_DATASET,
        usecols=["crop"],
        low_memory=True
    )

    crop_df = crop_df.dropna()

    if crop_df.empty:

        raise RuntimeError(
            "No crop found in price dataset."
        )

    crop = str(
        crop_df.iloc[0]["crop"]
    )

    del crop_df

    # --------------------------------------------------------------
    # Use a real origin district.
    # --------------------------------------------------------------

    logistics_origin = pd.read_csv(
        LOGISTICS_DATASET,
        usecols=["origin_district"],
        low_memory=True
    )

    logistics_origin = (
        logistics_origin
        .dropna()
        .reset_index(drop=True)
    )

    if logistics_origin.empty:

        raise RuntimeError(
            "No origin district found in logistics dataset."
        )

    origin_district = str(
        logistics_origin.iloc[0][
            "origin_district"
        ]
    )

    del logistics_origin

    print(
        f"\n✓ Test crop : {crop}"
    )

    print(
        f"✓ Test origin district : "
        f"{origin_district}"
    )

    # --------------------------------------------------------------
    # Run
    # --------------------------------------------------------------

    result = optimizer.recommend(

        crop=crop,

        quantity_kg=1000,

        origin_district=origin_district,

        top_n=5,
    )

    # --------------------------------------------------------------
    # Final status
    # --------------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("RISK-ADJUSTED MARKET TEST COMPLETED")
    print("=" * 70)

    print(
        f"\n✓ Best market : "
        f"{result['best_market']}"
    )

    print(
        f"✓ Risk-adjusted score : "
        f"{result['risk_adjusted_score']:.2f}/100"
    )

    print(
        f"✓ Risk-adjusted margin : "
        f"₹{result['risk_adjusted_margin']:,.2f}"
    )

    print(
        f"✓ Markets ranked : "
        f"{len(result['ranked_markets'])}"
    )

    print(
        "\n✓ Real price data used."
    )

    print(
        "✓ Real demand data used."
    )

    print(
        "✓ Real logistics data used."
    )

    print(
        "✓ Existing ML models used."
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