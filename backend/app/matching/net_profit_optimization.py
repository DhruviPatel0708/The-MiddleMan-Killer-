"""
======================================================================
NET PROFIT OPTIMIZATION
======================================================================

EXECUTION & MATCHING ARCHITECTURE
----------------------------------------------------------------------
Buyer Matching
      ↓
AI Auction
      ↓
Risk-Aware Bidding
      ↓
NET PROFIT OPTIMIZATION
      ↓
Best Economic Buyer
      ↓
Logistics Optimization

PURPOSE
----------------------------------------------------------------------
Determine the economically best buyer using:

    Revenue
    Transaction Cost
    Net Profit
    Profit Margin
    Risk-Aware Profit

IMPORTANT
----------------------------------------------------------------------
✓ Existing architecture only
✓ Existing buyer dataset
✓ Existing cost dataset
✓ Existing AI Auction
✓ Existing Risk-Aware Bidding
✓ No model retraining
✓ No new ML model
✓ No new dataset
✓ No dataset modification
✓ No fake predictions
✓ No AI Agent
======================================================================
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

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

COST_DATASET = (
    DATA_DIR
    / "cost_features.csv"
)


# ======================================================================
# ENGINE
# ======================================================================

class NetProfitOptimizationEngine:

    def __init__(self):

        print()
        print("=" * 70)
        print("NET PROFIT OPTIMIZATION ENGINE")
        print("=" * 70)

        print()
        print("✓ Existing Risk-Aware Bidding output supported.")
        print("✓ Existing Cost Estimation data supported.")
        print("✓ Transaction-level cost calculation enabled.")
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

        # Exact
        for candidate in candidates:

            if candidate in df.columns:

                return candidate

        # Case-insensitive
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
    # FIND QUANTITY COLUMN
    # ==================================================================

    def find_quantity_column(
        self,
        df: pd.DataFrame,
    ) -> Optional[str]:

        candidates = [

            "quantity_kg",

            "quantity",

            "required_quantity_kg",

            "order_quantity_kg",

            "total_quantity_kg",

            "load_quantity_kg",

            "produce_quantity_kg",

        ]

        column = self.find_column(
            df,
            candidates,
        )

        if column:

            return column

        # Flexible search
        for column in df.columns:

            name = (
                str(column)
                .lower()
                .replace(" ", "_")
            )

            if "quantity" in name:

                return column

        return None

    # ==================================================================
    # LOAD COST DATA
    # ==================================================================

    def load_cost_data(self):

        print()
        print("=" * 70)
        print("LOADING EXISTING COST DATA")
        print("=" * 70)

        if not COST_DATASET.exists():

            raise FileNotFoundError(
                "Existing cost dataset not found:\n"
                f"{COST_DATASET}"
            )

        df = pd.read_csv(
            COST_DATASET
        )

        print(
            f"✓ cost_features.csv loaded"
        )

        print(
            f"  Rows    : {len(df):,}"
        )

        print(
            f"  Columns : {len(df.columns)}"
        )

        return df

    # ==================================================================
    # CALCULATE EXISTING COST PER KG
    # ==================================================================

    def calculate_cost_per_kg(
        self,
        df: pd.DataFrame,
    ) -> float:

        target_column = self.find_column(

            df,

            [
                "estimated_total_cost",
                "total_cost",
                "estimated_cost",
            ],

        )

        if target_column is None:

            raise ValueError(
                "Existing cost target column not found."
            )

        quantity_column = (
            self.find_quantity_column(
                df
            )
        )

        if quantity_column is None:

            raise ValueError(
                "Quantity column not found "
                "in existing cost dataset."
            )

        cost = pd.to_numeric(
            df[target_column],
            errors="coerce",
        )

        quantity = pd.to_numeric(
            df[quantity_column],
            errors="coerce",
        )

        valid = (

            cost.notna()

            & quantity.notna()

            & (cost >= 0)

            & (quantity > 0)

        )

        if valid.sum() == 0:

            raise ValueError(
                "No valid cost/quantity records found."
            )

        cost_per_kg = (
            cost[valid]
            / quantity[valid]
        )

        cost_per_kg = cost_per_kg[
            np.isfinite(
                cost_per_kg
            )
        ]

        cost_per_kg = cost_per_kg[
            cost_per_kg >= 0
        ]

        if len(cost_per_kg) == 0:

            raise ValueError(
                "No valid cost-per-kg values available."
            )

        # Robust existing-data estimate.
        median_cost_per_kg = float(
            cost_per_kg.median()
        )

        print()
        print(
            f"✓ Cost target     : {target_column}"
        )

        print(
            f"✓ Quantity column : {quantity_column}"
        )

        print(
            f"✓ Existing cost/kg: "
            f"₹{median_cost_per_kg:,.2f}"
        )

        return median_cost_per_kg

    # ==================================================================
    # TRANSACTION COST
    # ==================================================================

    def calculate_transaction_cost(
        self,
        quantity_kg: float,
    ) -> float:

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

        df = self.load_cost_data()

        cost_per_kg = (
            self.calculate_cost_per_kg(
                df
            )
        )

        transaction_cost = (
            cost_per_kg
            * quantity_kg
        )

        print()
        print(
            f"✓ Current quantity : "
            f"{quantity_kg:,.2f} kg"
        )

        print(
            f"✓ Transaction cost : "
            f"₹{transaction_cost:,.2f}"
        )

        return transaction_cost

    # ==================================================================
    # BID PRICE
    # ==================================================================

    def get_bid_price(
        self,
        bid: Dict[str, Any],
    ) -> float:

        candidates = [

            "offered_price_per_kg",

            "winning_price_per_kg",

            "bid_price_per_kg",

            "price_per_kg",

            "offered_price",

            "bid_price",

        ]

        for key in candidates:

            if key in bid:

                value = self.number(
                    bid[key],
                    -1.0,
                )

                if value >= 0:

                    return value

        return 0.0

    # ==================================================================
    # CALCULATE FINANCIALS
    # ==================================================================

    def calculate_financials(
        self,
        bid: Dict[str, Any],
        quantity_kg: float,
        transaction_cost: float,
    ) -> Dict[str, float]:

        price = self.get_bid_price(
            bid
        )

        quantity = max(
            0.0,
            self.number(
                quantity_kg
            ),
        )

        cost = max(
            0.0,
            self.number(
                transaction_cost
            ),
        )

        revenue = (
            price
            * quantity
        )

        net_profit = (
            revenue
            - cost
        )

        if revenue > 0:

            margin = (
                net_profit
                / revenue
                * 100.0
            )

        else:

            margin = 0.0

        if net_profit > 0:

            profitability = (
                "PROFITABLE"
            )

        elif net_profit == 0:

            profitability = (
                "BREAK_EVEN"
            )

        else:

            profitability = (
                "NOT_PROFITABLE"
            )

        return {

            "price_per_kg":
                price,

            "quantity_kg":
                quantity,

            "expected_revenue":
                revenue,

            "transaction_cost":
                cost,

            "net_profit":
                net_profit,

            "profit_margin":
                margin,

            "profitability":
                profitability,

        }

    # ==================================================================
    # RISK-ADJUSTED PROFIT
    # ==================================================================

    def calculate_risk_adjusted_profit(
        self,
        net_profit: float,
        risk_score: float,
    ) -> float:

        risk = max(
            0.0,
            min(
                100.0,
                self.number(
                    risk_score,
                    50.0,
                ),
            ),
        )

        safety_factor = (
            1.0
            - risk / 100.0
        )

        # A loss remains a loss.
        # Risk adjustment must never create fake profit.

        if net_profit <= 0:

            return net_profit

        return (
            net_profit
            * safety_factor
        )

    # ==================================================================
    # OPTIMIZE
    # ==================================================================

    def optimize(
        self,
        bids: List[Dict[str, Any]],
        quantity_kg: float,
        transaction_cost: float,
    ) -> Dict[str, Any]:

        print()
        print("=" * 70)
        print("RUNNING NET PROFIT OPTIMIZATION")
        print("=" * 70)

        if not bids:

            return {

                "status":
                    "NO_BIDS",

                "recommended_bid":
                    None,

                "optimized_bids":
                    [],

            }

        candidates = []

        # --------------------------------------------------------------
        # Evaluate every buyer
        # --------------------------------------------------------------

        for bid in bids:

            financials = (
                self.calculate_financials(

                    bid,

                    quantity_kg,

                    transaction_cost,

                )
            )

            risk_score = self.number(

                bid.get(
                    "combined_risk",
                    bid.get(
                        "risk_score",
                        50.0,
                    ),
                ),

                50.0,

            )

            risk_adjusted_profit = (
                self.calculate_risk_adjusted_profit(

                    financials[
                        "net_profit"
                    ],

                    risk_score,

                )
            )

            result = dict(
                bid
            )

            result.update({

                "price_per_kg":
                    round(
                        financials[
                            "price_per_kg"
                        ],
                        2,
                    ),

                "quantity_kg":
                    round(
                        financials[
                            "quantity_kg"
                        ],
                        2,
                    ),

                "expected_revenue":
                    round(
                        financials[
                            "expected_revenue"
                        ],
                        2,
                    ),

                "transaction_cost":
                    round(
                        financials[
                            "transaction_cost"
                        ],
                        2,
                    ),

                "net_profit":
                    round(
                        financials[
                            "net_profit"
                        ],
                        2,
                    ),

                "profit_margin":
                    round(
                        financials[
                            "profit_margin"
                        ],
                        2,
                    ),

                "profitability":
                    financials[
                        "profitability"
                    ],

                "risk_score":
                    round(
                        risk_score,
                        2,
                    ),

                "risk_adjusted_profit":
                    round(
                        risk_adjusted_profit,
                        2,
                    ),

            })

            candidates.append(
                result
            )

        # --------------------------------------------------------------
        # PRIMARY RULE:
        #
        # Actual net profit is the primary economic objective.
        #
        # Secondary:
        # Risk-adjusted profit
        #
        # Tertiary:
        # Lower risk
        #
        # Final:
        # Higher bid
        # --------------------------------------------------------------

        candidates.sort(

            key=lambda item: (

                item[
                    "net_profit"
                ],

                item[
                    "risk_adjusted_profit"
                ],

                -item[
                    "risk_score"
                ],

                item[
                    "price_per_kg"
                ],

            ),

            reverse=True,

        )

        # --------------------------------------------------------------
        # Profit rank
        # --------------------------------------------------------------

        for rank, item in enumerate(

            candidates,

            start=1,

        ):

            item[
                "profit_rank"
            ] = rank

        # --------------------------------------------------------------
        # Determine whether ANY buyer is profitable
        # --------------------------------------------------------------

        profitable = [

            item

            for item in candidates

            if item[
                "net_profit"
            ] > 0

        ]

        break_even = [

            item

            for item in candidates

            if item[
                "net_profit"
            ] == 0

        ]

        if profitable:

            optimization_status = (
                "PROFITABLE_OPPORTUNITY"
            )

            recommended = profitable[0]

        elif break_even:

            optimization_status = (
                "BREAK_EVEN_OPPORTUNITY"
            )

            recommended = break_even[0]

        else:

            optimization_status = (
                "NO_PROFITABLE_BUYER"
            )

            # Best available buyer means:
            # highest actual net profit / least loss.
            recommended = candidates[0]

        # --------------------------------------------------------------
        # Display
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("NET PROFIT OPTIMIZATION RANKING")
        print("=" * 70)

        for item in candidates:

            print()
            print(
                f"#{item['profit_rank']} "
                f"{item.get('buyer_name', 'Unknown')}"
            )

            print(
                f"  Bid Price          : "
                f"₹{item['price_per_kg']:,.2f}/kg"
            )

            print(
                f"  Revenue            : "
                f"₹{item['expected_revenue']:,.2f}"
            )

            print(
                f"  Transaction Cost   : "
                f"₹{item['transaction_cost']:,.2f}"
            )

            print(
                f"  Net Profit         : "
                f"₹{item['net_profit']:,.2f}"
            )

            print(
                f"  Profit Margin      : "
                f"{item['profit_margin']:.2f}%"
            )

            print(
                f"  Profitability      : "
                f"{item['profitability']}"
            )

            print(
                f"  Risk               : "
                f"{item['risk_score']:.2f}/100"
            )

            print(
                f"  Risk-Adjusted      : "
                f"₹{item['risk_adjusted_profit']:,.2f}"
            )

        # --------------------------------------------------------------
        # Recommendation
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("NET PROFIT RECOMMENDATION")
        print("=" * 70)

        print(
            f"✓ Best Buyer         : "
            f"{recommended.get('buyer_name', 'Unknown')}"
        )

        print(
            f"✓ Buyer ID           : "
            f"{recommended.get('buyer_id', 'Unknown')}"
        )

        print(
            f"✓ Bid Price          : "
            f"₹{recommended['price_per_kg']:,.2f}/kg"
        )

        print(
            f"✓ Expected Revenue   : "
            f"₹{recommended['expected_revenue']:,.2f}"
        )

        print(
            f"✓ Transaction Cost   : "
            f"₹{recommended['transaction_cost']:,.2f}"
        )

        print(
            f"✓ Net Profit         : "
            f"₹{recommended['net_profit']:,.2f}"
        )

        print(
            f"✓ Profit Margin      : "
            f"{recommended['profit_margin']:.2f}%"
        )

        print(
            f"✓ Profitability      : "
            f"{recommended['profitability']}"
        )

        print(
            f"✓ Risk               : "
            f"{recommended['risk_score']:.2f}/100"
        )

        print(
            f"✓ Risk-Adjusted      : "
            f"₹{recommended['risk_adjusted_profit']:,.2f}"
        )

        print()
        print(
            f"FINAL STATUS: "
            f"{optimization_status}"
        )

        return {

            "status":
                "COMPLETED",

            "optimization_status":
                optimization_status,

            "profitable_buyer_exists":
                len(profitable) > 0,

            "recommended_bid":
                recommended,

            "recommended_buyer":
                recommended,

            "expected_revenue":
                recommended[
                    "expected_revenue"
                ],

            "transaction_cost":
                recommended[
                    "transaction_cost"
                ],

            "net_profit":
                recommended[
                    "net_profit"
                ],

            "profit_margin":
                recommended[
                    "profit_margin"
                ],

            "profitability":
                recommended[
                    "profitability"
                ],

            "risk_score":
                recommended[
                    "risk_score"
                ],

            "risk_adjusted_profit":
                recommended[
                    "risk_adjusted_profit"
                ],

            "optimized_bids":
                candidates,

            "candidate_count":
                len(candidates),

            "profitable_candidate_count":
                len(profitable),

        }


# ======================================================================
# TEST
# ======================================================================

def main():

    print()
    print("=" * 70)
    print("NET PROFIT OPTIMIZATION TEST")
    print("=" * 70)

    try:

        # ==============================================================
        # BUYER MATCHING
        # ==============================================================

        from buyer_matching import (
            BuyerMatchingEngine
        )

        matching_engine = (
            BuyerMatchingEngine()
        )

        matching_result = (
            matching_engine.find_best_buyer(

                crop="Bajra",

                quantity_kg=887.0,

                quality_grade="C",

                district="Kheda",

                market="Kheda APMC",

                expected_price=7591.84,

            )
        )

        if (
            matching_result.get(
                "status"
            )
            != "MATCHED"
        ):

            raise RuntimeError(
                "Buyer Matching failed."
            )

        # ==============================================================
        # AI AUCTION
        # ==============================================================

        from ai_auction import (
            AIAuctionEngine
        )

        auction_engine = (
            AIAuctionEngine()
        )

        auction_result = (
            auction_engine.run_auction(

                matched_buyers=
                matching_result[
                    "matched_buyers"
                ],

            )
        )

        if (
            auction_result.get(
                "status"
            )
            != "COMPLETED"
        ):

            raise RuntimeError(
                "AI Auction failed."
            )

        # ==============================================================
        # RISK-AWARE BIDDING
        # ==============================================================

        from risk_aware_bidding import (
            RiskAwareBiddingEngine
        )

        risk_engine = (
            RiskAwareBiddingEngine()
        )

        risk_result = (
            risk_engine.evaluate_bids(

                ranked_bids=
                auction_result[
                    "ranked_bids"
                ],

            )
        )

        if (
            risk_result.get(
                "status"
            )
            != "COMPLETED"
        ):

            raise RuntimeError(
                "Risk-Aware Bidding failed."
            )

        # ==============================================================
        # QUANTITY
        # ==============================================================

        quantity_kg = 887.0

        # ==============================================================
        # NET PROFIT ENGINE
        # ==============================================================

        engine = (
            NetProfitOptimizationEngine()
        )

        transaction_cost = (
            engine.calculate_transaction_cost(

                quantity_kg

            )
        )

        # ==============================================================
        # OPTIMIZATION
        # ==============================================================

        result = (
            engine.optimize(

                bids=
                risk_result[
                    "evaluated_bids"
                ],

                quantity_kg=
                quantity_kg,

                transaction_cost=
                transaction_cost,

            )
        )

        # ==============================================================
        # FINAL STATUS
        # ==============================================================

        print()
        print("=" * 70)
        print("NET PROFIT OPTIMIZATION FINAL STATUS")
        print("=" * 70)

        winner = (
            result[
                "recommended_bid"
            ]
        )

        print(
            "✓ NET PROFIT OPTIMIZATION COMPLETED"
        )

        print(
            f"✓ Best Buyer        : "
            f"{winner.get('buyer_name', 'Unknown')}"
        )

        print(
            f"✓ Bid Price         : "
            f"₹{winner['price_per_kg']:,.2f}/kg"
        )

        print(
            f"✓ Revenue           : "
            f"₹{winner['expected_revenue']:,.2f}"
        )

        print(
            f"✓ Transaction Cost  : "
            f"₹{winner['transaction_cost']:,.2f}"
        )

        print(
            f"✓ Net Profit        : "
            f"₹{winner['net_profit']:,.2f}"
        )

        print(
            f"✓ Profit Margin     : "
            f"{winner['profit_margin']:.2f}%"
        )

        print(
            f"✓ Profitability     : "
            f"{winner['profitability']}"
        )

        print(
            f"✓ Risk              : "
            f"{winner['risk_score']:.2f}/100"
        )

        print(
            f"✓ Risk-Adjusted     : "
            f"₹{winner['risk_adjusted_profit']:,.2f}"
        )

        print()
        print(
            f"✓ Optimization Status: "
            f"{result['optimization_status']}"
        )

        if result[
            "profitable_buyer_exists"
        ]:

            print(
                "✓ At least one profitable buyer exists."
            )

        else:

            print(
                "⚠ No profitable buyer at current bids."
            )

            print(
                "⚠ Best available buyer selected "
                "by highest actual net profit."
            )

        print()
        print(
            "✓ Existing Cost Estimation data used"
        )

        print(
            "✓ Existing Risk-Aware Bidding used"
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
        print("✗ NET PROFIT OPTIMIZATION TEST FAILED")
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