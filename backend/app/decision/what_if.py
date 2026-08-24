"""
WHAT-IF / SCENARIO ANALYSIS ENGINE

Purpose:
    Evaluate alternative agricultural selling scenarios using the
    existing ML predictions.

NO MODEL RETRAINING
NO FAKE ML PREDICTIONS

The engine modifies decision assumptions only and recalculates the
financial/risk outcome.
"""

from dataclasses import dataclass
from typing import Dict, List


# ======================================================================
# SCENARIO RESULT
# ======================================================================

@dataclass
class ScenarioResult:

    name: str

    quantity_kg: float

    price_per_kg: float

    transport_cost: float

    damage_percentage: float

    delay_hours: float

    revenue: float

    damage_loss: float

    total_cost: float

    profit: float

    margin_percentage: float

    risk_score: float


# ======================================================================
# WHAT-IF ENGINE
# ======================================================================

class WhatIfEngine:

    def __init__(self):

        print("\n")
        print("=" * 70)
        print("WHAT-IF SCENARIO ENGINE")
        print("=" * 70)

        print(
            "\n✓ What-If engine initialized."
        )

    # ==================================================================
    # SAFE NUMBER
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

    # ==================================================================
    # CALCULATE RISK
    # ==================================================================

    def _calculate_risk(
        self,
        damage_percentage,
        delay_hours,
        payment_risk="Paid",
        delivery_risk="Delivered"
    ):

        # --------------------------------------------------------------
        # Damage contribution
        # --------------------------------------------------------------

        damage_risk = min(
            max(
                damage_percentage * 8.0,
                0.0
            ),
            40.0
        )

        # --------------------------------------------------------------
        # Delay contribution
        # --------------------------------------------------------------

        delay_risk = min(
            max(
                delay_hours * 2.0,
                0.0
            ),
            30.0
        )

        # --------------------------------------------------------------
        # Payment risk
        # --------------------------------------------------------------

        payment_penalty = {

            "Paid": 0.0,
            "Pending": 15.0,
            "Late": 25.0,

        }.get(
            str(payment_risk),
            10.0
        )

        # --------------------------------------------------------------
        # Delivery risk
        # --------------------------------------------------------------

        delivery_penalty = {

            "Delivered": 0.0,
            "Delayed": 15.0,
            "Cancelled": 30.0,

        }.get(
            str(delivery_risk),
            10.0
        )

        risk = (

            damage_risk
            +
            delay_risk
            +
            payment_penalty
            +
            delivery_penalty

        )

        return min(
            max(
                risk,
                0.0
            ),
            100.0
        )

    # ==================================================================
    # RUN ONE SCENARIO
    # ==================================================================

    def _run_scenario(
        self,
        name,
        quantity_kg,
        price_per_kg,
        estimated_total_cost,
        transport_cost,
        damage_percentage,
        delay_hours,
        payment_risk,
        delivery_risk
    ):

        quantity_kg = self._number(
            quantity_kg
        )

        price_per_kg = self._number(
            price_per_kg
        )

        estimated_total_cost = self._number(
            estimated_total_cost
        )

        transport_cost = self._number(
            transport_cost
        )

        damage_percentage = self._number(
            damage_percentage
        )

        delay_hours = self._number(
            delay_hours
        )

        # --------------------------------------------------------------
        # Revenue
        # --------------------------------------------------------------

        revenue = (
            quantity_kg
            *
            price_per_kg
        )

        # --------------------------------------------------------------
        # Damage loss
        # --------------------------------------------------------------

        damage_loss = (

            revenue
            *
            damage_percentage
            /
            100.0

        )

        # --------------------------------------------------------------
        # Cost
        #
        # The base cost model already contains logistics-related cost.
        # For what-if transport scenarios, only the change in transport
        # cost is added separately.
        # --------------------------------------------------------------

        total_cost = (
            estimated_total_cost
        )

        profit = (

            revenue
            -
            total_cost
            -
            damage_loss

        )

        # --------------------------------------------------------------
        # Margin
        # --------------------------------------------------------------

        if revenue > 0:

            margin_percentage = (

                profit
                /
                revenue
                *
                100.0

            )

        else:

            margin_percentage = 0.0

        # --------------------------------------------------------------
        # Risk
        # --------------------------------------------------------------

        risk_score = self._calculate_risk(

            damage_percentage=
                damage_percentage,

            delay_hours=
                delay_hours,

            payment_risk=
                payment_risk,

            delivery_risk=
                delivery_risk,
        )

        return ScenarioResult(

            name=name,

            quantity_kg=quantity_kg,

            price_per_kg=price_per_kg,

            transport_cost=transport_cost,

            damage_percentage=damage_percentage,

            delay_hours=delay_hours,

            revenue=revenue,

            damage_loss=damage_loss,

            total_cost=total_cost,

            profit=profit,

            margin_percentage=margin_percentage,

            risk_score=risk_score,
        )

    # ==================================================================
    # RUN ALL SCENARIOS
    # ==================================================================

    def analyze(
        self,
        predictions: Dict
    ):

        print("\n")
        print("=" * 70)
        print("RUNNING WHAT-IF ANALYSIS")
        print("=" * 70)

        # --------------------------------------------------------------
        # Read real prediction values
        # --------------------------------------------------------------

        quantity = self._number(
            predictions.get(
                "quantity_kg",
                0
            )
        )

        price = self._number(
            predictions.get(
                "price_per_kg",
                predictions.get(
                    "agreed_price_per_kg",
                    0
                )
            )
        )

        total_cost = self._number(
            predictions.get(
                "estimated_total_cost",
                0
            )
        )

        transport = self._number(
            predictions.get(
                "transport_cost",
                0
            )
        )

        damage = self._number(
            predictions.get(
                "damage_percentage",
                0
            )
        )

        delay = self._number(
            predictions.get(
                "delay_hours",
                0
            )
        )

        payment_risk = predictions.get(
            "payment_risk",
            "Paid"
        )

        delivery_risk = predictions.get(
            "delivery_risk",
            "Delivered"
        )

        if quantity <= 0:

            raise ValueError(
                "quantity_kg must be greater than zero."
            )

        if price <= 0:

            raise ValueError(
                "price_per_kg must be greater than zero."
            )

        # --------------------------------------------------------------
        # Current scenario
        # --------------------------------------------------------------

        scenarios: List[ScenarioResult] = []

        scenarios.append(

            self._run_scenario(

                name="CURRENT",

                quantity_kg=quantity,

                price_per_kg=price,

                estimated_total_cost=total_cost,

                transport_cost=transport,

                damage_percentage=damage,

                delay_hours=delay,

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Price +10%
        # --------------------------------------------------------------

        scenarios.append(

            self._run_scenario(

                name="PRICE +10%",

                quantity_kg=quantity,

                price_per_kg=price * 1.10,

                estimated_total_cost=total_cost,

                transport_cost=transport,

                damage_percentage=damage,

                delay_hours=delay,

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Price -10%
        # --------------------------------------------------------------

        scenarios.append(

            self._run_scenario(

                name="PRICE -10%",

                quantity_kg=quantity,

                price_per_kg=price * 0.90,

                estimated_total_cost=total_cost,

                transport_cost=transport,

                damage_percentage=damage,

                delay_hours=delay,

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Transport +15%
        # --------------------------------------------------------------

        scenarios.append(

            self._run_scenario(

                name="TRANSPORT COST +15%",

                quantity_kg=quantity,

                price_per_kg=price,

                estimated_total_cost=(
                    total_cost
                    +
                    transport * 0.15
                ),

                transport_cost=(
                    transport * 1.15
                ),

                damage_percentage=damage,

                delay_hours=delay,

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Damage +2 percentage points
        # --------------------------------------------------------------

        scenarios.append(

            self._run_scenario(

                name="DAMAGE +2%",

                quantity_kg=quantity,

                price_per_kg=price,

                estimated_total_cost=total_cost,

                transport_cost=transport,

                damage_percentage=(
                    damage + 2.0
                ),

                delay_hours=delay,

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Delay +5 hours
        # --------------------------------------------------------------

        scenarios.append(

            self._run_scenario(

                name="DELAY +5 HOURS",

                quantity_kg=quantity,

                price_per_kg=price,

                estimated_total_cost=total_cost,

                transport_cost=transport,

                damage_percentage=damage,

                delay_hours=(
                    delay + 5.0
                ),

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Quantity +20%
        # --------------------------------------------------------------

        scenarios.append(

            self._run_scenario(

                name="QUANTITY +20%",

                quantity_kg=(
                    quantity * 1.20
                ),

                price_per_kg=price,

                estimated_total_cost=(
                    total_cost * 1.20
                ),

                transport_cost=(
                    transport * 1.20
                ),

                damage_percentage=damage,

                delay_hours=delay,

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Quantity -20%
        # --------------------------------------------------------------

        scenarios.append(

            self._run_scenario(

                name="QUANTITY -20%",

                quantity_kg=(
                    quantity * 0.80
                ),

                price_per_kg=price,

                estimated_total_cost=(
                    total_cost * 0.80
                ),

                transport_cost=(
                    transport * 0.80
                ),

                damage_percentage=damage,

                delay_hours=delay,

                payment_risk=payment_risk,

                delivery_risk=delivery_risk,
            )
        )

        # --------------------------------------------------------------
        # Display compact results
        # --------------------------------------------------------------

        print("\n")
        print("=" * 70)
        print("WHAT-IF RESULTS")
        print("=" * 70)

        for scenario in scenarios:

            print(
                f"\n{scenario.name}"
            )

            print(
                f"  Revenue : "
                f"₹{scenario.revenue:,.2f}"
            )

            print(
                f"  Cost    : "
                f"₹{scenario.total_cost:,.2f}"
            )

            print(
                f"  Profit  : "
                f"₹{scenario.profit:,.2f}"
            )

            print(
                f"  Margin  : "
                f"{scenario.margin_percentage:.2f}%"
            )

            print(
                f"  Risk    : "
                f"{scenario.risk_score:.2f}/100"
            )

        # --------------------------------------------------------------
        # Compare with current
        # --------------------------------------------------------------

        current = scenarios[0]

        print("\n")
        print("=" * 70)
        print("SCENARIO IMPACT")
        print("=" * 70)

        for scenario in scenarios[1:]:

            profit_change = (
                scenario.profit
                -
                current.profit
            )

            risk_change = (
                scenario.risk_score
                -
                current.risk_score
            )

            print(
                f"\n{scenario.name}"
            )

            print(
                f"  Profit change : "
                f"₹{profit_change:,.2f}"
            )

            print(
                f"  Risk change   : "
                f"{risk_change:+.2f}"
            )

        # --------------------------------------------------------------
        # Best scenario
        # --------------------------------------------------------------

        best_profit = max(
            scenarios,
            key=lambda x: x.profit
        )

        lowest_risk = min(
            scenarios,
            key=lambda x: x.risk_score
        )

        print("\n")
        print("=" * 70)
        print("BEST SCENARIOS")
        print("=" * 70)

        print(
            f"\n✓ Highest profit:"
            f" {best_profit.name}"
        )

        print(
            f"  Profit:"
            f" ₹{best_profit.profit:,.2f}"
        )

        print(
            f"\n✓ Lowest risk:"
            f" {lowest_risk.name}"
        )

        print(
            f"  Risk:"
            f" {lowest_risk.risk_score:.2f}/100"
        )

        return {

            "current": current,

            "scenarios": scenarios,

            "highest_profit":
                best_profit,

            "lowest_risk":
                lowest_risk,
        }


# ======================================================================
# TEST
# ======================================================================

def main():

    print("\n")
    print("=" * 70)
    print("WHAT-IF ENGINE TEST")
    print("=" * 70)

    engine = WhatIfEngine()

    # --------------------------------------------------------------
    # Use values from your REAL end-to-end prediction output.
    #
    # These are inputs to the scenario calculator, not new ML
    # predictions.
    # --------------------------------------------------------------

    predictions = {

        "quantity_kg": 887.0,

        "price_per_kg": 7591.84,

        "estimated_total_cost":
            5733135.72,

        "transport_cost":
            6438.86,

        "damage_percentage":
            3.5044,

        "delay_hours":
            10.2724,

        "payment_risk":
            "Paid",

        "delivery_risk":
            "Delayed",
    }

    result = engine.analyze(
        predictions
    )

    print("\n")
    print("=" * 70)
    print("WHAT-IF TEST COMPLETED")
    print("=" * 70)

    print(
        "\n✓ Current scenario calculated."
    )

    print(
        "✓ Price scenarios calculated."
    )

    print(
        "✓ Transport scenario calculated."
    )

    print(
        "✓ Damage scenario calculated."
    )

    print(
        "✓ Delay scenario calculated."
    )

    print(
        "✓ Quantity scenarios calculated."
    )

    print(
        "✓ Profit impact calculated."
    )

    print(
        "✓ Risk impact calculated."
    )

    print(
        "✓ No model retraining."
    )

    print(
        "✓ No fake ML predictions."
    )


# ======================================================================
# RUN
# ======================================================================

if __name__ == "__main__":

    main()