"""
======================================================================
BUYER MATCHING
======================================================================

Architecture:
    EXECUTION & MATCHING
        └── BUYER MATCHING
              ├── Best Buyer
              └── Match Reliability

Rules:
    - Existing architecture only
    - Existing buyers.csv only
    - No model retraining
    - No new ML model
    - No new dataset
    - No AI Agent
    - No modification of existing data
======================================================================
"""

from pathlib import Path
from typing import Optional, Dict, Any, List

import numpy as np
import pandas as pd


# ======================================================================
# PATH CONFIGURATION
# ======================================================================

CURRENT_FILE = Path(__file__).resolve()

# backend/app/matching/buyer_matching.py
# parents[0] = matching
# parents[1] = app
# parents[2] = backend
# parents[3] = PythonProject3

PROJECT_ROOT = CURRENT_FILE.parents[3]

DATA_DIR = PROJECT_ROOT / "data" / "processed"

BUYER_DATASET = DATA_DIR / "buyers.csv"

BUYER_FEATURE_DATASET = DATA_DIR / "buyer_features.csv"


# ======================================================================
# REQUIRED BUYER COLUMNS
# ======================================================================

REQUIRED_COLUMNS = [
    "buyer_id",
    "buyer_name",
    "buyer_type",
    "district",
    "market",
    "preferred_crop",
    "required_quantity_kg",
    "minimum_quantity_kg",
    "maximum_quantity_kg",
    "offered_price_per_kg",
    "minimum_quality_grade",
    "storage_available",
    "buyer_rating",
    "reliability_score",
    "buyer_reliability_label",
]


# ======================================================================
# QUALITY ORDER
# ======================================================================

QUALITY_RANK = {
    "A": 4,
    "B": 3,
    "C": 2,
    "D": 1,
}


# ======================================================================
# BUYER MATCHING ENGINE
# ======================================================================

class BuyerMatchingEngine:
    """
    Existing-data buyer matching engine.

    It ranks buyers using:
        - Crop compatibility
        - Quantity compatibility
        - Quality compatibility
        - Location compatibility
        - Offered price
        - Existing buyer reliability
        - Storage availability

    Final architecture outputs:
        - Best Buyer
        - Match Reliability
    """

    def __init__(
        self,
        dataset_path: Optional[str] = None,
    ) -> None:

        print()
        print("=" * 70)
        print("BUYER MATCHING ENGINE")
        print("=" * 70)

        self.dataset_path = self._resolve_dataset(
            dataset_path
        )

        print()
        print("Loading existing buyer dataset...")
        print("-" * 70)
        print(self.dataset_path)

        self.buyers = pd.read_csv(
            self.dataset_path
        )

        print()
        print("✓ Buyer dataset loaded")
        print(
            f"  Rows    : {len(self.buyers):,}"
        )
        print(
            f"  Columns : {len(self.buyers.columns)}"
        )

        self._validate_dataset()

        print()
        print("✓ Buyer Matching Engine initialized.")

    # ==================================================================
    # DATASET RESOLUTION
    # ==================================================================

    @staticmethod
    def _resolve_dataset(
        dataset_path: Optional[str]
    ) -> Path:

        if dataset_path:

            path = Path(dataset_path)

            if path.exists():

                return path

            raise FileNotFoundError(
                f"Specified buyer dataset not found:\n{path}"
            )

        if BUYER_DATASET.exists():

            return BUYER_DATASET

        if BUYER_FEATURE_DATASET.exists():

            return BUYER_FEATURE_DATASET

        raise FileNotFoundError(
            "No existing buyer dataset found.\n\n"
            f"Checked:\n"
            f"  {BUYER_DATASET}\n"
            f"  {BUYER_FEATURE_DATASET}"
        )

    # ==================================================================
    # DATASET VALIDATION
    # ==================================================================

    def _validate_dataset(self) -> None:

        missing = [
            column
            for column in REQUIRED_COLUMNS
            if column not in self.buyers.columns
        ]

        if missing:

            raise ValueError(
                "Buyer dataset is missing required "
                f"columns:\n{missing}"
            )

        print()
        print(
            "✓ Required Buyer Matching columns verified"
        )

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
    # NORMALIZE TEXT
    # ==================================================================

    @staticmethod
    def _text(
        value: Any,
    ) -> str:

        if pd.isna(value):

            return ""

        return str(value).strip()

    # ==================================================================
    # QUALITY RANK
    # ==================================================================

    @staticmethod
    def _quality_rank(
        grade: Any,
    ) -> int:

        return QUALITY_RANK.get(
            str(grade).strip().upper(),
            0,
        )

    # ==================================================================
    # CROP MATCH
    # ==================================================================

    def _crop_score(
        self,
        buyer: pd.Series,
        crop: str,
    ) -> float:

        buyer_crop = self._text(
            buyer["preferred_crop"]
        ).lower()

        requested_crop = self._text(
            crop
        ).lower()

        if (
            buyer_crop
            and requested_crop
            and buyer_crop == requested_crop
        ):

            return 100.0

        return 0.0

    # ==================================================================
    # QUANTITY MATCH
    # ==================================================================

    def _quantity_score(
        self,
        buyer: pd.Series,
        quantity_kg: float,
    ) -> float:

        quantity = max(
            0.0,
            self._number(quantity_kg),
        )

        minimum = max(
            0.0,
            self._number(
                buyer["minimum_quantity_kg"]
            ),
        )

        maximum = max(
            minimum,
            self._number(
                buyer["maximum_quantity_kg"]
            ),
        )

        if quantity <= 0:

            return 0.0

        # Perfect quantity compatibility.
        if minimum <= quantity <= maximum:

            return 100.0

        # Outside accepted range.
        if quantity < minimum:

            difference = minimum - quantity

        else:

            difference = quantity - maximum

        penalty = (
            difference
            / max(quantity, 1.0)
            * 100.0
        )

        return float(
            max(
                0.0,
                min(
                    100.0,
                    100.0 - penalty,
                ),
            )
        )

    # ==================================================================
    # QUALITY MATCH
    # ==================================================================

    def _quality_score(
        self,
        buyer: pd.Series,
        quality_grade: Optional[str],
    ) -> float:

        if not quality_grade:

            # No supplied quality information.
            return 50.0

        farmer_rank = self._quality_rank(
            quality_grade
        )

        required_rank = self._quality_rank(
            buyer["minimum_quality_grade"]
        )

        if farmer_rank <= 0:

            return 50.0

        if required_rank <= 0:

            return 50.0

        if farmer_rank >= required_rank:

            return 100.0

        difference = (
            required_rank - farmer_rank
        )

        return max(
            0.0,
            100.0 - (
                difference * 50.0
            ),
        )

    # ==================================================================
    # LOCATION MATCH
    # ==================================================================

    def _location_score(
        self,
        buyer: pd.Series,
        district: Optional[str],
        market: Optional[str],
    ) -> float:

        buyer_district = self._text(
            buyer.get("district", "")
        ).lower()

        buyer_market = self._text(
            buyer.get("market", "")
        ).lower()

        requested_district = self._text(
            district
        ).lower()

        requested_market = self._text(
            market
        ).lower()

        if (
            requested_market
            and buyer_market == requested_market
        ):

            return 100.0

        if (
            requested_district
            and buyer_district == requested_district
        ):

            return 85.0

        # Location is unknown rather than incompatible.
        if (
            not requested_market
            and not requested_district
        ):

            return 50.0

        return 50.0

    # ==================================================================
    # PRICE SCORE
    # ==================================================================

    def _price_score(
        self,
        buyer: pd.Series,
        expected_price: Optional[float],
    ) -> float:

        offered_price = self._number(
            buyer["offered_price_per_kg"]
        )

        if offered_price <= 0:

            return 0.0

        if expected_price is None:

            # Existing offered price is usable,
            # but there is no comparison price.
            return 70.0

        expected = self._number(
            expected_price
        )

        if expected <= 0:

            return 70.0

        ratio = (
            offered_price
            / expected
        )

        if ratio >= 1.10:

            return 100.0

        if ratio >= 1.05:

            return 95.0

        if ratio >= 1.00:

            return 90.0

        if ratio >= 0.95:

            return 75.0

        if ratio >= 0.90:

            return 55.0

        return 30.0

    # ==================================================================
    # RELIABILITY SCORE
    # ==================================================================

    def _reliability_score(
        self,
        buyer: pd.Series,
    ) -> float:

        score = self._number(
            buyer["reliability_score"]
        )

        return float(
            max(
                0.0,
                min(
                    100.0,
                    score,
                ),
            )
        )

    # ==================================================================
    # STORAGE SCORE
    # ==================================================================

    def _storage_score(
        self,
        buyer: pd.Series,
    ) -> float:

        value = self._text(
            buyer["storage_available"]
        ).lower()

        if value in {
            "yes",
            "true",
            "1",
        }:

            return 100.0

        return 50.0

    # ==================================================================
    # MATCH RELIABILITY
    # ==================================================================

    @staticmethod
    def _match_reliability(
        match_score: float,
    ) -> str:

        if match_score >= 85.0:

            return "HIGH"

        if match_score >= 65.0:

            return "MEDIUM"

        return "LOW"

    # ==================================================================
    # MATCH SCORE
    # ==================================================================

    def _calculate_match(
        self,
        buyer: pd.Series,
        crop: str,
        quantity_kg: float,
        quality_grade: Optional[str],
        district: Optional[str],
        market: Optional[str],
        expected_price: Optional[float],
    ) -> Dict[str, Any]:

        crop_score = self._crop_score(
            buyer,
            crop,
        )

        quantity_score = self._quantity_score(
            buyer,
            quantity_kg,
        )

        quality_score = self._quality_score(
            buyer,
            quality_grade,
        )

        location_score = self._location_score(
            buyer,
            district,
            market,
        )

        price_score = self._price_score(
            buyer,
            expected_price,
        )

        reliability_score = (
            self._reliability_score(
                buyer
            )
        )

        storage_score = (
            self._storage_score(
                buyer
            )
        )

        # --------------------------------------------------------------
        # Buyer Matching score
        #
        # Crop is the strongest compatibility signal.
        # Reliability is the strongest trust signal.
        # --------------------------------------------------------------

        match_score = (

            crop_score * 0.25

            + quantity_score * 0.15

            + quality_score * 0.10

            + location_score * 0.10

            + price_score * 0.15

            + reliability_score * 0.20

            + storage_score * 0.05
        )

        match_score = float(
            max(
                0.0,
                min(
                    100.0,
                    match_score,
                ),
            )
        )

        return {

            "buyer_id":
                self._text(
                    buyer["buyer_id"]
                ),

            "buyer_name":
                self._text(
                    buyer["buyer_name"]
                ),

            "buyer_type":
                self._text(
                    buyer["buyer_type"]
                ),

            "district":
                self._text(
                    buyer["district"]
                ),

            "market":
                self._text(
                    buyer["market"]
                ),

            "preferred_crop":
                self._text(
                    buyer["preferred_crop"]
                ),

            "offered_price_per_kg":
                round(
                    self._number(
                        buyer[
                            "offered_price_per_kg"
                        ]
                    ),
                    2,
                ),

            "minimum_quantity_kg":
                round(
                    self._number(
                        buyer[
                            "minimum_quantity_kg"
                        ]
                    ),
                    2,
                ),

            "maximum_quantity_kg":
                round(
                    self._number(
                        buyer[
                            "maximum_quantity_kg"
                        ]
                    ),
                    2,
                ),

            "minimum_quality_grade":
                self._text(
                    buyer[
                        "minimum_quality_grade"
                    ]
                ),

            "storage_available":
                self._text(
                    buyer[
                        "storage_available"
                    ]
                ),

            "buyer_rating":
                round(
                    self._number(
                        buyer["buyer_rating"]
                    ),
                    2,
                ),

            "reliability_score":
                round(
                    reliability_score,
                    2,
                ),

            "buyer_reliability_label":
                self._text(
                    buyer[
                        "buyer_reliability_label"
                    ]
                ),

            "crop_match_score":
                round(
                    crop_score,
                    2,
                ),

            "quantity_match_score":
                round(
                    quantity_score,
                    2,
                ),

            "quality_match_score":
                round(
                    quality_score,
                    2,
                ),

            "location_match_score":
                round(
                    location_score,
                    2,
                ),

            "price_match_score":
                round(
                    price_score,
                    2,
                ),

            "storage_match_score":
                round(
                    storage_score,
                    2,
                ),

            "match_score":
                round(
                    match_score,
                    2,
                ),

            "match_reliability":
                self._match_reliability(
                    match_score
                ),
        }

    # ==================================================================
    # FIND BUYERS
    # ==================================================================

    def match_buyers(
        self,
        crop: str,
        quantity_kg: float,
        quality_grade: Optional[str] = None,
        district: Optional[str] = None,
        market: Optional[str] = None,
        expected_price: Optional[float] = None,
        top_n: int = 5,
    ) -> Dict[str, Any]:

        print()
        print("=" * 70)
        print("BUYER MATCHING")
        print("=" * 70)

        print(
            f"Crop          : {crop}"
        )

        print(
            f"Quantity      : "
            f"{self._number(quantity_kg):,.2f} kg"
        )

        print(
            f"Quality       : "
            f"{quality_grade or 'Not specified'}"
        )

        print(
            f"District      : "
            f"{district or 'Not specified'}"
        )

        print(
            f"Market        : "
            f"{market or 'Not specified'}"
        )

        # --------------------------------------------------------------
        # Exact crop matching.
        # --------------------------------------------------------------

        requested_crop = self._text(
            crop
        ).lower()

        candidates = self.buyers[
            self.buyers[
                "preferred_crop"
            ]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq(requested_crop)
        ].copy()

        print()
        print(
            f"✓ Crop-compatible buyers: "
            f"{len(candidates):,}"
        )

        if candidates.empty:

            return {
                "status": "NO_MATCH",
                "best_buyer": None,
                "match_reliability": None,
                "matched_buyers": [],
                "candidate_count": 0,
            }

        # --------------------------------------------------------------
        # Calculate match results.
        # --------------------------------------------------------------

        matches: List[Dict[str, Any]] = []

        for _, buyer in candidates.iterrows():

            result = self._calculate_match(
                buyer=buyer,
                crop=crop,
                quantity_kg=quantity_kg,
                quality_grade=quality_grade,
                district=district,
                market=market,
                expected_price=expected_price,
            )

            matches.append(result)

        # --------------------------------------------------------------
        # Highest match first.
        # Reliability and offered price are
        # secondary tie-breakers.
        # --------------------------------------------------------------

        matches.sort(
            key=lambda item: (
                item["match_score"],
                item["reliability_score"],
                item["offered_price_per_kg"],
            ),
            reverse=True,
        )

        try:

            limit = max(
                1,
                int(top_n),
            )

        except (
            TypeError,
            ValueError,
        ):

            limit = 5

        matches = matches[
            :limit
        ]

        best = matches[0]

        # --------------------------------------------------------------
        # Output
        # --------------------------------------------------------------

        print()
        print("=" * 70)
        print("BEST BUYER")
        print("=" * 70)

        print(
            f"✓ Buyer              : "
            f"{best['buyer_name']}"
        )

        print(
            f"✓ Buyer ID           : "
            f"{best['buyer_id']}"
        )

        print(
            f"✓ Market             : "
            f"{best['market']}"
        )

        print(
            f"✓ Offered Price      : "
            f"₹{best['offered_price_per_kg']:,.2f}/kg"
        )

        print(
            f"✓ Buyer Reliability  : "
            f"{best['buyer_reliability_label']}"
        )

        print(
            f"✓ Reliability Score  : "
            f"{best['reliability_score']:.2f}/100"
        )

        print(
            f"✓ Match Score        : "
            f"{best['match_score']:.2f}/100"
        )

        print(
            f"✓ Match Reliability  : "
            f"{best['match_reliability']}"
        )

        print()
        print("=" * 70)
        print("TOP BUYER MATCHES")
        print("=" * 70)

        for index, buyer in enumerate(
            matches,
            start=1,
        ):

            print()
            print(
                f"#{index} "
                f"{buyer['buyer_name']}"
            )

            print(
                f"  Match Score       : "
                f"{buyer['match_score']:.2f}/100"
            )

            print(
                f"  Match Reliability : "
                f"{buyer['match_reliability']}"
            )

            print(
                f"  Buyer Reliability : "
                f"{buyer['buyer_reliability_label']}"
            )

            print(
                f"  Offered Price     : "
                f"₹{buyer['offered_price_per_kg']:,.2f}/kg"
            )

        return {

            "status": "MATCHED",

            "best_buyer": best,

            "match_reliability":
                best[
                    "match_reliability"
                ],

            "matched_buyers": matches,

            "candidate_count":
                len(candidates),
        }

    # ==================================================================
    # ARCHITECTURE-FRIENDLY METHOD
    # ==================================================================

    def find_best_buyer(
        self,
        crop: str,
        quantity_kg: float,
        quality_grade: Optional[str] = None,
        district: Optional[str] = None,
        market: Optional[str] = None,
        expected_price: Optional[float] = None,
    ) -> Dict[str, Any]:

        return self.match_buyers(
            crop=crop,
            quantity_kg=quantity_kg,
            quality_grade=quality_grade,
            district=district,
            market=market,
            expected_price=expected_price,
            top_n=5,
        )


# ======================================================================
# TEST
# ======================================================================

def main() -> None:

    print()
    print("=" * 70)
    print("BUYER MATCHING TEST")
    print("=" * 70)

    try:

        engine = BuyerMatchingEngine()

        # Test input from the existing Decision Intelligence
        # execution flow.
        result = engine.find_best_buyer(

            crop="Bajra",

            quantity_kg=887.0,

            quality_grade="C",

            district="Kheda",

            market="Kheda APMC",

            expected_price=7591.84,
        )

        print()
        print("=" * 70)
        print("BUYER MATCHING FINAL STATUS")
        print("=" * 70)

        if result["status"] == "MATCHED":

            best = result["best_buyer"]

            print(
                "✓ BUYER MATCHING COMPLETED"
            )

            print(
                f"✓ Best Buyer          : "
                f"{best['buyer_name']}"
            )

            print(
                f"✓ Match Score         : "
                f"{best['match_score']:.2f}/100"
            )

            print(
                f"✓ Match Reliability   : "
                f"{best['match_reliability']}"
            )

            print(
                f"✓ Buyer Reliability   : "
                f"{best['buyer_reliability_label']}"
            )

            print(
                f"✓ Candidates evaluated: "
                f"{result['candidate_count']}"
            )

            print()
            print(
                "✓ Existing buyer dataset used"
            )

            print(
                "✓ No new ML model"
            )

            print(
                "✓ No dataset modification"
            )

            print(
                "✓ No AI Agent"
            )

        else:

            print(
                "⚠ BUYER MATCHING NOT COMPLETED"
            )

            print(
                "No compatible buyer was found."
            )

    except Exception as exc:

        print()
        print("=" * 70)
        print("✗ BUYER MATCHING TEST FAILED")
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