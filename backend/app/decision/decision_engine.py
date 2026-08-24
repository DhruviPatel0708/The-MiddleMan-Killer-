"""
======================================================================
AGRICULTURE AI - DECISION INTELLIGENCE ENGINE
======================================================================

FINAL UNIFIED DECISION ENGINE

Integrated Modules
------------------
✓ Financial Analysis
✓ Risk Analysis
✓ Recommendation Logic
✓ Risk Adjusted Best Market
✓ What-If Scenario Analysis
✓ Confidence Score

IMPORTANT
---------
No ML model is trained here.
No fake predictions are generated.
Only existing trained models and prediction outputs are used.
======================================================================
"""

from pathlib import Path
import sys
from typing import Dict, Any, Optional


# ======================================================================
# PATH
# ======================================================================

CURRENT_DIR = Path(__file__).resolve().parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))


# ======================================================================
# IMPORT DECISION MODULES
# ======================================================================

from what_if import WhatIfEngine
from confidence_score import ConfidenceScoreEngine

try:

    from risk_adjusted_market import RiskAdjustedMarketOptimizer

    MARKET_AVAILABLE = True

except Exception:

    MARKET_AVAILABLE = False
    RiskAdjustedMarketOptimizer = None


# ======================================================================
# DECISION ENGINE
# ======================================================================

class DecisionIntelligenceEngine:

    def __init__(self):

        print("\n")
        print("=" * 70)
        print("DECISION INTELLIGENCE ENGINE")
        print("=" * 70)

        self.what_if_engine = WhatIfEngine()

        self.confidence_engine = ConfidenceScoreEngine()

        self.market_optimizer = None

        if MARKET_AVAILABLE:

            try:

                self.market_optimizer = RiskAdjustedMarketOptimizer()

                print("✓ Risk-adjusted market optimizer loaded.")

            except Exception as e:

                print(f"⚠ Market optimizer unavailable: {e}")

        print("\n✓ Decision engine initialized.")
        print("✓ Ready to process ML predictions.")

    # ==================================================================
    # HELPERS
    # ==================================================================

    @staticmethod
    def _safe_float(value, default=0.0):

        try:

            value = float(value)

            if value != value:
                return default

            return value

        except Exception:

            return default

    @staticmethod
    def _clamp(value, minimum=0.0, maximum=100.0):

        return max(minimum, min(maximum, value))

    # ==================================================================
    # SCORE FUNCTIONS
    # ==================================================================

    def price_score(self, agreed_price, market_price):

        agreed_price = self._safe_float(agreed_price)
        market_price = self._safe_float(market_price)

        if market_price <= 0:
            return 50.0

        ratio = agreed_price / market_price

        if ratio >= 1.05:
            return 100.0

        if ratio >= 1.00:
            return 90.0

        if ratio >= 0.97:
            return 85.0

        if ratio >= 0.94:
            return 70.0

        if ratio >= 0.90:
            return 55.0

        return 35.0

    def demand_score(self, demand):

        demand = self._safe_float(demand)

        if demand >= 120:
            return 100.0

        if demand >= 90:
            return 85.0

        if demand >= 70:
            return 70.0

        if demand >= 40:
            return 50.0

        return 30.0

    def quality_score(self, quality):

        return self._clamp(self._safe_float(quality, 50))

    def spoilage_score(self, spoilage):

        spoilage = self._safe_float(spoilage, 50)

        return self._clamp(100 - spoilage)

    def buyer_score(self, reliability):

        reliability = str(reliability).upper()

        mapping = {
            "RELIABLE": 100,
            "MODERATE": 60,
            "UNRELIABLE": 20
        }

        return mapping.get(reliability, 50)

    def payment_score(self, status):

        status = str(status).upper()

        mapping = {
            "PAID": 100,
            "PENDING": 50,
            "LATE": 20
        }

        return mapping.get(status, 50)

    def delivery_score(self, status):

        status = str(status).upper()

        mapping = {
            "DELIVERED": 100,
            "DELAYED": 35,
            "CANCELLED": 5
        }

        return mapping.get(status, 50)

    def logistics_score(self, transport_cost, delay, damage):

        transport_cost = self._safe_float(transport_cost)
        delay = self._safe_float(delay)
        damage = self._safe_float(damage)

        transport_component = self._clamp(100 - transport_cost / 100)
        delay_component = self._clamp(100 - delay * 4)
        damage_component = self._clamp(100 - damage * 8)

        score = (
            transport_component * 0.35
            + delay_component * 0.35
            + damage_component * 0.30
        )

        return self._clamp(score)

    def financial_score(self, margin_percentage):

        margin_percentage = self._safe_float(margin_percentage)

        if margin_percentage <= 0:
            return 0

        if margin_percentage >= 30:
            return 100

        if margin_percentage >= 20:
            return 90

        if margin_percentage >= 15:
            return 80

        if margin_percentage >= 10:
            return 75

        if margin_percentage >= 5:
            return 60

        return 40

    # ==================================================================
    # RISK
    # ==================================================================

    def calculate_risk(
        self,
        spoilage,
        buyer,
        payment,
        delivery,
        logistics
    ):

        spoilage_risk = 100 - spoilage
        buyer_risk = 100 - buyer
        payment_risk = 100 - payment
        delivery_risk = 100 - delivery
        logistics_risk = 100 - logistics

        risk = (
            spoilage_risk * 0.25
            + buyer_risk * 0.15
            + payment_risk * 0.20
            + delivery_risk * 0.25
            + logistics_risk * 0.15
        )

        return self._clamp(risk)

    def risk_level(self, risk):

        if risk <= 30:
            return "LOW"

        if risk <= 60:
            return "MEDIUM"

        return "HIGH"

    # ==================================================================
    # RECOMMENDATION
    # ==================================================================

    def recommendation(
        self,
        decision_score,
        risk_score,
        margin,
        margin_percentage
    ):

        if margin <= 0:
            return "WAIT / FIND BETTER PRICE"

        if risk_score >= 70:

            if decision_score >= 70:
                return "SELL WITH HIGH RISK"

            return "WAIT / FIND SAFER OPTION"

        if decision_score >= 80 and margin_percentage >= 15:
            return "SELL NOW"

        if decision_score >= 60:
            return "SELL WITH CAUTION"

        return "WAIT / FIND BETTER PRICE"

    # ==================================================================
    # SELL NOW VS WAIT
    # ==================================================================

    def sell_now_vs_wait(
        self,
        recommendation,
        margin,
        margin_percentage,
        risk_score,
        decision_score
    ):
        """Return the existing architecture's explicit sell/wait decision.

        Uses only signals already calculated by this Decision Intelligence
        Engine. No new model or external data is introduced.
        """

        margin = self._safe_float(margin)
        margin_percentage = self._safe_float(margin_percentage)
        risk_score = self._safe_float(risk_score)
        decision_score = self._safe_float(decision_score)
        recommendation = str(recommendation).upper().strip()

        if margin <= 0:
            return "WAIT"

        if risk_score >= 70:
            return "WAIT"

        if (
            recommendation == "SELL NOW"
            and decision_score >= 80
            and margin_percentage >= 15
        ):
            return "SELL NOW"

        if recommendation == "SELL WITH CAUTION":
            return "SELL NOW WITH CAUTION"

        if recommendation == "SELL WITH HIGH RISK":
            return "WAIT"

        if recommendation.startswith("WAIT"):
            return "WAIT"

        return "WAIT"

    # ==================================================================
    # STRENGTHS
    # ==================================================================

    def get_strengths(self, scores):

        strengths = []

        if scores["price"] >= 70:
            strengths.append("favorable market price")

        if scores["demand"] >= 70:
            strengths.append("strong demand")

        if scores["buyer"] >= 80:
            strengths.append("reliable buyer")

        if scores["payment"] >= 80:
            strengths.append("secure payment")

        if scores["financial"] >= 75:
            strengths.append("positive financial outcome")

        return strengths

    # ==================================================================
    # CONCERNS
    # ==================================================================

    def get_concerns(self, scores, margin):

        concerns = []

        if scores["quality"] < 70:
            concerns.append("crop quality is moderate or low")

        if scores["spoilage"] < 50:
            concerns.append("high spoilage risk")

        if scores["delivery"] < 60:
            concerns.append("delivery risk is elevated")

        if scores["logistics"] < 60:
            concerns.append("logistics risk is elevated")

        if margin <= 0:
            concerns.append("estimated financial margin is negative")

        return concerns

    # ==================================================================
    # MAIN DECISION
    # ==================================================================

    def make_decision(
        self,
        predictions: Dict[str, Any],
        input_data: Optional[Dict[str, Any]] = None
    ):

        if input_data is None:
            input_data = {}

        print("\n")
        print("=" * 70)
        print("FINAL DECISION")
        print("=" * 70)

        # --------------------------------------------------------------
        # INPUT VALUES
        # --------------------------------------------------------------

        quantity = self._safe_float(
            input_data.get(
                "quantity_kg",
                predictions.get("quantity_kg", 0)
            )
        )

        agreed_price = self._safe_float(
            input_data.get(
                "agreed_price_per_kg",
                predictions.get("agreed_price_per_kg", 0)
            )
        )

        market_price = self._safe_float(
            input_data.get(
                "market_price_per_kg",
                predictions.get("market_price_per_kg", 0)
            )
        )

        crop = input_data.get(
            "crop",
            predictions.get("crop", None)
        )

        origin_district = input_data.get(
            "origin_district",
            predictions.get("origin_district", None)
        )

        # --------------------------------------------------------------
        # ML OUTPUTS
        # --------------------------------------------------------------

        predicted_price = self._safe_float(
            predictions.get("price_prediction", 0)
        )

        demand = self._safe_float(
            predictions.get("demand_prediction", 0)
        )

        buyer_reliability = predictions.get(
            "buyer_reliability",
            "MODERATE"
        )

        quality = self._safe_float(
            predictions.get("quality_score", 50)
        )

        spoilage = self._safe_float(
            predictions.get("spoilage_risk_score", 50)
        )

        transport_cost = self._safe_float(
            predictions.get("transport_cost", 0)
        )

        delay_hours = self._safe_float(
            predictions.get("delay_hours", 0)
        )

        damage_percentage = self._safe_float(
            predictions.get("damage_percentage", 0)
        )

        estimated_cost = self._safe_float(
            predictions.get("estimated_total_cost", 0)
        )

        payment_risk = predictions.get(
            "payment_risk",
            "Paid"
        )

        delivery_risk = predictions.get(
            "delivery_risk",
            "Delivered"
        )

        # --------------------------------------------------------------
        # PRICE USED
        # --------------------------------------------------------------

        if agreed_price > 0:

            price_used = agreed_price
            price_source = "agreed_price"

        elif market_price > 0:

            price_used = market_price
            price_source = "market_price"

        else:

            price_used = predicted_price
            price_source = "predicted_price"

        # --------------------------------------------------------------
        # FINANCIAL
        # --------------------------------------------------------------

        expected_revenue = quantity * price_used

        estimated_margin = expected_revenue - estimated_cost

        margin_percentage = 0

        if expected_revenue > 0:

            margin_percentage = (
                estimated_margin
                / expected_revenue
                * 100
            )

        # --------------------------------------------------------------
        # SCORES
        # --------------------------------------------------------------

        scores = {

            "price": self.price_score(
                agreed_price,
                market_price
            ),

            "demand": self.demand_score(demand),

            "quality": self.quality_score(quality),

            "spoilage": self.spoilage_score(spoilage),

            "buyer": self.buyer_score(buyer_reliability),

            "payment": self.payment_score(payment_risk),

            "delivery": self.delivery_score(delivery_risk),

            "logistics": self.logistics_score(
                transport_cost,
                delay_hours,
                damage_percentage
            ),

            "financial": self.financial_score(
                margin_percentage
            )
        }

        # --------------------------------------------------------------
        # DECISION SCORE
        # --------------------------------------------------------------

        decision_score = (
            scores["price"] * 0.15
            + scores["demand"] * 0.15
            + scores["quality"] * 0.10
            + scores["spoilage"] * 0.10
            + scores["buyer"] * 0.10
            + scores["payment"] * 0.10
            + scores["delivery"] * 0.10
            + scores["logistics"] * 0.05
            + scores["financial"] * 0.15
        )

        decision_score = self._clamp(decision_score)

        # --------------------------------------------------------------
        # RISK
        # --------------------------------------------------------------

        risk_score = self.calculate_risk(
            scores["spoilage"],
            scores["buyer"],
            scores["payment"],
            scores["delivery"],
            scores["logistics"]
        )

        risk_level = self.risk_level(risk_score)

        recommendation = self.recommendation(
            decision_score,
            risk_score,
            estimated_margin,
            margin_percentage
        )

        sell_now_vs_wait = self.sell_now_vs_wait(
            recommendation=recommendation,
            margin=estimated_margin,
            margin_percentage=margin_percentage,
            risk_score=risk_score,
            decision_score=decision_score
        )

        strengths = self.get_strengths(scores)
        concerns = self.get_concerns(scores, estimated_margin)

        # --------------------------------------------------------------
        # BASE RESULT
        # --------------------------------------------------------------

        decision = {

            "recommendation": recommendation,

            "decision_score": round(decision_score, 2),

            "risk_score": round(risk_score, 2),

            "risk_level": risk_level,

            "price_used": round(price_used, 2),

            "price_source": price_source,

            "quantity_kg": round(quantity, 2),

            "expected_revenue": round(expected_revenue, 2),

            "estimated_cost": round(estimated_cost, 2),

            "estimated_margin": round(estimated_margin, 2),

            "net_profit": round(estimated_margin, 2),

            "margin_percentage": round(margin_percentage, 2),

            "sell_now_vs_wait": sell_now_vs_wait,

            "scores": {
                k: round(v, 2)
                for k, v in scores.items()
            },

            "strengths": strengths,

            "concerns": concerns,

            "crop": crop,

            "origin_district": origin_district,

            "best_market": None,

            "best_market_district": None,

            "best_market_score": None,

            "risk_adjusted_margin": None,

            "what_if": None,

            "confidence_score": None,

            "confidence_level": None,

            "confidence_strengths": [],

            "confidence_uncertainties": [],

            "confidence_components": {}
        }

        # --------------------------------------------------------------
        # DISPLAY BASE RESULT
        # --------------------------------------------------------------

        print(f"\nRecommendation : {recommendation}")
        print(f"Decision Score : {decision_score:.2f}/100")
        print(f"Risk Score     : {risk_score:.2f}/100")
        print(f"Risk Level     : {risk_level}")

        print("\nFINANCIAL")
        print("-" * 70)

        print(f"Price Used       : ₹{price_used:,.2f}/kg")
        print(f"Price Source     : {price_source}")
        print(f"Quantity         : {quantity:,.2f} kg")
        print(f"Expected Revenue : ₹{expected_revenue:,.2f}")
        print(f"Estimated Cost   : ₹{estimated_cost:,.2f}")
        print(f"Estimated Margin : ₹{estimated_margin:,.2f}")
        print(f"Net Profit       : ₹{estimated_margin:,.2f}")
        print(f"Margin %         : {margin_percentage:.2f}%")
        print(f"Sell Now vs Wait : {sell_now_vs_wait}")

        # --------------------------------------------------------------
        # BEST MARKET
        # --------------------------------------------------------------

        market_result = None

        if (
            self.market_optimizer is not None
            and crop
            and origin_district
        ):

            try:

                market_result = self.market_optimizer.recommend(
                    crop=crop,
                    quantity_kg=quantity,
                    origin_district=origin_district,
                    top_n=5
                )

                decision["best_market"] = market_result.get(
                    "best_market"
                )

                decision["best_market_district"] = market_result.get(
                    "best_district"
                )

                decision["best_market_score"] = market_result.get(
                    "risk_adjusted_score"
                )

                decision["risk_adjusted_margin"] = market_result.get(
                    "risk_adjusted_margin"
                )

            except Exception as e:

                print(f"\n⚠ Best market skipped: {e}")

        # --------------------------------------------------------------
        # WHAT IF
        # --------------------------------------------------------------

        try:

            what_if_input = {

                "quantity_kg": quantity,

                "price_per_kg": price_used,

                "estimated_total_cost": estimated_cost,

                "transport_cost": transport_cost,

                "damage_percentage": damage_percentage,

                "delay_hours": delay_hours,

                "payment_risk": payment_risk,

                "delivery_risk": delivery_risk
            }

            decision["what_if"] = self.what_if_engine.analyze(
                what_if_input
            )

        except Exception as e:

            print(f"\n⚠ What-If failed: {e}")

        # --------------------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------------------

        try:

            confidence_input = {

                "price_score": scores["price"],

                "demand_score": scores["demand"],

                "quality_score": scores["quality"],

                "buyer_reliability": buyer_reliability,

                "risk_score": risk_score,

                "margin_percentage": margin_percentage,

                "risk_adjusted_score":
                    decision["best_market_score"]
                    if decision["best_market_score"] is not None
                    else 50
            }

            confidence = self.confidence_engine.calculate(
                confidence_input
            )

            decision["confidence_score"] = confidence.get(
                "confidence_score"
            )

            decision["confidence_level"] = confidence.get(
                "confidence_level"
            )

            decision["confidence_strengths"] = confidence.get(
                "strengths"
            )

            decision["confidence_uncertainties"] = confidence.get(
                "uncertainties"
            )

            decision["confidence_components"] = confidence.get(
                "components"
            )

        except Exception as e:

            print(f"\n⚠ Confidence failed: {e}")

        # --------------------------------------------------------------
        # FINAL DISPLAY
        # --------------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("FINAL DECISION INTELLIGENCE")
        print("=" * 70)

        print(f"\nRecommendation : {decision['recommendation']}")
        print(f"Decision Score : {decision['decision_score']:.2f}/100")
        print(f"Risk Score     : {decision['risk_score']:.2f}/100")
        print(f"Risk Level     : {decision['risk_level']}")

        if decision["confidence_score"] is not None:

            print(
                f"Confidence     : "
                f"{decision['confidence_score']:.2f}%"
            )

            print(
                f"Confidence Level : "
                f"{decision['confidence_level']}"
            )

        if decision["best_market"] is not None:

            market_score = self._safe_float(
                decision["best_market_score"]
            )

            print(
                f"Best Market    : "
                f"{decision['best_market']}"
            )

            print(
                f"District       : "
                f"{decision['best_market_district']}"
            )

            print(
                f"Market Score   : "
                f"{market_score:.2f}/100"
            )

        print(
            f"\nExpected Revenue : "
            f"₹{decision['expected_revenue']:,.2f}"
        )

        print(
            f"Estimated Cost   : "
            f"₹{decision['estimated_cost']:,.2f}"
        )

        print(
            f"Expected Margin  : "
            f"₹{decision['estimated_margin']:,.2f}"
        )

        print(
            f"Margin %         : "
            f"{decision['margin_percentage']:.2f}%"
        )

        print(
            f"Net Profit       : "
            f"₹{decision['net_profit']:,.2f}"
        )

        print(
            f"Sell Now vs Wait : "
            f"{decision['sell_now_vs_wait']}"
        )

        print("\n✓ Final unified decision generated.")

        return decision

    # ==================================================================
    # COMPATIBILITY METHOD
    # ==================================================================

    def enrich_decision(
        self,
        decision: Dict[str, Any],
        predictions: Dict[str, Any],
        market_result: Optional[Dict[str, Any]] = None
    ):

        what_if_input = {

            "quantity_kg":
                predictions.get(
                    "quantity_kg",
                    decision.get("quantity_kg", 0)
                ),

            "price_per_kg":
                decision.get(
                    "price_used",
                    predictions.get(
                        "agreed_price_per_kg",
                        0
                    )
                ),

            "estimated_total_cost":
                decision.get(
                    "estimated_cost",
                    predictions.get(
                        "estimated_total_cost",
                        0
                    )
                ),

            "transport_cost":
                predictions.get("transport_cost", 0),

            "damage_percentage":
                predictions.get("damage_percentage", 0),

            "delay_hours":
                predictions.get("delay_hours", 0),

            "payment_risk":
                predictions.get("payment_risk", "Paid"),

            "delivery_risk":
                predictions.get("delivery_risk", "Delivered")
        }

        decision["what_if"] = self.what_if_engine.analyze(
            what_if_input
        )

        decision["net_profit"] = self._safe_float(
            decision.get(
                "net_profit",
                decision.get("estimated_margin", 0)
            )
        )

        decision["sell_now_vs_wait"] = self.sell_now_vs_wait(
            recommendation=decision.get(
                "recommendation",
                "WAIT / FIND BETTER PRICE"
            ),
            margin=decision.get(
                "net_profit",
                decision.get("estimated_margin", 0)
            ),
            margin_percentage=decision.get(
                "margin_percentage",
                0
            ),
            risk_score=decision.get(
                "risk_score",
                50
            ),
            decision_score=decision.get(
                "decision_score",
                50
            )
        )

        if market_result:

            decision["best_market"] = market_result.get(
                "best_market"
            )

            decision["best_market_district"] = market_result.get(
                "best_district"
            )

            decision["best_market_score"] = market_result.get(
                "risk_adjusted_score"
            )

            decision["risk_adjusted_margin"] = market_result.get(
                "risk_adjusted_margin"
            )

        confidence_input = {

            "price_score":
                decision.get(
                    "price_score",
                    decision.get("scores", {}).get("price", 50)
                ),

            "demand_score":
                decision.get(
                    "demand_score",
                    decision.get("scores", {}).get("demand", 50)
                ),

            "quality_score":
                predictions.get("quality_score", 50),

            "buyer_reliability":
                predictions.get(
                    "buyer_reliability",
                    "MODERATE"
                ),

            "risk_score":
                decision.get("risk_score", 50),

            "margin_percentage":
                decision.get("margin_percentage", 0),

            "risk_adjusted_score":
                decision.get("best_market_score", 50)
                if decision.get("best_market_score") is not None
                else 50
        }

        confidence = self.confidence_engine.calculate(
            confidence_input
        )

        decision["confidence_score"] = confidence.get(
            "confidence_score"
        )

        decision["confidence_level"] = confidence.get(
            "confidence_level"
        )

        decision["confidence_strengths"] = confidence.get(
            "strengths"
        )

        decision["confidence_uncertainties"] = confidence.get(
            "uncertainties"
        )

        decision["confidence_components"] = confidence.get(
            "components"
        )

        return decision


# ======================================================================
# STANDALONE TEST
# ======================================================================

def main():

    print("\n")
    print("=" * 70)
    print("DECISION INTELLIGENCE ENGINE TEST")
    print("=" * 70)

    engine = DecisionIntelligenceEngine()

    predictions = {

        "price_prediction": 2973.07,

        "demand_prediction": 92.02,

        "buyer_reliability": "RELIABLE",

        "quality_score": 65.28,

        "quality_grade": "C",

        "spoilage_risk_score": 74.89,

        "spoilage_risk": "HIGH",

        "transport_cost": 6438.86,

        "delay_hours": 10.27,

        "damage_percentage": 3.50,

        "estimated_total_cost": 5733135.72,

        "payment_risk": "Paid",

        "delivery_risk": "Delayed",

        "quantity_kg": 887,

        "agreed_price_per_kg": 7591.84,

        "market_price_per_kg": 7803.36,

        "crop": "Bajra",

        "origin_district": "Kheda"
    }

    input_data = {

        "crop": "Bajra",

        "quantity_kg": 887,

        "agreed_price_per_kg": 7591.84,

        "market_price_per_kg": 7803.36,

        "origin_district": "Kheda"
    }

    result = engine.make_decision(
        predictions,
        input_data
    )

    print("\n")
    print("=" * 70)
    print("DECISION ENGINE TEST COMPLETED")
    print("=" * 70)

    print("\n✓ Recommendation :", result["recommendation"])
    print("✓ Confidence     :", result["confidence_score"])
    print("✓ Risk Level     :", result["risk_level"])

    if result["best_market"]:

        print("✓ Best Market    :", result["best_market"])

    print("✓ Final integration successful.")


if __name__ == "__main__":
    main()
