"""
FINAL AI RECOMMENDATION - VERIFICATION TEST

Verifies ONLY the Final AI Recommendation layer.

Required outputs:
    1. Sell Now vs Wait
    2. Choose Market
    3. Choose Buyer
    4. Expected Net Profit
    5. Risk Level
    6. Confidence
    7. Reason

This test:
    - does not train any model
    - does not modify any dataset
    - does not modify trained models
    - does not create fake ML predictions
    - does not add an architecture component
"""

from pathlib import Path
import sys
import traceback


# ======================================================================
# PATH SETUP
# ======================================================================

CURRENT_FILE = Path(__file__).resolve()

RECOMMENDATION_DIR = CURRENT_FILE.parent

APP_DIR = RECOMMENDATION_DIR.parent

BACKEND_DIR = APP_DIR.parent

PROJECT_ROOT = BACKEND_DIR.parent

for path in [
    RECOMMENDATION_DIR,
    APP_DIR,
    BACKEND_DIR,
    PROJECT_ROOT,
]:

    if str(path) not in sys.path:

        sys.path.insert(
            0,
            str(path),
        )


# ======================================================================
# TEST DATA
# ======================================================================

DECISION_RESULT = {

    "recommendation":
        "SELL WITH CAUTION",

    "decision_score":
        72.02,

    "risk_score":
        41.77,

    "risk_level":
        "MEDIUM",

    "confidence":
        76.96,

    "best_market":
        "Gandhinagar APMC",

    "net_profit":
        1000826.36,

}


AUCTION_RESULT = {

    "winner":
        "Buyer_01865",

    "buyer_name":
        "Buyer_01865",

    "winning_bid":
        2845.52,

}


RISK_RESULT = {

    "recommended_buyer":
        "Buyer_01865",

    "buyer_name":
        "Buyer_01865",

    "combined_risk":
        8.32,

    "risk_level":
        "LOW",

    "risk_aware_score":
        96.26,

}


PROFIT_RESULT = {

    "buyer_name":
        "Buyer_01865",

    "net_profit":
        -772634.03,

    "profitability":
        "NOT_PROFITABLE",

}


LOGISTICS_RESULT = {

    "destination":
        "Kheda",

    "best_destination":
        "Kheda",

    "transport_cost":
        369.25,

    "delay_hours":
        2.15,

    "damage_percentage":
        1.20,

    "logistics_risk":
        10.79,

    "logistics_score":
        93.65,

}


# ======================================================================
# HELPERS
# ======================================================================

def section(title):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def require(condition, message):

    if not condition:

        raise RuntimeError(
            message
        )


# ======================================================================
# MAIN TEST
# ======================================================================

def main():

    section(
        "FINAL AI RECOMMENDATION VERIFICATION"
    )

    print()
    print(
        "Testing the existing Final AI Recommendation layer."
    )

    print()
    print(
        "No new ML model."
    )

    print(
        "No new dataset."
    )

    print(
        "No model retraining."
    )

    print(
        "No dataset modification."
    )

    print(
        "No AI Agent."
    )


    # ==================================================================
    # LOAD ENGINE
    # ==================================================================

    section(
        "1. LOADING FINAL AI RECOMMENDATION ENGINE"
    )

    from final_ai_recommendation import (
        FinalAIRecommendationEngine
    )

    engine = (
        FinalAIRecommendationEngine()
    )

    print()
    print(
        "✓ Final AI Recommendation Engine loaded."
    )


    # ==================================================================
    # GENERATE RECOMMENDATION
    # ==================================================================

    section(
        "2. GENERATING FINAL RECOMMENDATION"
    )

    result = engine.generate(

        DECISION_RESULT,

        AUCTION_RESULT,

        RISK_RESULT,

        PROFIT_RESULT,

        LOGISTICS_RESULT,

    )

    require(

        isinstance(
            result,
            dict,
        ),

        "Final recommendation did not return a dictionary."

    )

    print()
    print(
        "✓ Recommendation generated."
    )


    # ==================================================================
    # REQUIRED FIELD CHECK
    # ==================================================================

    section(
        "3. REQUIRED FIELD VERIFICATION"
    )

    required_fields = [

        "sell_now_vs_wait",

        "choose_market",

        "choose_buyer",

        "expected_net_profit",

        "risk_level",

        "confidence",

        "reason",

    ]

    for field in required_fields:

        require(

            field in result,

            f"Missing required field: {field}"

        )

        value = result[field]

        require(

            value is not None,

            f"Field '{field}' contains None."

        )

        if isinstance(
            value,
            str,
        ):

            require(

                value.strip() != "",

                f"Field '{field}' is empty."

            )

        print(
            f"✓ {field} present."
        )


    # ==================================================================
    # SELL NOW VS WAIT
    # ==================================================================

    section(
        "4. SELL NOW VS WAIT VERIFICATION"
    )

    sell_wait = str(
        result[
            "sell_now_vs_wait"
        ]
    ).strip()

    valid_sell_wait_terms = [

        "SELL",

        "WAIT",

        "REASSESS",

    ]

    require(

        any(
            term in sell_wait.upper()
            for term in valid_sell_wait_terms
        ),

        f"Invalid Sell Now vs Wait recommendation: "
        f"{sell_wait}"

    )

    print(
        f"✓ Sell Now vs Wait : "
        f"{sell_wait}"
    )


    # ==================================================================
    # MARKET
    # ==================================================================

    section(
        "5. MARKET VERIFICATION"
    )

    market = str(
        result[
            "choose_market"
        ]
    ).strip()

    require(

        market.upper()
        != "NOT AVAILABLE",

        "Choose Market is unavailable."

    )

    print(
        f"✓ Choose Market : "
        f"{market}"
    )


    # ==================================================================
    # BUYER
    # ==================================================================

    section(
        "6. BUYER VERIFICATION"
    )

    buyer = str(
        result[
            "choose_buyer"
        ]
    ).strip()

    require(

        buyer.upper()
        != "NOT AVAILABLE",

        "Choose Buyer is unavailable."

    )

    print(
        f"✓ Choose Buyer : "
        f"{buyer}"
    )


    # ==================================================================
    # NET PROFIT
    # ==================================================================

    section(
        "7. EXPECTED NET PROFIT VERIFICATION"
    )

    net_profit = result[
        "expected_net_profit"
    ]

    require(

        isinstance(
            net_profit,
            (int, float),
        ),

        "Expected Net Profit is not numeric."

    )

    require(

        net_profit
        == net_profit,

        "Expected Net Profit is NaN."

    )

    print(
        f"✓ Expected Net Profit : "
        f"₹{net_profit:,.2f}"
    )


    # ==================================================================
    # PROFIT CONSISTENCY
    # ==================================================================

    section(
        "8. PROFITABILITY CONSISTENCY CHECK"
    )

    profitability = str(

        PROFIT_RESULT.get(
            "profitability",
            "",
        )

    ).upper()

    if net_profit < 0:

        require(

            "NOT_PROFITABLE"
            in profitability,

            "Negative net profit is inconsistent with "
            "the profitability status."

        )

        print(
            "✓ Negative net profit correctly "
            "identified as NOT_PROFITABLE."
        )

    elif net_profit > 0:

        print(
            "✓ Positive net profit detected."
        )

    else:

        print(
            "✓ Net profit is approximately zero."
        )


    # ==================================================================
    # RISK LEVEL
    # ==================================================================

    section(
        "9. RISK LEVEL VERIFICATION"
    )

    risk_level = str(
        result[
            "risk_level"
        ]
    ).strip().upper()

    valid_risk_levels = {

        "LOW",

        "MEDIUM",

        "HIGH",

    }

    require(

        risk_level in valid_risk_levels,

        f"Invalid risk level: {risk_level}"

    )

    print(
        f"✓ Risk Level : "
        f"{risk_level}"
    )


    # ==================================================================
    # CONFIDENCE
    # ==================================================================

    section(
        "10. CONFIDENCE VERIFICATION"
    )

    confidence = result[
        "confidence"
    ]

    require(

        isinstance(
            confidence,
            (int, float),
        ),

        "Confidence is not numeric."

    )

    require(

        0 <= confidence <= 100,

        f"Confidence outside valid range: "
        f"{confidence}"

    )

    print(
        f"✓ Confidence : "
        f"{confidence:.2f}%"
    )


    # ==================================================================
    # REASON
    # ==================================================================

    section(
        "11. REASON VERIFICATION"
    )

    reason = str(
        result[
            "reason"
        ]
    ).strip()

    require(

        len(reason) >= 20,

        "Reason is too short."

    )

    print(
        "✓ Reason is present."
    )

    print()
    print(
        "Reason:"
    )

    print(
        reason
    )


    # ==================================================================
    # REASON CONSISTENCY
    # ==================================================================

    section(
        "12. REASON CONSISTENCY CHECK"
    )

    reason_upper = reason.upper()

    # --------------------------------------------------------------
    # Negative profit consistency
    # --------------------------------------------------------------

    if net_profit < 0:

        require(

            (
                "NEGATIVE"
                in reason_upper
            )
            or
            (
                "NOT"
                in reason_upper
                and
                "PROFIT"
                in reason_upper
            )
            or
            (
                "₹"
                in reason
                and
                "PROFIT"
                in reason_upper
            ),

            "Reason does not acknowledge "
            "the negative net profit."

        )

        print(
            "✓ Reason acknowledges negative profit."
        )

    # --------------------------------------------------------------
    # Risk consistency
    # --------------------------------------------------------------

    require(

        risk_level
        in reason_upper,

        "Reason does not contain "
        "the selected risk level."

    )

    print(
        "✓ Reason contains selected risk level."
    )

    # --------------------------------------------------------------
    # Market consistency
    # --------------------------------------------------------------

    require(

        market.upper()
        in reason_upper,

        "Reason does not contain "
        "the selected market."

    )

    print(
        "✓ Reason contains selected market."
    )

    # --------------------------------------------------------------
    # Buyer consistency
    # --------------------------------------------------------------

    require(

        buyer.upper()
        in reason_upper,

        "Reason does not contain "
        "the selected buyer."

    )

    print(
        "✓ Reason contains selected buyer."
    )


    # ==================================================================
    # CONFIDENCE CONSISTENCY
    # ==================================================================

    section(
        "13. CONFIDENCE CONSISTENCY CHECK"
    )

    confidence_text = (
        f"{confidence:.2f}"
    )

    require(

        confidence_text
        in reason,

        "Reason does not contain "
        "the confidence value."

    )

    print(
        "✓ Confidence is reflected in reason."
    )


    # ==================================================================
    # FINAL OUTPUT VERIFICATION
    # ==================================================================

    section(
        "14. FINAL OUTPUT VERIFICATION"
    )

    print()

    print(
        f"Sell Now vs Wait     : "
        f"{sell_wait}"
    )

    print(
        f"Choose Market        : "
        f"{market}"
    )

    print(
        f"Choose Buyer         : "
        f"{buyer}"
    )

    print(
        f"Expected Net Profit  : "
        f"₹{net_profit:,.2f}"
    )

    print(
        f"Risk Level           : "
        f"{risk_level}"
    )

    print(
        f"Confidence           : "
        f"{confidence:.2f}%"
    )

    print(
        "Reason               : "
        f"{reason}"
    )


    # ==================================================================
    # FINAL STATUS
    # ==================================================================

    section(
        "FINAL AI RECOMMENDATION STATUS"
    )

    print(
        "✓ Sell Now vs Wait       : VERIFIED"
    )

    print(
        "✓ Choose Market          : VERIFIED"
    )

    print(
        "✓ Choose Buyer           : VERIFIED"
    )

    print(
        "✓ Expected Net Profit    : VERIFIED"
    )

    print(
        "✓ Risk Level             : VERIFIED"
    )

    print(
        "✓ Confidence             : VERIFIED"
    )

    print(
        "✓ Reason                 : VERIFIED"
    )

    print()

    print("=" * 70)

    print(
        "✓ FINAL AI RECOMMENDATION FULLY VERIFIED"
    )

    print("=" * 70)

    print()

    print(
        "✓ All 7 required recommendation outputs "
        "are valid."
    )

    print(
        "✓ Profit consistency verified."
    )

    print(
        "✓ Risk consistency verified."
    )

    print(
        "✓ Market consistency verified."
    )

    print(
        "✓ Buyer consistency verified."
    )

    print(
        "✓ Confidence consistency verified."
    )

    print(
        "✓ Reason consistency verified."
    )

    print()

    print(
        "FINAL AI RECOMMENDATION STATUS: VERIFIED"
    )


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print(
            "✗ Verification interrupted by user."
        )

        sys.exit(130)

    except Exception as exc:

        print()
        print("=" * 70)
        print(
            "✗ FINAL AI RECOMMENDATION VERIFICATION FAILED"
        )
        print("=" * 70)

        print()
        print(
            f"{type(exc).__name__}: {exc}"
        )

        print()

        traceback.print_exc()

        sys.exit(1)