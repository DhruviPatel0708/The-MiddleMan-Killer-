"""
======================================================================
FINAL AI RECOMMENDATION - FINAL INTEGRATION VERIFICATION
======================================================================

Components:
1. Price Prediction
2. Demand Forecasting
3. Quality Assessment
4. Buyer Reliability
5. Risk & Spillage
6. Cost Estimation
7. Feasibility Evaluation
8. Alternative Ranking
9. Final AI Recommendation
10. Optimal Action Selection

Rules:
- No frontend
- No FastAPI
- No external API
- No new dataset
- No model training
- Existing trained models only
- Existing processed feature datasets only
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ======================================================================
# 1. PROJECT PATH CONFIGURATION
# ======================================================================

CURRENT_FILE = Path(__file__).resolve()

# Expected file:
#
# D:\PythonProject3\backend\ml\evaluation\
#     test_final_ai_recommendation.py
#
# parents:
# 0 -> evaluation
# 1 -> ml
# 2 -> backend
# 3 -> PythonProject3

PROJECT_ROOT = CURRENT_FILE.parents[3]

BACKEND_DIR = PROJECT_ROOT / "backend"
ML_DIR = BACKEND_DIR / "ml"

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"

MODELS_DIR = ML_DIR / "saved_models"


# ======================================================================
# 2. MODEL → CORRECT FEATURE DATASET MAPPING
# ======================================================================

MODEL_DATASET_MAP = {

    "price_model.joblib":
        "price_features.csv",

    "demand_model.joblib":
        "demand_features.csv",

    "quality_grade_model.joblib":
        "quality_features.csv",

    "quality_score_model.joblib":
        "quality_features.csv",

    "buyer_model.joblib":
        "buyer_features.csv",

    "payment_risk_model.joblib":
        "transaction_features.csv",

    "delivery_risk_model.joblib":
        "transaction_features.csv",

    "damage_percentage_model.joblib":
        "logistics_features.csv",

    "delay_hours_model.joblib":
        "logistics_features.csv",

    "spoilage_risk_model.joblib":
        "quality_features.csv",

    "spoilage_risk_score_model.joblib":
        "quality_features.csv",

    "cost_estimation_model.joblib":
        "cost_features.csv",

    "transport_cost_model.joblib":
        "logistics_features.csv",
}


# ======================================================================
# 3. DISPLAY HELPERS
# ======================================================================

def line():
    print("=" * 70)


def section(number, title):
    print()
    line()
    print(f"{number}. {title}")
    line()


def success(message):
    print(f"✓ {message}")


def failure(message):
    print(f"✗ {message}")


def warning(message):
    print(f"⚠ {message}")


# ======================================================================
# 4. PATH VERIFICATION
# ======================================================================

def verify_project_paths():

    if not PROJECT_ROOT.exists():
        raise RuntimeError(
            f"Project root not found: {PROJECT_ROOT}"
        )

    if not PROCESSED_DIR.exists():
        raise RuntimeError(
            f"Processed data directory not found: "
            f"{PROCESSED_DIR}"
        )

    if not MODELS_DIR.exists():
        raise RuntimeError(
            f"Saved models directory not found: "
            f"{MODELS_DIR}"
        )

    success(
        f"Project root : {PROJECT_ROOT}"
    )

    success(
        f"ML directory : {ML_DIR}"
    )

    success(
        f"Processed directory : {PROCESSED_DIR}"
    )

    success(
        f"Saved models directory : {MODELS_DIR}"
    )

    success(
        "Project paths verified"
    )


# ======================================================================
# 5. LOAD MODEL
# ======================================================================

def load_model(model_name):

    model_path = MODELS_DIR / model_name

    if not model_path.exists():

        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    model = joblib.load(model_path)

    return model


# ======================================================================
# 6. LOAD DATASET
# ======================================================================

def load_dataset(dataset_name):

    dataset_path = (
        PROCESSED_DIR / dataset_name
    )

    if not dataset_path.exists():

        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    df = pd.read_csv(
        dataset_path
    )

    if df.empty:

        raise ValueError(
            f"Dataset is empty: {dataset_name}"
        )

    return df


# ======================================================================
# 7. EXTRACT EXPECTED MODEL FEATURES
# ======================================================================

def get_expected_features(model):

    # Direct estimator / pipeline
    if hasattr(
        model,
        "feature_names_in_"
    ):

        return list(
            model.feature_names_in_
        )

    # Pipeline
    if hasattr(
        model,
        "steps"
    ):

        for _, step in reversed(
            model.steps
        ):

            if hasattr(
                step,
                "feature_names_in_"
            ):

                return list(
                    step.feature_names_in_
                )

    return None


# ======================================================================
# 8. PREPARE MODEL INPUT
# ======================================================================

def prepare_model_input(
    model,
    dataframe,
    model_name
):

    features = get_expected_features(
        model
    )

    if features is None:

        raise RuntimeError(
            f"Could not determine expected "
            f"features for {model_name}"
        )

    missing = [
        feature
        for feature in features
        if feature not in dataframe.columns
    ]

    if missing:

        raise RuntimeError(
            f"{model_name} missing "
            f"{len(missing)} required features: "
            + ", ".join(missing)
        )

    X = dataframe[
        features
    ].iloc[
        [0]
    ].copy()

    return X, features


# ======================================================================
# 9. MODEL PREDICTION
# ======================================================================

def predict(
    model_name
):

    dataset_name = (
        MODEL_DATASET_MAP[
            model_name
        ]
    )

    model = load_model(
        model_name
    )

    dataframe = load_dataset(
        dataset_name
    )

    X, features = prepare_model_input(
        model,
        dataframe,
        model_name
    )

    prediction = model.predict(
        X
    )

    if prediction is None:

        raise RuntimeError(
            f"{model_name} returned no prediction"
        )

    if len(prediction) == 0:

        raise RuntimeError(
            f"{model_name} returned empty prediction"
        )

    return prediction[0], features


# ======================================================================
# 10. NUMERIC CONVERSION
# ======================================================================

def to_float(
    value,
    default=0.0
):

    try:

        result = float(value)

        if np.isfinite(result):

            return result

    except (
        TypeError,
        ValueError
    ):

        pass

    return default


# ======================================================================
# 11. RISK NORMALIZATION
# ======================================================================

def risk_to_numeric(value):

    if isinstance(
        value,
        str
    ):

        text = value.strip().upper()

        mapping = {
            "LOW": 10.0,
            "MEDIUM": 50.0,
            "MODERATE": 50.0,
            "HIGH": 90.0,
            "VERY_HIGH": 100.0,
            "CRITICAL": 100.0,
            "RELIABLE": 10.0,
            "UNRELIABLE": 90.0,
        }

        if text in mapping:

            return mapping[text]

    return to_float(
        value
    )


# ======================================================================
# 12. FINAL RECOMMENDATION ENGINE
# ======================================================================

def calculate_recommendation(
    price,
    demand,
    quality_grade,
    quality_score,
    buyer_reliability,
    payment_risk,
    delivery_risk,
    damage_percentage,
    delay_hours,
    spoilage_risk,
    spoilage_score,
    estimated_cost,
    transport_cost,
):

    price_value = to_float(
        price
    )

    demand_value = to_float(
        demand
    )

    quality_value = to_float(
        quality_score
    )

    payment_risk_value = risk_to_numeric(
        payment_risk
    )

    delivery_risk_value = risk_to_numeric(
        delivery_risk
    )

    damage_value = to_float(
        damage_percentage
    )

    delay_value = to_float(
        delay_hours
    )

    spoilage_value = risk_to_numeric(
        spoilage_score
    )

    cost_value = to_float(
        estimated_cost
    )

    transport_value = to_float(
        transport_cost
    )

    # --------------------------------------------------------------
    # TOTAL COST
    # --------------------------------------------------------------

    total_cost = (
        cost_value
        + transport_value
    )

    # --------------------------------------------------------------
    # ESTIMATED NET VALUE
    # --------------------------------------------------------------

    estimated_revenue = price_value

    estimated_net_value = (
        estimated_revenue
        - total_cost
    )

    # --------------------------------------------------------------
    # TOTAL RISK
    # --------------------------------------------------------------

    risk_score = (
        payment_risk_value * 0.20
        + delivery_risk_value * 0.20
        + damage_value * 0.15
        + delay_value * 0.10
        + spoilage_value * 0.35
    )

    risk_score = max(
        0.0,
        min(
            risk_score,
            100.0
        )
    )

    # --------------------------------------------------------------
    # BUYER SCORE
    # --------------------------------------------------------------

    reliability_text = str(
        buyer_reliability
    ).upper()

    if reliability_text == "RELIABLE":

        buyer_score = 100.0

    elif reliability_text in {
        "MEDIUM",
        "MODERATE",
    }:

        buyer_score = 60.0

    elif reliability_text == "UNRELIABLE":

        buyer_score = 20.0

    else:

        buyer_score = 50.0

    # --------------------------------------------------------------
    # DEMAND SCORE
    # --------------------------------------------------------------

    demand_score = max(
        0.0,
        min(
            demand_value,
            100.0
        )
    )

    # --------------------------------------------------------------
    # QUALITY SCORE
    # --------------------------------------------------------------

    quality_score_normalized = max(
        0.0,
        min(
            quality_value,
            100.0
        )
    )

    # --------------------------------------------------------------
    # PROFIT SCORE
    # --------------------------------------------------------------

    if estimated_revenue > 0:

        profit_ratio = (
            estimated_net_value
            / estimated_revenue
        )

        profit_score = max(
            0.0,
            min(
                profit_ratio * 100.0,
                100.0
            )
        )

    else:

        profit_score = 0.0

    # --------------------------------------------------------------
    # FINAL DECISION SCORE
    # --------------------------------------------------------------

    recommendation_score = (

        profit_score * 0.35

        + demand_score * 0.20

        + quality_score_normalized * 0.15

        + buyer_score * 0.15

        + (100.0 - risk_score) * 0.15

    )

    recommendation_score = max(
        0.0,
        min(
            recommendation_score,
            100.0
        )
    )

    # --------------------------------------------------------------
    # FEASIBILITY
    # --------------------------------------------------------------

    feasible = True

    reasons = []

    if estimated_net_value <= 0:

        feasible = False

        reasons.append(
            "Estimated net value is not positive"
        )

    if risk_score >= 80:

        feasible = False

        reasons.append(
            "Overall risk is too high"
        )

    if reliability_text == "UNRELIABLE":

        feasible = False

        reasons.append(
            "Buyer reliability is low"
        )

    if quality_score_normalized <= 0:

        feasible = False

        reasons.append(
            "Quality assessment is invalid"
        )

    # --------------------------------------------------------------
    # FINAL ACTION
    # --------------------------------------------------------------

    if not feasible:

        action = (
            "DO NOT PROCEED"
        )

    elif recommendation_score >= 75:

        action = (
            "PROCEED WITH RECOMMENDED DEAL"
        )

    elif recommendation_score >= 55:

        action = (
            "PROCEED AFTER REVIEW"
        )

    else:

        action = (
            "HOLD FOR BETTER ALTERNATIVE"
        )

    return {

        "quality_grade":
            quality_grade,

        "buyer_reliability":
            buyer_reliability,

        "estimated_revenue":
            estimated_revenue,

        "estimated_cost":
            total_cost,

        "estimated_net_value":
            estimated_net_value,

        "risk_score":
            risk_score,

        "buyer_score":
            buyer_score,

        "demand_score":
            demand_score,

        "quality_score":
            quality_score_normalized,

        "profit_score":
            profit_score,

        "recommendation_score":
            recommendation_score,

        "feasible":
            feasible,

        "action":
            action,

        "reasons":
            reasons,
    }


# ======================================================================
# 13. ALTERNATIVE RANKING
# ======================================================================

def rank_alternatives(
    recommendation
):

    alternatives = [

        {
            "name":
                "Recommended Deal",

            "score":
                recommendation[
                    "recommendation_score"
                ],

            "feasible":
                recommendation[
                    "feasible"
                ],
        },

        {
            "name":
                "Risk-Minimized Alternative",

            "score":
                max(
                    0.0,
                    recommendation[
                        "recommendation_score"
                    ]
                    - recommendation[
                        "risk_score"
                    ] * 0.10
                ),

            "feasible":
                recommendation[
                    "risk_score"
                ] < 70,
        },

        {
            "name":
                "Profit-Focused Alternative",

            "score":
                recommendation[
                    "profit_score"
                ],

            "feasible":
                recommendation[
                    "estimated_net_value"
                ] > 0,
        },
    ]

    alternatives.sort(
        key=lambda item:
            (
                item["feasible"],
                item["score"]
            ),
        reverse=True
    )

    return alternatives


# ======================================================================
# 14. MAIN
# ======================================================================

def main():

    print()
    line()

    print(
        "FINAL AI RECOMMENDATION - "
        "FINAL INTEGRATION VERIFICATION"
    )

    line()

    print()
    print("Components:")
    print("1. Price Prediction")
    print("2. Demand Forecasting")
    print("3. Quality Assessment")
    print("4. Buyer Reliability")
    print("5. Risk & Spillage")
    print("6. Cost Estimation")
    print("7. Feasibility Evaluation")
    print("8. Alternative Ranking")
    print("9. Final AI Recommendation")
    print("10. Optimal Action Selection")

    print()
    print("No frontend.")
    print("No FastAPI.")
    print("No external API.")
    print("No new dataset.")
    print("No model training.")
    print("Existing trained models only.")

    # ==================================================================
    # 1. INITIALIZATION
    # ==================================================================

    section(
        1,
        "AI RECOMMENDATION ENGINE INITIALIZATION"
    )

    verify_project_paths()

    # ==================================================================
    # 2. PRICE PREDICTION
    # ==================================================================

    section(
        2,
        "PRICE PREDICTION"
    )

    price, price_features = predict(
        "price_model.joblib"
    )

    success(
        f"Price prediction verified"
    )

    success(
        f"Features used : {len(price_features)}"
    )

    print(
        f"✓ Predicted Price : "
        f"₹ {to_float(price):,.2f}"
    )

    # ==================================================================
    # 3. DEMAND
    # ==================================================================

    section(
        3,
        "DEMAND FORECASTING"
    )

    demand, demand_features = predict(
        "demand_model.joblib"
    )

    success(
        "Demand prediction verified"
    )

    success(
        f"Features used : {len(demand_features)}"
    )

    print(
        f"✓ Predicted Demand : "
        f"{to_float(demand):,.2f}"
    )

    # ==================================================================
    # 4. QUALITY
    # ==================================================================

    section(
        4,
        "QUALITY ASSESSMENT"
    )

    quality_grade, grade_features = predict(
        "quality_grade_model.joblib"
    )

    quality_score, score_features = predict(
        "quality_score_model.joblib"
    )

    success(
        "Quality grade prediction verified"
    )

    success(
        "Quality score prediction verified"
    )

    print(
        f"✓ Quality Grade : {quality_grade}"
    )

    print(
        f"✓ Quality Score : "
        f"{to_float(quality_score):.2f}"
    )

    # ==================================================================
    # 5. BUYER RELIABILITY
    # ==================================================================

    section(
        5,
        "BUYER RELIABILITY"
    )

    buyer_reliability, buyer_features = predict(
        "buyer_model.joblib"
    )

    success(
        "Buyer reliability prediction verified"
    )

    print(
        f"✓ Buyer Reliability : "
        f"{buyer_reliability}"
    )

    # ==================================================================
    # 6. PAYMENT / DELIVERY RISK
    # ==================================================================

    section(
        6,
        "PAYMENT & DELIVERY RISK"
    )

    payment_risk, payment_features = predict(
        "payment_risk_model.joblib"
    )

    delivery_risk, delivery_features = predict(
        "delivery_risk_model.joblib"
    )

    success(
        "Payment risk prediction verified"
    )

    success(
        "Delivery risk prediction verified"
    )

    print(
        f"✓ Payment Risk : "
        f"{payment_risk}"
    )

    print(
        f"✓ Delivery Risk : "
        f"{delivery_risk}"
    )

    # ==================================================================
    # 7. RISK & SPILLAGE
    # ==================================================================

    section(
        7,
        "RISK & SPILLAGE ASSESSMENT"
    )

    damage_percentage, damage_features = predict(
        "damage_percentage_model.joblib"
    )

    delay_hours, delay_features = predict(
        "delay_hours_model.joblib"
    )

    spoilage_risk, spoilage_features = predict(
        "spoilage_risk_model.joblib"
    )

    spoilage_score, spoilage_score_features = predict(
        "spoilage_risk_score_model.joblib"
    )

    success(
        "Damage prediction verified"
    )

    success(
        "Delay prediction verified"
    )

    success(
        "Spoilage risk prediction verified"
    )

    success(
        "Spoilage score prediction verified"
    )

    print(
        f"✓ Damage : "
        f"{to_float(damage_percentage):.2f}%"
    )

    print(
        f"✓ Delay : "
        f"{to_float(delay_hours):.2f} hours"
    )

    print(
        f"✓ Spoilage Risk : "
        f"{spoilage_risk}"
    )

    print(
        f"✓ Spoilage Score : "
        f"{to_float(spoilage_score):.2f}"
    )

    # ==================================================================
    # 8. COST ESTIMATION
    # ==================================================================

    section(
        8,
        "COST ESTIMATION"
    )

    estimated_cost, cost_features = predict(
        "cost_estimation_model.joblib"
    )

    transport_cost, transport_features = predict(
        "transport_cost_model.joblib"
    )

    success(
        "Total cost prediction verified"
    )

    success(
        "Transport cost prediction verified"
    )

    print(
        f"✓ Estimated Cost : "
        f"₹ {to_float(estimated_cost):,.2f}"
    )

    print(
        f"✓ Transport Cost : "
        f"₹ {to_float(transport_cost):,.2f}"
    )

    # ==================================================================
    # 9. FEASIBILITY
    # ==================================================================

    section(
        9,
        "FEASIBILITY EVALUATION"
    )

    recommendation = calculate_recommendation(

        price=price,

        demand=demand,

        quality_grade=quality_grade,

        quality_score=quality_score,

        buyer_reliability=buyer_reliability,

        payment_risk=payment_risk,

        delivery_risk=delivery_risk,

        damage_percentage=damage_percentage,

        delay_hours=delay_hours,

        spoilage_risk=spoilage_risk,

        spoilage_score=spoilage_score,

        estimated_cost=estimated_cost,

        transport_cost=transport_cost,
    )

    success(
        f"Feasibility : "
        f"{recommendation['feasible']}"
    )

    success(
        f"Estimated Revenue : "
        f"₹ {recommendation['estimated_revenue']:,.2f}"
    )

    success(
        f"Estimated Total Cost : "
        f"₹ {recommendation['estimated_cost']:,.2f}"
    )

    success(
        f"Estimated Net Value : "
        f"₹ {recommendation['estimated_net_value']:,.2f}"
    )

    # ==================================================================
    # 10. ALTERNATIVE RANKING
    # ==================================================================

    section(
        10,
        "FEASIBLE ALTERNATIVE RANKING"
    )

    alternatives = rank_alternatives(
        recommendation
    )

    if not alternatives:

        raise RuntimeError(
            "No alternatives generated"
        )

    for index, alternative in enumerate(
        alternatives,
        start=1
    ):

        status = (
            "FEASIBLE"
            if alternative["feasible"]
            else "NOT FEASIBLE"
        )

        print(
            f"{index}. "
            f"{alternative['name']} | "
            f"Score: "
            f"{alternative['score']:.2f} | "
            f"{status}"
        )

    success(
        "Alternative ranking generated"
    )

    # ==================================================================
    # 11. FINAL AI RECOMMENDATION
    # ==================================================================

    section(
        11,
        "FINAL AI RECOMMENDATION"
    )

    feasible_alternatives = [
        item
        for item in alternatives
        if item["feasible"]
    ]

    if feasible_alternatives:

        best = feasible_alternatives[0]

    else:

        best = alternatives[0]

    success(
        f"Best Alternative : "
        f"{best['name']}"
    )

    success(
        f"Best Score : "
        f"{best['score']:.2f}"
    )

    success(
        f"Final Feasibility : "
        f"{best['feasible']}"
    )

    # ==================================================================
    # 12. OPTIMAL ACTION
    # ==================================================================

    section(
        12,
        "OPTIMAL ACTION SELECTION"
    )

    final_action = (
        recommendation["action"]
    )

    if not isinstance(
        final_action,
        str
    ) or not final_action.strip():

        raise RuntimeError(
            "Final AI action is empty"
        )

    print(
        "✓ FINAL AI RECOMMENDED ACTION:"
    )

    print()

    print(
        f"   {final_action}"
    )

    success(
        "Optimal action selected"
    )

    # ==================================================================
    # 13. FINAL VALIDATION
    # ==================================================================

    section(
        13,
        "FINAL RECOMMENDATION VALIDATION"
    )

    required_prediction_values = {

        "price":
            price,

        "demand":
            demand,

        "quality_grade":
            quality_grade,

        "quality_score":
            quality_score,

        "buyer_reliability":
            buyer_reliability,

        "payment_risk":
            payment_risk,

        "delivery_risk":
            delivery_risk,

        "damage_percentage":
            damage_percentage,

        "delay_hours":
            delay_hours,

        "spoilage_risk":
            spoilage_risk,

        "spoilage_score":
            spoilage_score,

        "estimated_cost":
            estimated_cost,

        "transport_cost":
            transport_cost,
    }

    for name, value in (
        required_prediction_values.items()
    ):

        if value is None:

            raise RuntimeError(
                f"Missing AI output: {name}"
            )

    success(
        "All AI prediction outputs available"
    )

    if not np.isfinite(
        recommendation[
            "recommendation_score"
        ]
    ):

        raise RuntimeError(
            "Invalid recommendation score"
        )

    success(
        "Recommendation score verified"
    )

    if not np.isfinite(
        recommendation[
            "risk_score"
        ]
    ):

        raise RuntimeError(
            "Invalid risk score"
        )

    success(
        "Risk score verified"
    )

    if not np.isfinite(
        recommendation[
            "estimated_net_value"
        ]
    ):

        raise RuntimeError(
            "Invalid estimated net value"
        )

    success(
        "Net value verified"
    )

    success(
        "Final recommendation structure verified"
    )

    # ==================================================================
    # 14. FINAL STATUS
    # ==================================================================

    section(
        14,
        "FINAL AI RECOMMENDATION STATUS"
    )

    success(
        "Price Prediction              : VERIFIED"
    )

    success(
        "Demand Forecasting            : VERIFIED"
    )

    success(
        "Quality Assessment            : VERIFIED"
    )

    success(
        "Buyer Reliability             : VERIFIED"
    )

    success(
        "Risk & Spillage               : VERIFIED"
    )

    success(
        "Cost Estimation               : VERIFIED"
    )

    success(
        "Feasibility Evaluation        : VERIFIED"
    )

    success(
        "Alternative Ranking           : VERIFIED"
    )

    success(
        "Final AI Recommendation       : VERIFIED"
    )

    success(
        "Optimal Action Selection      : VERIFIED"
    )

    print()

    line()

    print(
        "FINAL AI RECOMMENDATION STATUS: COMPLETE"
    )

    line()

    print()

    success(
        "FINAL AI RECOMMENDATION "
        "VERIFICATION PASSED"
    )

    print()
    print(
        "✓ Existing trained models verified"
    )

    print(
        "✓ Existing feature datasets verified"
    )

    print(
        "✓ Correct model-to-feature mapping verified"
    )

    print(
        "✓ All AI outputs generated"
    )

    print(
        "✓ Feasibility evaluated"
    )

    print(
        "✓ Alternatives ranked"
    )

    print(
        "✓ Final recommendation generated"
    )

    print(
        "✓ Optimal action selected"
    )

    return 0


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        sys.exit(
            main()
        )

    except KeyboardInterrupt:

        print()
        print(
            "Verification interrupted by user."
        )

        sys.exit(130)

    except Exception as exc:

        print()
        line()

        print(
            "FINAL AI RECOMMENDATION "
            "VERIFICATION FAILED"
        )

        line()

        print()

        print(
            f"Error Type : "
            f"{type(exc).__name__}"
        )

        print(
            f"Error      : {exc}"
        )

        print()

        traceback.print_exc()

        sys.exit(1)