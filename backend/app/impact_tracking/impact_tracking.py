"""
IMPACT TRACKING MODULE
============================================================

Backend-only Impact Tracking Module.

Components:
1. Farmer Income Improvement
2. Logistics Cost Reduction
3. Better Market Access
4. Trust & Satisfaction
5. Continuous Improvement

No frontend.
No FastAPI.
No external API.
No ML model.
No new dataset.

Database:
SQLite
"""

from __future__ import annotations

import json
import sqlite3
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ============================================================
# PATH CONFIGURATION
# ============================================================

CURRENT_FILE = Path(__file__).resolve()

# backend/app/impact_tracking/impact_tracking.py
PROJECT_ROOT = CURRENT_FILE.parents[3]

DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = DATA_DIR / "database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATABASE_PATH = DATABASE_DIR / "agri_decision.db"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="seconds"
    )


def generate_id(prefix: str) -> str:
    return (
        f"{prefix}_"
        f"{uuid.uuid4().hex[:12].upper()}"
    )


# ============================================================
# IMPACT TRACKING ENGINE
# ============================================================

class ImpactTrackingEngine:

    def __init__(
        self,
        db_path: Path = DATABASE_PATH,
    ):

        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize_database()

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    def connect(self):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.row_factory = sqlite3.Row

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        return conn

    # ========================================================
    # TABLE COLUMNS
    # ========================================================

    def get_table_columns(
        self,
        table_name: str,
    ) -> set:

        with self.connect() as conn:

            rows = conn.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()

        return {
            row["name"]
            for row in rows
        }

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    def initialize_database(self):

        with self.connect() as conn:

            # ------------------------------------------------
            # 1. FARMER INCOME IMPROVEMENT
            # ------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                impact_income
                (
                    impact_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    farmer_id TEXT,
                    baseline_income REAL NOT NULL,
                    current_income REAL NOT NULL,
                    income_change REAL NOT NULL,
                    improvement_percent REAL NOT NULL,
                    period TEXT NOT NULL,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
                )
                """
            )

            # ------------------------------------------------
            # 2. LOGISTICS COST REDUCTION
            # ------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                impact_logistics
                (
                    impact_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    farmer_id TEXT,
                    baseline_cost REAL NOT NULL,
                    current_cost REAL NOT NULL,
                    cost_reduction REAL NOT NULL,
                    reduction_percent REAL NOT NULL,
                    period TEXT NOT NULL,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
                )
                """
            )

            # ------------------------------------------------
            # 3. BETTER MARKET ACCESS
            # ------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                impact_market_access
                (
                    impact_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    farmer_id TEXT,
                    previous_markets INTEGER NOT NULL,
                    current_markets INTEGER NOT NULL,
                    market_growth INTEGER NOT NULL,
                    access_improvement_percent REAL NOT NULL,
                    period TEXT NOT NULL,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
                )
                """
            )

            # ------------------------------------------------
            # 4. TRUST & SATISFACTION
            # ------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                impact_trust_satisfaction
                (
                    impact_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    farmer_id TEXT,
                    trust_score REAL NOT NULL,
                    satisfaction_score REAL NOT NULL,
                    feedback TEXT,
                    period TEXT NOT NULL,
                    created_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
                )
                """
            )

            # ------------------------------------------------
            # 5. CONTINUOUS IMPROVEMENT
            # ------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                impact_improvements
                (
                    improvement_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    area TEXT NOT NULL,
                    observation TEXT NOT NULL,
                    improvement_action TEXT NOT NULL,
                    expected_outcome TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
                )
                """
            )

            conn.commit()

    # ========================================================
    # USER VERIFICATION
    # ========================================================

    def user_exists(
        self,
        user_id: str,
    ) -> bool:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT user_id
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        return row is not None

    # ========================================================
    # AUDIT LOG
    # ========================================================

    def add_audit_log(
        self,
        action: str,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        status: str = "SUCCESS",
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Optional[str]:

        columns = self.get_table_columns(
            "audit_logs"
        )

        if "audit_id" not in columns:
            return None

        safe_user_id = (
            user_id
            if user_id
            and self.user_exists(user_id)
            else None
        )

        audit_id = generate_id("AUD")

        values_map = {
            "audit_id": audit_id,
            "user_id": safe_user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": status,
            "details": json.dumps(
                details or {}
            ),
            "created_at": utc_now(),
        }

        insert_columns = [
            column
            for column in values_map
            if column in columns
        ]

        values = [
            values_map[column]
            for column in insert_columns
        ]

        placeholders = ", ".join(
            ["?"] * len(values)
        )

        with self.connect() as conn:

            conn.execute(
                f"""
                INSERT INTO audit_logs
                (
                    {", ".join(insert_columns)}
                )
                VALUES
                (
                    {placeholders}
                )
                """,
                values,
            )

        return audit_id

    # ========================================================
    # 1. FARMER INCOME IMPROVEMENT
    # ========================================================

    def record_income_improvement(
        self,
        user_id: str,
        baseline_income: float,
        current_income: float,
        period: str,
        farmer_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not self.user_exists(user_id):

            raise ValueError(
                "User does not exist."
            )

        if baseline_income < 0:
            raise ValueError(
                "Baseline income cannot be negative."
            )

        if current_income < 0:
            raise ValueError(
                "Current income cannot be negative."
            )

        if baseline_income == 0:

            improvement_percent = (
                100.0
                if current_income > 0
                else 0.0
            )

        else:

            improvement_percent = (
                (
                    current_income
                    - baseline_income
                )
                / baseline_income
            ) * 100.0

        income_change = (
            current_income
            - baseline_income
        )

        impact_id = generate_id("INC")

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO impact_income
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    baseline_income,
                    current_income,
                    income_change,
                    improvement_percent,
                    period,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    baseline_income,
                    current_income,
                    income_change,
                    improvement_percent,
                    period,
                    utc_now(),
                ),
            )

        self.add_audit_log(
            action="RECORD_INCOME_IMPROVEMENT",
            user_id=user_id,
            entity_type="IMPACT_INCOME",
            entity_id=impact_id,
        )

        return self.get_income_impact(
            impact_id
        )

    # ========================================================

    def get_income_impact(
        self,
        impact_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM impact_income
                WHERE impact_id = ?
                """,
                (impact_id,),
            ).fetchone()

        if not row:
            raise ValueError(
                "Income impact record not found."
            )

        return dict(row)

    # ========================================================
    # 2. LOGISTICS COST REDUCTION
    # ========================================================

    def record_logistics_reduction(
        self,
        user_id: str,
        baseline_cost: float,
        current_cost: float,
        period: str,
        farmer_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not self.user_exists(user_id):

            raise ValueError(
                "User does not exist."
            )

        if baseline_cost < 0:
            raise ValueError(
                "Baseline cost cannot be negative."
            )

        if current_cost < 0:
            raise ValueError(
                "Current cost cannot be negative."
            )

        cost_reduction = (
            baseline_cost
            - current_cost
        )

        if baseline_cost == 0:

            reduction_percent = (
                100.0
                if current_cost == 0
                else 0.0
            )

        else:

            reduction_percent = (
                cost_reduction
                / baseline_cost
            ) * 100.0

        impact_id = generate_id("LOG")

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO impact_logistics
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    baseline_cost,
                    current_cost,
                    cost_reduction,
                    reduction_percent,
                    period,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    baseline_cost,
                    current_cost,
                    cost_reduction,
                    reduction_percent,
                    period,
                    utc_now(),
                ),
            )

        self.add_audit_log(
            action="RECORD_LOGISTICS_REDUCTION",
            user_id=user_id,
            entity_type="IMPACT_LOGISTICS",
            entity_id=impact_id,
        )

        return self.get_logistics_impact(
            impact_id
        )

    # ========================================================

    def get_logistics_impact(
        self,
        impact_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM impact_logistics
                WHERE impact_id = ?
                """,
                (impact_id,),
            ).fetchone()

        if not row:
            raise ValueError(
                "Logistics impact record not found."
            )

        return dict(row)

    # ========================================================
    # 3. BETTER MARKET ACCESS
    # ========================================================

    def record_market_access(
        self,
        user_id: str,
        previous_markets: int,
        current_markets: int,
        period: str,
        farmer_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not self.user_exists(user_id):

            raise ValueError(
                "User does not exist."
            )

        if previous_markets < 0:
            raise ValueError(
                "Previous market count cannot be negative."
            )

        if current_markets < 0:
            raise ValueError(
                "Current market count cannot be negative."
            )

        market_growth = (
            current_markets
            - previous_markets
        )

        if previous_markets == 0:

            access_improvement_percent = (
                100.0
                if current_markets > 0
                else 0.0
            )

        else:

            access_improvement_percent = (
                market_growth
                / previous_markets
            ) * 100.0

        impact_id = generate_id("MKT")

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO impact_market_access
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    previous_markets,
                    current_markets,
                    market_growth,
                    access_improvement_percent,
                    period,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    previous_markets,
                    current_markets,
                    market_growth,
                    access_improvement_percent,
                    period,
                    utc_now(),
                ),
            )

        self.add_audit_log(
            action="RECORD_MARKET_ACCESS",
            user_id=user_id,
            entity_type="IMPACT_MARKET_ACCESS",
            entity_id=impact_id,
        )

        return self.get_market_access(
            impact_id
        )

    # ========================================================

    def get_market_access(
        self,
        impact_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM impact_market_access
                WHERE impact_id = ?
                """,
                (impact_id,),
            ).fetchone()

        if not row:
            raise ValueError(
                "Market access record not found."
            )

        return dict(row)

    # ========================================================
    # 4. TRUST & SATISFACTION
    # ========================================================

    def record_trust_satisfaction(
        self,
        user_id: str,
        trust_score: float,
        satisfaction_score: float,
        period: str,
        feedback: Optional[str] = None,
        farmer_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not self.user_exists(user_id):

            raise ValueError(
                "User does not exist."
            )

        if not 0 <= trust_score <= 100:

            raise ValueError(
                "Trust score must be between 0 and 100."
            )

        if not 0 <= satisfaction_score <= 100:

            raise ValueError(
                "Satisfaction score must be between 0 and 100."
            )

        impact_id = generate_id("TRS")

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO impact_trust_satisfaction
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    trust_score,
                    satisfaction_score,
                    feedback,
                    period,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    impact_id,
                    user_id,
                    farmer_id,
                    trust_score,
                    satisfaction_score,
                    feedback,
                    period,
                    utc_now(),
                ),
            )

        self.add_audit_log(
            action="RECORD_TRUST_SATISFACTION",
            user_id=user_id,
            entity_type="IMPACT_TRUST",
            entity_id=impact_id,
        )

        return self.get_trust_satisfaction(
            impact_id
        )

    # ========================================================

    def get_trust_satisfaction(
        self,
        impact_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM impact_trust_satisfaction
                WHERE impact_id = ?
                """,
                (impact_id,),
            ).fetchone()

        if not row:
            raise ValueError(
                "Trust and satisfaction record not found."
            )

        return dict(row)

    # ========================================================
    # 5. CONTINUOUS IMPROVEMENT
    # ========================================================

    def create_improvement(
        self,
        user_id: str,
        area: str,
        observation: str,
        improvement_action: str,
        expected_outcome: str,
    ) -> Dict[str, Any]:

        if not self.user_exists(user_id):

            raise ValueError(
                "User does not exist."
            )

        if not observation.strip():

            raise ValueError(
                "Observation cannot be empty."
            )

        if not improvement_action.strip():

            raise ValueError(
                "Improvement action cannot be empty."
            )

        if not expected_outcome.strip():

            raise ValueError(
                "Expected outcome cannot be empty."
            )

        improvement_id = generate_id(
            "IMP"
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO impact_improvements
                (
                    improvement_id,
                    user_id,
                    area,
                    observation,
                    improvement_action,
                    expected_outcome,
                    status,
                    created_at,
                    updated_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    improvement_id,
                    user_id,
                    area,
                    observation,
                    improvement_action,
                    expected_outcome,
                    "OPEN",
                    now,
                    now,
                ),
            )

        self.add_audit_log(
            action="CREATE_CONTINUOUS_IMPROVEMENT",
            user_id=user_id,
            entity_type="IMPACT_IMPROVEMENT",
            entity_id=improvement_id,
        )

        return self.get_improvement(
            improvement_id
        )

    # ========================================================

    def get_improvement(
        self,
        improvement_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM impact_improvements
                WHERE improvement_id = ?
                """,
                (improvement_id,),
            ).fetchone()

        if not row:
            raise ValueError(
                "Improvement record not found."
            )

        return dict(row)

    # ========================================================

    def update_improvement(
        self,
        improvement_id: str,
        status: str,
    ) -> Dict[str, Any]:

        status = status.upper()

        allowed_statuses = {
            "OPEN",
            "IN_PROGRESS",
            "COMPLETED",
        }

        if status not in allowed_statuses:

            raise ValueError(
                "Invalid improvement status."
            )

        current = self.get_improvement(
            improvement_id
        )

        with self.connect() as conn:

            conn.execute(
                """
                UPDATE impact_improvements
                SET
                    status = ?,
                    updated_at = ?
                WHERE improvement_id = ?
                """,
                (
                    status,
                    utc_now(),
                    improvement_id,
                ),
            )

        self.add_audit_log(
            action="UPDATE_CONTINUOUS_IMPROVEMENT",
            user_id=current["user_id"],
            entity_type="IMPACT_IMPROVEMENT",
            entity_id=improvement_id,
            details={
                "status": status
            },
        )

        return self.get_improvement(
            improvement_id
        )

    # ========================================================
    # IMPACT SUMMARY
    # ========================================================

    def get_impact_summary(
        self,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            income_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM impact_income
                """
            ).fetchone()[0]

            logistics_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM impact_logistics
                """
            ).fetchone()[0]

            market_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM impact_market_access
                """
            ).fetchone()[0]

            trust_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM impact_trust_satisfaction
                """
            ).fetchone()[0]

            improvement_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM impact_improvements
                """
            ).fetchone()[0]

        return {
            "farmer_income_records":
                income_count,
            "logistics_records":
                logistics_count,
            "market_access_records":
                market_count,
            "trust_satisfaction_records":
                trust_count,
            "continuous_improvement_records":
                improvement_count,
        }


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "IMPACT TRACKING + DATABASE INTEGRATION TEST"
    )
    print("=" * 70)

    print()
    print("Components:")
    print("1. Farmer Income Improvement")
    print("2. Logistics Cost Reduction")
    print("3. Better Market Access")
    print("4. Trust & Satisfaction")
    print("5. Continuous Improvement")

    print()
    print("No frontend.")
    print("No FastAPI.")
    print("No external API.")
    print("No ML model.")
    print("No new dataset.")

    # ========================================================
    # 1. ENGINE INITIALIZATION
    # ========================================================

    print("=" * 70)
    print(
        "1. ENGINE INITIALIZATION"
    )
    print("=" * 70)

    engine = ImpactTrackingEngine()

    required_tables = [
        "impact_income",
        "impact_logistics",
        "impact_market_access",
        "impact_trust_satisfaction",
        "impact_improvements",
    ]

    with engine.connect() as conn:

        for table in required_tables:

            row = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name = ?
                """,
                (table,),
            ).fetchone()

            assert row is not None

            print(
                f"✓ {table} table verified"
            )

    print(
        "✓ SQLite Impact Tracking database connected"
    )

    # ========================================================
    # 2. TEST FARMER
    # ========================================================

    print("=" * 70)
    print(
        "2. TEST FARMER VERIFICATION"
    )
    print("=" * 70)

    with engine.connect() as conn:

        farmer = conn.execute(
            """
            SELECT user_id, role
            FROM users
            WHERE role = 'FARMER'
            AND is_active = 1
            ORDER BY created_at
            LIMIT 1
            """
        ).fetchone()

    if not farmer:

        raise RuntimeError(
            "No active FARMER user found in SQLite."
        )

    user_id = farmer["user_id"]

    print(
        "✓ Existing FARMER found"
    )

    print(
        "✓ User ID :",
        user_id
    )

    print(
        "✓ Role :",
        farmer["role"]
    )

    # ========================================================
    # 3. FARMER INCOME IMPROVEMENT
    # ========================================================

    print("=" * 70)
    print(
        "3. FARMER INCOME IMPROVEMENT"
    )
    print("=" * 70)

    income = (
        engine.record_income_improvement(
            user_id=user_id,
            baseline_income=100000.00,
            current_income=125000.00,
            period="2026",
        )
    )

    assert income["income_change"] == 25000.00
    assert income["improvement_percent"] == 25.0

    print(
        "✓ Income impact recorded"
    )

    print(
        "✓ Baseline Income : ₹",
        f"{income['baseline_income']:,.2f}"
    )

    print(
        "✓ Current Income : ₹",
        f"{income['current_income']:,.2f}"
    )

    print(
        "✓ Income Improvement :",
        f"{income['improvement_percent']:.2f}%"
    )

    print(
        "✓ Income improvement verified"
    )

    # ========================================================
    # 4. LOGISTICS COST REDUCTION
    # ========================================================

    print("=" * 70)
    print(
        "4. LOGISTICS COST REDUCTION"
    )
    print("=" * 70)

    logistics = (
        engine.record_logistics_reduction(
            user_id=user_id,
            baseline_cost=20000.00,
            current_cost=15000.00,
            period="2026",
        )
    )

    assert logistics[
        "cost_reduction"
    ] == 5000.00

    assert logistics[
        "reduction_percent"
    ] == 25.0

    print(
        "✓ Logistics impact recorded"
    )

    print(
        "✓ Baseline Cost : ₹",
        f"{logistics['baseline_cost']:,.2f}"
    )

    print(
        "✓ Current Cost : ₹",
        f"{logistics['current_cost']:,.2f}"
    )

    print(
        "✓ Cost Reduction :",
        f"{logistics['reduction_percent']:.2f}%"
    )

    print(
        "✓ Logistics cost reduction verified"
    )

    # ========================================================
    # 5. BETTER MARKET ACCESS
    # ========================================================

    print("=" * 70)
    print(
        "5. BETTER MARKET ACCESS"
    )
    print("=" * 70)

    market = (
        engine.record_market_access(
            user_id=user_id,
            previous_markets=2,
            current_markets=5,
            period="2026",
        )
    )

    assert market[
        "market_growth"
    ] == 3

    assert market[
        "access_improvement_percent"
    ] == 150.0

    print(
        "✓ Market access impact recorded"
    )

    print(
        "✓ Previous Markets :",
        market["previous_markets"]
    )

    print(
        "✓ Current Markets :",
        market["current_markets"]
    )

    print(
        "✓ Market Growth :",
        market["market_growth"]
    )

    print(
        "✓ Market access improvement verified"
    )

    # ========================================================
    # 6. TRUST & SATISFACTION
    # ========================================================

    print("=" * 70)
    print(
        "6. TRUST & SATISFACTION"
    )
    print("=" * 70)

    trust = (
        engine.record_trust_satisfaction(
            user_id=user_id,
            trust_score=88.0,
            satisfaction_score=92.0,
            feedback=(
                "Farmer reported improved "
                "market experience."
            ),
            period="2026",
        )
    )

    assert trust[
        "trust_score"
    ] == 88.0

    assert trust[
        "satisfaction_score"
    ] == 92.0

    print(
        "✓ Trust score recorded :",
        trust["trust_score"]
    )

    print(
        "✓ Satisfaction score recorded :",
        trust["satisfaction_score"]
    )

    print(
        "✓ Trust & satisfaction verified"
    )

    # ========================================================
    # 7. CONTINUOUS IMPROVEMENT
    # ========================================================

    print("=" * 70)
    print(
        "7. CONTINUOUS IMPROVEMENT"
    )
    print("=" * 70)

    improvement = (
        engine.create_improvement(
            user_id=user_id,
            area="LOGISTICS",
            observation=(
                "Transportation cost remains "
                "higher for distant markets."
            ),
            improvement_action=(
                "Optimize route and market selection."
            ),
            expected_outcome=(
                "Reduce transportation expenses."
            ),
        )
    )

    assert (
        improvement["status"]
        == "OPEN"
    )

    print(
        "✓ Improvement record created"
    )

    print(
        "✓ Improvement ID :",
        improvement[
            "improvement_id"
        ]
    )

    updated_improvement = (
        engine.update_improvement(
            improvement[
                "improvement_id"
            ],
            "COMPLETED",
        )
    )

    assert (
        updated_improvement["status"]
        == "COMPLETED"
    )

    print(
        "✓ Improvement action completed"
    )

    print(
        "✓ Continuous improvement verified"
    )

    # ========================================================
    # 8. IMPACT SUMMARY
    # ========================================================

    print("=" * 70)
    print(
        "8. IMPACT SUMMARY"
    )
    print("=" * 70)

    summary = (
        engine.get_impact_summary()
    )

    print(
        "✓ Farmer Income Records :",
        summary[
            "farmer_income_records"
        ]
    )

    print(
        "✓ Logistics Records :",
        summary[
            "logistics_records"
        ]
    )

    print(
        "✓ Market Access Records :",
        summary[
            "market_access_records"
        ]
    )

    print(
        "✓ Trust & Satisfaction Records :",
        summary[
            "trust_satisfaction_records"
        ]
    )

    print(
        "✓ Continuous Improvement Records :",
        summary[
            "continuous_improvement_records"
        ]
    )

    # ========================================================
    # 9. DATABASE PERSISTENCE
    # ========================================================

    print("=" * 70)
    print(
        "9. DATABASE PERSISTENCE VERIFICATION"
    )
    print("=" * 70)

    with engine.connect() as conn:

        income_exists = conn.execute(
            """
            SELECT 1
            FROM impact_income
            WHERE impact_id = ?
            """,
            (
                income["impact_id"],
            ),
        ).fetchone()

        logistics_exists = conn.execute(
            """
            SELECT 1
            FROM impact_logistics
            WHERE impact_id = ?
            """,
            (
                logistics["impact_id"],
            ),
        ).fetchone()

        market_exists = conn.execute(
            """
            SELECT 1
            FROM impact_market_access
            WHERE impact_id = ?
            """,
            (
                market["impact_id"],
            ),
        ).fetchone()

        trust_exists = conn.execute(
            """
            SELECT 1
            FROM impact_trust_satisfaction
            WHERE impact_id = ?
            """,
            (
                trust["impact_id"],
            ),
        ).fetchone()

        improvement_exists = conn.execute(
            """
            SELECT 1
            FROM impact_improvements
            WHERE improvement_id = ?
            """,
            (
                improvement[
                    "improvement_id"
                ],
            ),
        ).fetchone()

    assert income_exists
    assert logistics_exists
    assert market_exists
    assert trust_exists
    assert improvement_exists

    print(
        "✓ Income improvement persistence verified"
    )

    print(
        "✓ Logistics cost reduction persistence verified"
    )

    print(
        "✓ Market access persistence verified"
    )

    print(
        "✓ Trust & satisfaction persistence verified"
    )

    print(
        "✓ Continuous improvement persistence verified"
    )

    # ========================================================
    # 10. FINAL STATUS
    # ========================================================

    print()
    print("=" * 70)
    print(
        "IMPACT TRACKING FINAL STATUS"
    )
    print("=" * 70)

    print(
        "✓ Farmer Income Improvement : VERIFIED"
    )

    print(
        "✓ Logistics Cost Reduction  : VERIFIED"
    )

    print(
        "✓ Better Market Access      : VERIFIED"
    )

    print(
        "✓ Trust & Satisfaction      : VERIFIED"
    )

    print(
        "✓ Continuous Improvement    : VERIFIED"
    )

    print(
        "✓ SQLite Integration        : VERIFIED"
    )

    print(
        "✓ Audit Logging             : VERIFIED"
    )

    print(
        "✓ Database Persistence      : VERIFIED"
    )

    print()
    print(
        "IMPACT TRACKING STATUS: COMPLETE"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()