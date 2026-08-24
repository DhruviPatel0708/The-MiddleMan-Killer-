"""
======================================================================
AI AUCTION
======================================================================

Architecture:
    EXECUTION & MATCHING
        └── AI AUCTION

Purpose:
    Rank matched buyers and select the best auction bid.

Uses:
    - Existing Buyer Matching output
    - Existing buyer reliability
    - Existing offered prices

Does NOT:
    - Train a new ML model
    - Create a new dataset
    - Modify existing datasets
    - Add an AI Agent
    - Add unrelated architecture components
======================================================================
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


# ======================================================================
# AI AUCTION ENGINE
# ======================================================================

class AIAuctionEngine:

    def __init__(self) -> None:

        print()
        print("=" * 70)
        print("AI AUCTION ENGINE")
        print("=" * 70)

        print()
        print("✓ AI Auction Engine initialized.")
        print("✓ Existing Buyer Matching output will be used.")
        print("✓ No new ML model.")
        print("✓ No new dataset.")
        print("✓ No AI Agent.")

    # ==================================================================
    # SAFE NUMBER
    # ==================================================================

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            result = float(value)

            if not np.isfinite(result):

                return default

            return result

        except (
            TypeError,
            ValueError,
        ):

            return default

    # ==================================================================
    # NORMALIZE RELIABILITY
    # ==================================================================

    def _reliability_score(
        self,
        buyer: Dict[str, Any],
    ) -> float:

        score = self._number(
            buyer.get(
                "reliability_score",
                0.0,
            )
        )

        label = str(
            buyer.get(
                "buyer_reliability_label",
                "",
            )
        ).strip().upper()

        # Existing verified Buyer Reliability output
        # remains the primary signal.

        if score > 0:

            return max(
                0.0,
                min(
                    100.0,
                    score,
                ),
            )

        if label == "RELIABLE":

            return 100.0

        if label == "MODERATE":

            return 70.0

        if label == "UNRELIABLE":

            return 30.0

        return 50.0

    # ==================================================================
    # MATCH SCORE
    # ==================================================================

    def _match_score(
        self,
        buyer: Dict[str, Any],
    ) -> float:

        return max(
            0.0,
            min(
                100.0,
                self._number(
                    buyer.get(
                        "match_score",
                        0.0,
                    )
                ),
            ),
        )

    # ==================================================================
    # PRICE SCORE
    # ==================================================================

    @staticmethod
    def _price_score(
        offered_price: float,
        maximum_bid: Optional[float],
    ) -> float:

        if offered_price <= 0:

            return 0.0

        if (
            maximum_bid is None
            or maximum_bid <= 0
        ):

            return 100.0

        ratio = (
            offered_price
            / maximum_bid
        )

        return max(
            0.0,
            min(
                100.0,
                ratio * 100.0,
            ),
        )

    # ==================================================================
    # AUCTION SCORE
    # ==================================================================

    def _auction_score(
        self,
        buyer: Dict[str, Any],
        maximum_bid: Optional[float],
    ) -> float:

        offered_price = self._number(
            buyer.get(
                "offered_price_per_kg",
                0.0,
            )
        )

        reliability = (
            self._reliability_score(
                buyer
            )
        )

        match = (
            self._match_score(
                buyer
            )
        )

        price_score = self._price_score(
            offered_price,
            maximum_bid,
        )

        # --------------------------------------------------------------
        # AI Auction score
        #
        # Price is important, but a higher bid from an unreliable
        # buyer should not automatically win.
        #
        # Existing architecture signals:
        #   50% bid value
        #   30% buyer reliability
        #   20% buyer matching
        # --------------------------------------------------------------

        score = (

            price_score * 0.50

            + reliability * 0.30

            + match * 0.20
        )

        return max(
            0.0,
            min(
                100.0,
                score,
            ),
        )

    # ==================================================================
    # AUCTION
    # ==================================================================

    def run_auction(
        self,
        matched_buyers: List[Dict[str, Any]],
        maximum_bid: Optional[float] = None,
    ) -> Dict[str, Any]:

        print()
        print("=" * 70)
        print("RUNNING AI AUCTION")
        print("=" * 70)

        if not matched_buyers:

            print()
            print(
                "⚠ No matched buyers available."
            )

            return {
                "status": "NO_BIDS",
                "winning_bid": None,
                "winning_buyer": None,
                "ranked_bids": [],
            }

        # --------------------------------------------------------------
        # Calculate auction scores
        # --------------------------------------------------------------

        ranked_bids = []

        for buyer in matched_buyers:

            offered_price = self._number(
                buyer.get(
                    "offered_price_per_kg",
                    0.0,
                )
            )

            reliability = (
                self._reliability_score(
                    buyer
                )
            )

            match_score = (
                self._match_score(
                    buyer
                )
            )

            price_score = (
                self._price_score(
                    offered_price,
                    maximum_bid,
                )
            )

            auction_score = (
                self._auction_score(
                    buyer,
                    maximum_bid,
                )
            )

            ranked_bids.append({

                "buyer_id":
                    buyer.get(
                        "buyer_id"
                    ),

                "buyer_name":
                    buyer.get(
                        "buyer_name"
                    ),

                "buyer_type":
                    buyer.get(
                        "buyer_type"
                    ),

                "district":
                    buyer.get(
                        "district"
                    ),

                "market":
                    buyer.get(
                        "market"
                    ),

                "offered_price_per_kg":
                    round(
                        offered_price,
                        2,
                    ),

                "buyer_reliability_label":
                    buyer.get(
                        "buyer_reliability_label"
                    ),

                "reliability_score":
                    round(
                        reliability,
                        2,
                    ),

                "match_score":
                    round(
                        match_score,
                        2,
                    ),

                "price_score":
                    round(
                        price_score,
                        2,
                    ),

                "auction_score":
                    round(
                        auction_score,
                        2,
                    ),

                "match_reliability":
                    buyer.get(
                        "match_reliability"
                    ),
            })

        # --------------------------------------------------------------
        # Rank auction bids
        # --------------------------------------------------------------

        ranked_bids.sort(
            key=lambda item: (
                item["auction_score"],
                item["offered_price_per_kg"],
                item["reliability_score"],
            ),
            reverse=True,
        )

        # --------------------------------------------------------------
        # Assign auction rank
        # --------------------------------------------------------------

        for index, bid in enumerate(
            ranked_bids,
            start=1,
        ):

            bid["auction_rank"] = index

        winning_bid = ranked_bids[0]

        # --------------------------------------------------------------
        # Display ranking
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("AI AUCTION BID RANKING")
        print("=" * 70)

        for bid in ranked_bids:

            print()
            print(
                f"#{bid['auction_rank']} "
                f"{bid['buyer_name']}"
            )

            print(
                f"  Bid Price       : "
                f"₹{bid['offered_price_per_kg']:,.2f}/kg"
            )

            print(
                f"  Price Score     : "
                f"{bid['price_score']:.2f}/100"
            )

            print(
                f"  Reliability     : "
                f"{bid['reliability_score']:.2f}/100"
            )

            print(
                f"  Match Score     : "
                f"{bid['match_score']:.2f}/100"
            )

            print(
                f"  Auction Score   : "
                f"{bid['auction_score']:.2f}/100"
            )

        # --------------------------------------------------------------
        # Winner
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("AI AUCTION WINNER")
        print("=" * 70)

        print(
            f"✓ Buyer          : "
            f"{winning_bid['buyer_name']}"
        )

        print(
            f"✓ Buyer ID       : "
            f"{winning_bid['buyer_id']}"
        )

        print(
            f"✓ Winning Bid    : "
            f"₹{winning_bid['offered_price_per_kg']:,.2f}/kg"
        )

        print(
            f"✓ Auction Score  : "
            f"{winning_bid['auction_score']:.2f}/100"
        )

        print(
            f"✓ Reliability    : "
            f"{winning_bid['reliability_score']:.2f}/100"
        )

        print(
            f"✓ Match Score    : "
            f"{winning_bid['match_score']:.2f}/100"
        )

        return {

            "status": "COMPLETED",

            "winning_buyer":
                winning_bid,

            "winning_bid":
                winning_bid,

            "winning_price_per_kg":
                winning_bid[
                    "offered_price_per_kg"
                ],

            "auction_score":
                winning_bid[
                    "auction_score"
                ],

            "ranked_bids":
                ranked_bids,

            "bid_count":
                len(ranked_bids),
        }

    # ==================================================================
    # DIRECT API
    # ==================================================================

    def auction(
        self,
        matched_buyers: List[Dict[str, Any]],
        maximum_bid: Optional[float] = None,
    ) -> Dict[str, Any]:

        return self.run_auction(
            matched_buyers=matched_buyers,
            maximum_bid=maximum_bid,
        )


# ======================================================================
# TEST
# ======================================================================

def main() -> None:

    print()
    print("=" * 70)
    print("AI AUCTION TEST")
    print("=" * 70)

    try:

        # --------------------------------------------------------------
        # Import the existing Buyer Matching engine.
        # --------------------------------------------------------------

        from buyer_matching import (
            BuyerMatchingEngine
        )

        # --------------------------------------------------------------
        # Existing Buyer Matching
        # --------------------------------------------------------------

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
            matching_result["status"]
            != "MATCHED"
        ):

            print()
            print(
                "⚠ AI Auction cannot run."
            )

            print(
                "No matched buyers were returned."
            )

            return

        # --------------------------------------------------------------
        # Existing matched buyers are passed directly into auction.
        # --------------------------------------------------------------

        matched_buyers = (
            matching_result[
                "matched_buyers"
            ]
        )

        # --------------------------------------------------------------
        # AI Auction
        # --------------------------------------------------------------

        auction_engine = (
            AIAuctionEngine()
        )

        auction_result = (
            auction_engine.run_auction(
                matched_buyers=matched_buyers,
            )
        )

        # --------------------------------------------------------------
        # Final status
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("AI AUCTION FINAL STATUS")
        print("=" * 70)

        if (
            auction_result["status"]
            == "COMPLETED"
        ):

            winner = (
                auction_result[
                    "winning_buyer"
                ]
            )

            print(
                "✓ AI AUCTION COMPLETED"
            )

            print(
                f"✓ Winning Buyer : "
                f"{winner['buyer_name']}"
            )

            print(
                f"✓ Winning Bid   : "
                f"₹{winner['offered_price_per_kg']:,.2f}/kg"
            )

            print(
                f"✓ Auction Score : "
                f"{winner['auction_score']:.2f}/100"
            )

            print(
                f"✓ Reliability   : "
                f"{winner['reliability_score']:.2f}/100"
            )

            print(
                f"✓ Bids Ranked   : "
                f"{auction_result['bid_count']}"
            )

            print()
            print(
                "✓ Existing Buyer Matching output used"
            )

            print(
                "✓ No new ML model"
            )

            print(
                "✓ No new dataset"
            )

            print(
                "✓ No AI Agent"
            )

        else:

            print(
                "⚠ AI AUCTION NOT COMPLETED"
            )

    except Exception as exc:

        print()
        print("=" * 70)
        print("✗ AI AUCTION TEST FAILED")
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