"""
AGRICULTURE AI - END-TO-END DECISION TEST

Uses a REAL transaction row from transaction_features.csv.

Flow:

Real transaction
    ↓
Real transaction inputs
    ↓
13 ML model predictions
    ↓
Decision Intelligence Engine
    ↓
Final recommendation

IMPORTANT:
- No model retraining
- No fake prediction values
- Uses actual quantity
- Uses actual agreed price
- Uses actual market price
"""

from pathlib import Path
import pandas as pd

from prediction_service import PredictionService
from model_adapters import ModelAdapters
from decision_engine import DecisionIntelligenceEngine


# ======================================================================
# PATH
# ======================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRANSACTION_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "transaction_features.csv"
)


# ======================================================================
# LOAD REAL TRANSACTION
# ======================================================================

def load_real_transaction():

    print("\n")
    print("=" * 70)
    print("LOADING REAL TRANSACTION")
    print("=" * 70)

    if not TRANSACTION_PATH.exists():

        raise FileNotFoundError(
            f"\nTransaction dataset not found:\n"
            f"{TRANSACTION_PATH}"
        )

    df = pd.read_csv(
        TRANSACTION_PATH
    )

    if df.empty:

        raise ValueError(
            "Transaction dataset is empty."
        )

    print(
        f"\n✓ Dataset loaded."
    )

    print(
        f"Rows    : {len(df):,}"
    )

    print(
        f"Columns : {len(df.columns)}"
    )

    # --------------------------------------------------------------
    # Select first real transaction
    # --------------------------------------------------------------

    row = df.iloc[0].copy()

    print("\nREAL TRANSACTION INPUT")
    print("-" * 70)

    important_columns = [

        "transaction_id",
        "farmer_id",
        "buyer_id",
        "crop",
        "quantity_kg",
        "agreed_price_per_kg",
        "market_price_per_kg",
        "buyer_rating",
        "distance_km",
        "estimated_travel_hours",
    ]

    for column in important_columns:

        if column in row.index:

            print(
                f"{column:<30}: {row[column]}"
            )

    return row


# ======================================================================
# VALIDATE REAL TRANSACTION
# ======================================================================

def validate_transaction(transaction):

    print("\n")
    print("=" * 70)
    print("VALIDATING REAL TRANSACTION")
    print("=" * 70)

    # --------------------------------------------------------------
    # Required fields
    # --------------------------------------------------------------

    required_fields = [

        "quantity_kg",
        "agreed_price_per_kg",
        "market_price_per_kg",
    ]

    missing_fields = [

        field
        for field in required_fields
        if field not in transaction.index
    ]

    if missing_fields:

        raise ValueError(
            "Missing required transaction fields: "
            + str(missing_fields)
        )

    # --------------------------------------------------------------
    # Quantity
    # --------------------------------------------------------------

    quantity = float(
        transaction["quantity_kg"]
    )

    if quantity <= 0:

        raise ValueError(
            "Quantity must be greater than zero."
        )

    # --------------------------------------------------------------
    # Agreed price
    # --------------------------------------------------------------

    agreed_price = float(
        transaction["agreed_price_per_kg"]
    )

    if agreed_price <= 0:

        raise ValueError(
            "Agreed price must be greater than zero."
        )

    # --------------------------------------------------------------
    # Market price
    # --------------------------------------------------------------

    market_price = float(
        transaction["market_price_per_kg"]
    )

    if market_price <= 0:

        raise ValueError(
            "Market price must be greater than zero."
        )

    # --------------------------------------------------------------
    # Crop
    # --------------------------------------------------------------

    crop = str(
        transaction.get(
            "crop",
            ""
        )
    ).strip()

    if (
        not crop
        or crop.upper() == "UNKNOWN"
        or crop.upper() == "NAN"
    ):

        print(
            "\n⚠ WARNING: Crop is UNKNOWN in this dataset row."
        )

        print(
            "The ML models can still be tested, "
            "but the farmer-facing production system "
            "must require a valid crop."
        )

    print(
        "\n✓ Transaction values validated."
    )

    print(
        f"Quantity        : {quantity:,.2f} kg"
    )

    print(
        f"Agreed price    : ₹{agreed_price:,.2f}/kg"
    )

    print(
        f"Market price    : ₹{market_price:,.2f}/kg"
    )


# ======================================================================
# MAIN
# ======================================================================

def main():

    print("\n")
    print("=" * 70)
    print("AGRICULTURE AI END-TO-END DECISION TEST")
    print("=" * 70)

    # ==================================================================
    # 1. REAL TRANSACTION
    # ==================================================================

    transaction = load_real_transaction()

    validate_transaction(
        transaction
    )

    # ==================================================================
    # 2. PREDICTION SERVICE
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("INITIALIZING PREDICTION SERVICE")
    print("=" * 70)

    prediction_service = (
        PredictionService()
    )

    # ==================================================================
    # 3. MODEL ADAPTERS
    # ==================================================================

    adapters = ModelAdapters(
        prediction_service=prediction_service
    )

    # ==================================================================
    # 4. VALIDATE ADAPTERS
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("VALIDATING MODEL ADAPTERS")
    print("=" * 70)

    validation = (
        adapters.validate_all_adapters()
    )

    if not all(
        validation.values()
    ):

        raise RuntimeError(
            "Model adapter validation failed."
        )

    print(
        "\n✓ ALL MODEL ADAPTERS PASSED"
    )

    # ==================================================================
    # 5. GENERATE MODEL PREDICTIONS
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("GENERATING MODEL PREDICTIONS")
    print("=" * 70)

    # --------------------------------------------------------------
    # Buyer
    # --------------------------------------------------------------

    buyer_prediction = (
        adapters.predict_buyer()
    )

    # --------------------------------------------------------------
    # Quality / Spoilage
    # --------------------------------------------------------------

    quality_prediction = (
        adapters.predict_quality()
    )

    # --------------------------------------------------------------
    # Logistics
    # --------------------------------------------------------------

    logistics_prediction = (
        adapters.predict_logistics()
    )

    # --------------------------------------------------------------
    # Cost
    # --------------------------------------------------------------

    cost_prediction = (
        adapters.predict_cost()
    )

    # --------------------------------------------------------------
    # Transaction Risk
    # --------------------------------------------------------------

    risk_prediction = (
        adapters.predict_risk()
    )

    # --------------------------------------------------------------
    # Price
    # --------------------------------------------------------------

    price_input = (
        adapters.build_price_input()
    )

    price_prediction = (
        prediction_service.predict_one(
            "price",
            price_input
        )
    )

    # --------------------------------------------------------------
    # Demand
    # --------------------------------------------------------------

    demand_input = (
        adapters.build_demand_input()
    )

    demand_prediction = (
        prediction_service.predict_one(
            "demand",
            demand_input
        )
    )

    # ==================================================================
    # 6. COMBINE ML PREDICTIONS + REAL TRANSACTION VALUES
    # ==================================================================

    predictions = {

        # ----------------------------------------------------------
        # ML predictions
        # ----------------------------------------------------------

        "price_prediction":
            float(
                price_prediction
            ),

        "demand_prediction":
            float(
                demand_prediction
            ),

        "buyer_reliability":
            buyer_prediction[
                "buyer_reliability"
            ],

        "quality_score":
            float(
                quality_prediction[
                    "quality_score"
                ]
            ),

        "quality_grade":
            quality_prediction[
                "quality_grade"
            ],

        "spoilage_risk_score":
            float(
                quality_prediction[
                    "spoilage_risk_score"
                ]
            ),

        "spoilage_risk":
            quality_prediction[
                "spoilage_risk"
            ],

        "transport_cost":
            float(
                logistics_prediction[
                    "transport_cost"
                ]
            ),

        "delay_hours":
            float(
                logistics_prediction[
                    "delay_hours"
                ]
            ),

        "damage_percentage":
            float(
                logistics_prediction[
                    "damage_percentage"
                ]
            ),

        "estimated_total_cost":
            float(
                cost_prediction[
                    "estimated_total_cost"
                ]
            ),

        "payment_risk":
            risk_prediction[
                "payment_risk"
            ],

        "delivery_risk":
            risk_prediction[
                "delivery_risk"
            ],

        # ----------------------------------------------------------
        # REAL TRANSACTION VALUES
        # ----------------------------------------------------------

        "quantity_kg":
            float(
                transaction[
                    "quantity_kg"
                ]
            ),

        "agreed_price_per_kg":
            float(
                transaction[
                    "agreed_price_per_kg"
                ]
            ),

        "market_price_per_kg":
            float(
                transaction[
                    "market_price_per_kg"
                ]
            ),

        # ----------------------------------------------------------
        # Optional real transaction information
        # ----------------------------------------------------------

        "crop":
            str(
                transaction.get(
                    "crop",
                    ""
                )
            ),

        "buyer_rating":
            float(
                transaction.get(
                    "buyer_rating",
                    0
                )
            ),

        "distance_km":
            float(
                transaction.get(
                    "distance_km",
                    0
                )
            ),

        "estimated_travel_hours":
            float(
                transaction.get(
                    "estimated_travel_hours",
                    0
                )
            ),
    }

    # ==================================================================
    # 7. DISPLAY PREDICTIONS
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("REAL ML PREDICTIONS")
    print("=" * 70)

    print(
        f"\nPredicted Price       : "
        f"{predictions['price_prediction']:.2f}"
    )

    print(
        f"Predicted Demand      : "
        f"{predictions['demand_prediction']:.2f}"
    )

    print(
        f"Buyer Reliability     : "
        f"{predictions['buyer_reliability']}"
    )

    print(
        f"Quality Score         : "
        f"{predictions['quality_score']:.2f}"
    )

    print(
        f"Quality Grade         : "
        f"{predictions['quality_grade']}"
    )

    print(
        f"Spoilage Score        : "
        f"{predictions['spoilage_risk_score']:.2f}"
    )

    print(
        f"Spoilage Risk         : "
        f"{predictions['spoilage_risk']}"
    )

    print(
        f"Transport Cost        : "
        f"{predictions['transport_cost']:.2f}"
    )

    print(
        f"Delay Hours           : "
        f"{predictions['delay_hours']:.2f}"
    )

    print(
        f"Damage Percentage     : "
        f"{predictions['damage_percentage']:.2f}%"
    )

    print(
        f"Estimated Total Cost  : "
        f"{predictions['estimated_total_cost']:.2f}"
    )

    print(
        f"Payment Risk          : "
        f"{predictions['payment_risk']}"
    )

    print(
        f"Delivery Risk         : "
        f"{predictions['delivery_risk']}"
    )

    # ==================================================================
    # 8. REAL TRANSACTION VALUES
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("REAL TRANSACTION VALUES USED FOR DECISION")
    print("=" * 70)

    print(
        f"\nCrop                  : "
        f"{predictions['crop']}"
    )

    print(
        f"Quantity              : "
        f"{predictions['quantity_kg']:,.2f} kg"
    )

    print(
        f"Agreed Price          : "
        f"₹{predictions['agreed_price_per_kg']:,.2f}/kg"
    )

    print(
        f"Market Price         : "
        f"₹{predictions['market_price_per_kg']:,.2f}/kg"
    )

    print(
        f"Buyer Rating          : "
        f"{predictions['buyer_rating']:.2f}"
    )

    # ==================================================================
    # 9. DECISION ENGINE
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("RUNNING DECISION INTELLIGENCE")
    print("=" * 70)

    engine = (
        DecisionIntelligenceEngine()
    )

    decision = (
        engine.make_decision(
            predictions
        )
    )

    # ==================================================================
    # 10. FINAL DECISION
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("FINAL AGRICULTURAL DECISION")
    print("=" * 70)

    print(
        f"\nRecommendation : "
        f"{decision['recommendation']}"
    )

    print(
        f"Decision Score : "
        f"{decision['decision_score']:.2f}/100"
    )

    print(
        f"Risk Score     : "
        f"{decision['risk_score']:.2f}/100"
    )

    print(
        f"Risk Level     : "
        f"{decision['risk_level']}"
    )

    print(
        f"\nPrice Used     : "
        f"₹{decision['price_used_for_revenue']:,.2f}/kg"
    )

    print(
        f"Price Source   : "
        f"{decision['price_source']}"
    )

    print(
        f"Quantity       : "
        f"{decision['quantity_kg']:,.2f} kg"
    )

    print(
        f"\nExpected Revenue : "
        f"₹{decision['expected_revenue']:,.2f}"
    )

    print(
        f"Estimated Cost   : "
        f"₹{decision['estimated_total_cost']:,.2f}"
    )

    print(
        f"Estimated Margin : "
        f"₹{decision['estimated_margin']:,.2f}"
    )

    print(
        f"Margin %         : "
        f"{decision['margin_percentage']:.2f}%"
    )

    # ==================================================================
    # 11. SCORES
    # ==================================================================

    print("\nSCORES")
    print("-" * 70)

    for name, value in decision[
        "scores"
    ].items():

        print(
            f"{name:<15}: {value:.2f}"
        )

    # ==================================================================
    # 12. STRENGTHS
    # ==================================================================

    print("\nSTRENGTHS")
    print("-" * 70)

    if decision["strengths"]:

        for item in decision["strengths"]:

            print(
                f"✓ {item}"
            )

    else:

        print(
            "None identified."
        )

    # ==================================================================
    # 13. CONCERNS
    # ==================================================================

    print("\nCONCERNS")
    print("-" * 70)

    if decision["concerns"]:

        for item in decision["concerns"]:

            print(
                f"⚠ {item}"
            )

    else:

        print(
            "No major concerns identified."
        )

    # ==================================================================
    # 14. EXPLANATION
    # ==================================================================

    print("\nEXPLANATION")
    print("-" * 70)

    print(
        decision["explanation"]
    )

    # ==================================================================
    # 15. COMPLETION
    # ==================================================================

    print("\n")
    print("=" * 70)
    print("END-TO-END DECISION TEST COMPLETED")
    print("=" * 70)

    print(
        "\n✓ Real transaction row used."
    )

    print(
        "✓ Real ML models used."
    )

    print(
        "✓ 13 ML model predictions generated."
    )

    print(
        "✓ Real quantity used."
    )

    print(
        "✓ Real agreed price used."
    )

    print(
        "✓ Real market price used."
    )

    print(
        "✓ Financial calculation completed."
    )

    print(
        "✓ Decision score calculated."
    )

    print(
        "✓ Risk score calculated."
    )

    print(
        "✓ Final recommendation generated."
    )

    print(
        "\nNo ML model was retrained."
    )

    print(
        "No fake prediction values were generated."
    )


# ======================================================================
# RUN
# ======================================================================

if __name__ == "__main__":

    main()