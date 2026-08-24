"""
======================================================================
CONFIDENCE SCORE ENGINE
======================================================================

Purpose:
    Calculate confidence in the final agricultural recommendation
    using the already-generated ML predictions and decision signals.

NO MODEL RETRAINING
NO NEW ML MODEL
NO FAKE PREDICTIONS

Confidence is a decision-layer metric.
======================================================================
"""

from typing import Dict, Any


class ConfidenceScoreEngine:

    def __init__(self):

        print("\n")
        print("=" * 70)
        print("CONFIDENCE SCORE ENGINE")
        print("=" * 70)

        print(
            "\n✓ Confidence engine initialized."
        )

    # ==================================================================
    # HELPERS
    # ==================================================================

    @staticmethod
    def _number(
        value,
        default=0.0
    ):

        try:

            value = float(value)

            if value != value:
                return default

            return value

        except (
            TypeError,
            ValueError
        ):

            return default

    @staticmethod
    def _clamp(
        value,
        minimum=0.0,
        maximum=100.0
    ):

        return max(
            minimum,
            min(
                maximum,
                value
            )
        )

    # ==================================================================
    # CONFIDENCE COMPONENTS
    # ==================================================================

    def _price_confidence(
        self,
        price_score
    ):

        price_score = self._number(
            price_score
        )

        # Distance from neutral is a stronger signal.
        confidence = (
            50.0
            +
            abs(price_score - 50.0)
        )

        return self._clamp(
            confidence
        )

    def _demand_confidence(
        self,
        demand_score
    ):

        demand_score = self._number(
            demand_score
        )

        confidence = (
            50.0
            +
            abs(demand_score - 50.0)
        )

        return self._clamp(
            confidence
        )

    def _quality_confidence(
        self,
        quality_score
    ):

        quality_score = self._number(
            quality_score
        )

        # Very low/high quality gives a stronger signal.
        confidence = (
            50.0
            +
            abs(quality_score - 50.0)
        )

        return self._clamp(
            confidence
        )

    def _buyer_confidence(
        self,
        buyer_reliability
    ):

        reliability = str(
            buyer_reliability
        ).strip().upper()

        mapping = {

            "RELIABLE": 95.0,
            "MODERATE": 65.0,
            "UNRELIABLE": 25.0,

        }

        return mapping.get(
            reliability,
            50.0
        )

    def _risk_confidence(
        self,
        risk_score
    ):

        risk_score = self._number(
            risk_score
        )

        # Lower risk gives higher confidence.
        return self._clamp(
            100.0 - risk_score
        )

    def _financial_confidence(
        self,
        margin_percentage
    ):

        margin_percentage = self._number(
            margin_percentage
        )

        if margin_percentage <= 0:

            return 20.0

        if margin_percentage >= 30:

            return 95.0

        return self._clamp(
            50.0
            +
            margin_percentage
            * 1.5
        )

    def _market_confidence(
        self,
        market_score
    ):

        market_score = self._number(
            market_score
        )

        return self._clamp(
            market_score
        )

    # ==================================================================
    # MAIN CALCULATION
    # ==================================================================

    def calculate(
        self,
        decision: Dict[str, Any]
    ):

        print("\n")
        print("=" * 70)
        print("CALCULATING DECISION CONFIDENCE")
        print("=" * 70)

        # --------------------------------------------------------------
        # Read existing decision signals
        # --------------------------------------------------------------

        price_score = self._number(
            decision.get(
                "price_score",
                decision.get(
                    "price",
                    50
                )
            )
        )

        demand_score = self._number(
            decision.get(
                "demand_score",
                decision.get(
                    "demand",
                    50
                )
            )
        )

        quality_score = self._number(
            decision.get(
                "quality_score",
                50
            )
        )

        buyer_reliability = decision.get(
            "buyer_reliability",
            "MODERATE"
        )

        risk_score = self._number(
            decision.get(
                "risk_score",
                50
            )
        )

        margin_percentage = self._number(
            decision.get(
                "margin_percentage",
                0
            )
        )

        market_score = self._number(
            decision.get(
                "market_score",
                decision.get(
                    "risk_adjusted_score",
                    50
                )
            )
        )

        # --------------------------------------------------------------
        # Individual confidence signals
        # --------------------------------------------------------------

        price_confidence = (
            self._price_confidence(
                price_score
            )
        )

        demand_confidence = (
            self._demand_confidence(
                demand_score
            )
        )

        quality_confidence = (
            self._quality_confidence(
                quality_score
            )
        )

        buyer_confidence = (
            self._buyer_confidence(
                buyer_reliability
            )
        )

        risk_confidence = (
            self._risk_confidence(
                risk_score
            )
        )

        financial_confidence = (
            self._financial_confidence(
                margin_percentage
            )
        )

        market_confidence = (
            self._market_confidence(
                market_score
            )
        )

        # --------------------------------------------------------------
        # Weighted confidence
        #
        # Financial outcome is intentionally important.
        # Risk is also important.
        # --------------------------------------------------------------

        confidence = (

            price_confidence
            * 0.15

            +

            demand_confidence
            * 0.10

            +

            quality_confidence
            * 0.10

            +

            buyer_confidence
            * 0.15

            +

            risk_confidence
            * 0.20

            +

            financial_confidence
            * 0.20

            +

            market_confidence
            * 0.10

        )

        confidence = self._clamp(
            confidence
        )

        # --------------------------------------------------------------
        # Confidence label
        # --------------------------------------------------------------

        if confidence >= 85:

            level = "VERY HIGH"

        elif confidence >= 70:

            level = "HIGH"

        elif confidence >= 55:

            level = "MODERATE"

        elif confidence >= 40:

            level = "LOW"

        else:

            level = "VERY LOW"

        # --------------------------------------------------------------
        # Strengths / uncertainties
        # --------------------------------------------------------------

        strengths = []

        uncertainties = []

        if price_score >= 70:

            strengths.append(
                "strong price signal"
            )

        elif price_score <= 30:

            uncertainties.append(
                "weak price signal"
            )

        if demand_score >= 70:

            strengths.append(
                "strong demand signal"
            )

        elif demand_score <= 30:

            uncertainties.append(
                "weak demand signal"
            )

        if quality_score >= 70:

            strengths.append(
                "good crop quality"
            )

        elif quality_score < 50:

            uncertainties.append(
                "moderate or low crop quality"
            )

        if str(
            buyer_reliability
        ).strip().upper() == "RELIABLE":

            strengths.append(
                "reliable buyer"
            )

        elif str(
            buyer_reliability
        ).strip().upper() == "UNRELIABLE":

            uncertainties.append(
                "unreliable buyer"
            )

        if risk_score <= 30:

            strengths.append(
                "low overall risk"
            )

        elif risk_score >= 70:

            uncertainties.append(
                "high overall risk"
            )

        if margin_percentage > 20:

            strengths.append(
                "strong financial margin"
            )

        elif margin_percentage <= 0:

            uncertainties.append(
                "negative financial margin"
            )

        if market_score >= 75:

            strengths.append(
                "strong market opportunity"
            )

        elif market_score < 50:

            uncertainties.append(
                "weak market opportunity"
            )

        # --------------------------------------------------------------
        # Display
        # --------------------------------------------------------------

        print(
            f"\nPrice confidence    : "
            f"{price_confidence:.2f}"
        )

        print(
            f"Demand confidence   : "
            f"{demand_confidence:.2f}"
        )

        print(
            f"Quality confidence  : "
            f"{quality_confidence:.2f}"
        )

        print(
            f"Buyer confidence    : "
            f"{buyer_confidence:.2f}"
        )

        print(
            f"Risk confidence     : "
            f"{risk_confidence:.2f}"
        )

        print(
            f"Financial confidence: "
            f"{financial_confidence:.2f}"
        )

        print(
            f"Market confidence   : "
            f"{market_confidence:.2f}"
        )

        print("\n")
        print("=" * 70)
        print("FINAL CONFIDENCE")
        print("=" * 70)

        print(
            f"\nConfidence : "
            f"{confidence:.2f}%"
        )

        print(
            f"Level      : "
            f"{level}"
        )

        print("\nSTRENGTHS")
        print("-" * 70)

        if strengths:

            for item in strengths:

                print(
                    f"✓ {item}"
                )

        else:

            print(
                "No strong signals identified."
            )

        print("\nUNCERTAINTIES")
        print("-" * 70)

        if uncertainties:

            for item in uncertainties:

                print(
                    f"⚠ {item}"
                )

        else:

            print(
                "No major uncertainties identified."
            )

        return {

            "confidence_score":
                round(
                    confidence,
                    2
                ),

            "confidence_level":
                level,

            "strengths":
                strengths,

            "uncertainties":
                uncertainties,

            "components": {

                "price":
                    round(
                        price_confidence,
                        2
                    ),

                "demand":
                    round(
                        demand_confidence,
                        2
                    ),

                "quality":
                    round(
                        quality_confidence,
                        2
                    ),

                "buyer":
                    round(
                        buyer_confidence,
                        2
                    ),

                "risk":
                    round(
                        risk_confidence,
                        2
                    ),

                "financial":
                    round(
                        financial_confidence,
                        2
                    ),

                "market":
                    round(
                        market_confidence,
                        2
                    ),
            }
        }


# ======================================================================
# TEST
# ======================================================================

def main():

    print("\n")
    print("=" * 70)
    print("CONFIDENCE SCORE TEST")
    print("=" * 70)

    engine = ConfidenceScoreEngine()

    # --------------------------------------------------------------
    # These are the REAL decision values from your completed
    # Decision Intelligence test.
    #
    # They are inputs to the confidence layer, NOT new predictions.
    # --------------------------------------------------------------

    decision = {

        "price_score":
            85.0,

        "demand_score":
            85.0,

        "quality_score":
            65.28,

        "buyer_reliability":
            "RELIABLE",

        "risk_score":
            31.73,

        "margin_percentage":
            14.86,

        "risk_adjusted_score":
            88.03,
    }

    result = engine.calculate(
        decision
    )

    print("\n")
    print("=" * 70)
    print("CONFIDENCE SCORE TEST COMPLETED")
    print("=" * 70)

    print(
        f"\n✓ Confidence : "
        f"{result['confidence_score']:.2f}%"
    )

    print(
        f"✓ Level : "
        f"{result['confidence_level']}"
    )

    print(
        "\n✓ Existing decision signals used."
    )

    print(
        "✓ No ML model retrained."
    )

    print(
        "✓ No fake predictions generated."
    )


# ======================================================================
# RUN
# ======================================================================

if __name__ == "__main__":

    main()