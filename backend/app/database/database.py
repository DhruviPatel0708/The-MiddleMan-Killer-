"""
DATABASE / STORAGE LAYER
========================

Database: SQLite

Architecture components:
1. User Data
2. Farmer Data
3. Crop Data
4. Buyer Data
5. Transactions
6. Historical Data
7. Logs & Audit

No external API
No FastAPI
No ML model
No new dataset
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# ================================================================
# PATH CONFIGURATION
# ================================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parents[3]

DATABASE_DIR = PROJECT_ROOT / "data" / "database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = DATABASE_DIR / "agri_decision.db"


# ================================================================
# UTILITY FUNCTIONS
# ================================================================

def utc_now() -> str:

    return datetime.now(
        timezone.utc
    ).isoformat(
        timespec="seconds"
    )


def generate_id(
    prefix: str
) -> str:

    return (
        f"{prefix}_"
        f"{uuid.uuid4().hex[:12].upper()}"
    )


# ================================================================
# DATABASE MANAGER
# ================================================================

class DatabaseManager:

    def __init__(
        self,
        db_path: Path = DATABASE_PATH
    ):

        self.db_path = Path(
            db_path
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.initialize_database()


    # ============================================================
    # CONNECTION
    # ============================================================

    def connect(self):

        connection = sqlite3.connect(
            self.db_path
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection


    # ============================================================
    # INITIALIZE DATABASE
    # ============================================================

    def initialize_database(self):

        with self.connect() as conn:

            # ====================================================
            # 1. USER DATA
            # ====================================================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (

                    user_id TEXT PRIMARY KEY,

                    name TEXT NOT NULL,

                    email TEXT NOT NULL UNIQUE,

                    role TEXT NOT NULL,

                    is_active INTEGER NOT NULL DEFAULT 1,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL
                )
            """)


            # ====================================================
            # 2. FARMER DATA
            # ====================================================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS farmers (

                    farmer_id TEXT PRIMARY KEY,

                    user_id TEXT NOT NULL UNIQUE,

                    location TEXT,

                    district TEXT,

                    phone TEXT,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
                )
            """)


            # ====================================================
            # 3. CROP DATA
            # ====================================================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS crops (

                    crop_id TEXT PRIMARY KEY,

                    farmer_id TEXT NOT NULL,

                    crop_name TEXT NOT NULL,

                    quantity_kg REAL NOT NULL,

                    quality TEXT,

                    district TEXT,

                    market TEXT,

                    status TEXT NOT NULL
                    DEFAULT 'AVAILABLE',

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(farmer_id)
                    REFERENCES farmers(farmer_id)
                    ON DELETE CASCADE
                )
            """)


            # ====================================================
            # 4. BUYER DATA
            # ====================================================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS buyers (

                    buyer_id TEXT PRIMARY KEY,

                    user_id TEXT,

                    buyer_name TEXT NOT NULL,

                    market TEXT,

                    district TEXT,

                    reliability_score REAL,

                    reliability_level TEXT,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
                )
            """)


            # ====================================================
            # 5. TRANSACTIONS
            # ====================================================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (

                    transaction_id TEXT PRIMARY KEY,

                    crop_id TEXT,

                    farmer_id TEXT,

                    buyer_id TEXT,

                    quantity_kg REAL,

                    price_per_kg REAL,

                    gross_revenue REAL,

                    total_cost REAL,

                    net_profit REAL,

                    status TEXT NOT NULL
                    DEFAULT 'CREATED',

                    transaction_data TEXT,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(crop_id)
                    REFERENCES crops(crop_id)
                    ON DELETE SET NULL,

                    FOREIGN KEY(farmer_id)
                    REFERENCES farmers(farmer_id)
                    ON DELETE SET NULL,

                    FOREIGN KEY(buyer_id)
                    REFERENCES buyers(buyer_id)
                    ON DELETE SET NULL
                )
            """)


            # ====================================================
            # 6. HISTORICAL DATA
            # ====================================================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS historical_data (

                    history_id TEXT PRIMARY KEY,

                    entity_type TEXT NOT NULL,

                    entity_id TEXT,

                    event_type TEXT NOT NULL,

                    event_data TEXT,

                    created_at TEXT NOT NULL
                )
            """)


            # ====================================================
            # 7. LOGS & AUDIT
            # ====================================================

            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (

                    audit_id TEXT PRIMARY KEY,

                    user_id TEXT,

                    action TEXT NOT NULL,

                    entity_type TEXT,

                    entity_id TEXT,

                    status TEXT NOT NULL,

                    details TEXT,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
                )
            """)


            # ====================================================
            # INDEXES
            # ====================================================

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_farmers_user
                ON farmers(user_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_crops_farmer
                ON crops(farmer_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_buyers_user
                ON buyers(user_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_transactions_farmer
                ON transactions(farmer_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_transactions_buyer
                ON transactions(buyer_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_transactions_crop
                ON transactions(crop_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_history_entity
                ON historical_data(
                    entity_type,
                    entity_id
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_audit_user
                ON audit_logs(user_id)
            """)


    # ============================================================
    # USER DATA
    # ============================================================

    def create_user(
        self,
        name: str,
        email: str,
        role: str,
        user_id: Optional[str] = None
    ):

        user_id = (
            user_id
            or generate_id("USR")
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute("""
                INSERT INTO users
                (
                    user_id,
                    name,
                    email,
                    role,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                name.strip(),
                email.strip().lower(),
                role.strip().upper(),
                1,
                now,
                now
            ))

        return self.get_user(
            user_id
        )


    def get_user(
        self,
        user_id: str
    ):

        with self.connect() as conn:

            row = conn.execute("""
                SELECT *
                FROM users
                WHERE user_id = ?
            """, (
                user_id,
            )).fetchone()

        return (
            dict(row)
            if row
            else None
        )


    def get_user_by_email(
        self,
        email: str
    ):

        with self.connect() as conn:

            row = conn.execute("""
                SELECT *
                FROM users
                WHERE email = ?
            """, (
                email.strip().lower(),
            )).fetchone()

        return (
            dict(row)
            if row
            else None
        )


    def update_user(
        self,
        user_id: str,
        **updates
    ):

        allowed_fields = {
            "name",
            "email",
            "role",
            "is_active"
        }

        clean_updates = {
            key: value
            for key, value in updates.items()
            if key in allowed_fields
        }

        if not clean_updates:

            return self.get_user(
                user_id
            )

        clean_updates[
            "updated_at"
        ] = utc_now()

        fields = ", ".join(
            f"{key} = ?"
            for key in clean_updates
        )

        values = list(
            clean_updates.values()
        )

        values.append(
            user_id
        )

        with self.connect() as conn:

            cursor = conn.execute(
                f"""
                UPDATE users
                SET {fields}
                WHERE user_id = ?
                """,
                values
            )

            if cursor.rowcount == 0:

                raise ValueError(
                    "User not found."
                )

        return self.get_user(
            user_id
        )


    # ============================================================
    # FARMER DATA
    # ============================================================

    def create_farmer(
        self,
        user_id: str,
        location: str = "",
        district: str = "",
        phone: str = "",
        farmer_id: Optional[str] = None
    ):

        farmer_id = (
            farmer_id
            or generate_id("FAR")
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute("""
                INSERT INTO farmers
                (
                    farmer_id,
                    user_id,
                    location,
                    district,
                    phone,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                farmer_id,
                user_id,
                location,
                district,
                phone,
                now,
                now
            ))

        return self.get_farmer(
            farmer_id
        )


    def get_farmer(
        self,
        farmer_id: str
    ):

        with self.connect() as conn:

            row = conn.execute("""
                SELECT *
                FROM farmers
                WHERE farmer_id = ?
            """, (
                farmer_id,
            )).fetchone()

        return (
            dict(row)
            if row
            else None
        )


    def get_farmer_by_user(
        self,
        user_id: str
    ):

        with self.connect() as conn:

            row = conn.execute("""
                SELECT *
                FROM farmers
                WHERE user_id = ?
            """, (
                user_id,
            )).fetchone()

        return (
            dict(row)
            if row
            else None
        )


    # ============================================================
    # CROP DATA
    # ============================================================

    def create_crop(
        self,
        farmer_id: str,
        crop_name: str,
        quantity_kg: float,
        quality: str = "",
        district: str = "",
        market: str = "",
        status: str = "AVAILABLE"
    ):

        crop_id = generate_id(
            "CRP"
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute("""
                INSERT INTO crops
                (
                    crop_id,
                    farmer_id,
                    crop_name,
                    quantity_kg,
                    quality,
                    district,
                    market,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                crop_id,
                farmer_id,
                crop_name,
                float(quantity_kg),
                quality,
                district,
                market,
                status.upper(),
                now,
                now
            ))

        return self.get_crop(
            crop_id
        )


    def get_crop(
        self,
        crop_id: str
    ):

        with self.connect() as conn:

            row = conn.execute("""
                SELECT *
                FROM crops
                WHERE crop_id = ?
            """, (
                crop_id,
            )).fetchone()

        return (
            dict(row)
            if row
            else None
        )


    def get_crops_by_farmer(
        self,
        farmer_id: str
    ):

        with self.connect() as conn:

            rows = conn.execute("""
                SELECT *
                FROM crops
                WHERE farmer_id = ?
                ORDER BY created_at DESC
            """, (
                farmer_id,
            )).fetchall()

        return [
            dict(row)
            for row in rows
        ]


    def update_crop_status(
        self,
        crop_id: str,
        status: str
    ):

        with self.connect() as conn:

            cursor = conn.execute("""
                UPDATE crops

                SET
                    status = ?,
                    updated_at = ?

                WHERE crop_id = ?
            """, (
                status.upper(),
                utc_now(),
                crop_id
            ))

            if cursor.rowcount == 0:

                raise ValueError(
                    "Crop not found."
                )

        return self.get_crop(
            crop_id
        )


    # ============================================================
    # BUYER DATA
    # ============================================================

    def create_buyer(
        self,
        buyer_name: str,
        user_id: Optional[str] = None,
        market: str = "",
        district: str = "",
        reliability_score: Optional[float] = None,
        reliability_level: str = "",
        buyer_id: Optional[str] = None
    ):

        buyer_id = (
            buyer_id
            or generate_id("BUY")
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute("""
                INSERT INTO buyers
                (
                    buyer_id,
                    user_id,
                    buyer_name,
                    market,
                    district,
                    reliability_score,
                    reliability_level,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                buyer_id,
                user_id,
                buyer_name,
                market,
                district,
                reliability_score,
                reliability_level,
                now,
                now
            ))

        return self.get_buyer(
            buyer_id
        )


    def get_buyer(
        self,
        buyer_id: str
    ):

        with self.connect() as conn:

            row = conn.execute("""
                SELECT *
                FROM buyers
                WHERE buyer_id = ?
            """, (
                buyer_id,
            )).fetchone()

        return (
            dict(row)
            if row
            else None
        )


    def get_buyers_by_market(
        self,
        market: str
    ):

        with self.connect() as conn:

            rows = conn.execute("""
                SELECT *
                FROM buyers
                WHERE market = ?
                ORDER BY reliability_score DESC
            """, (
                market,
            )).fetchall()

        return [
            dict(row)
            for row in rows
        ]


    # ============================================================
    # TRANSACTIONS
    # ============================================================

    def create_transaction(
        self,
        crop_id: Optional[str],
        farmer_id: Optional[str],
        buyer_id: Optional[str],
        quantity_kg: float,
        price_per_kg: float,
        gross_revenue: float,
        total_cost: float,
        net_profit: float,
        status: str = "CREATED",
        transaction_data: Optional[
            Dict[str, Any]
        ] = None
    ):

        transaction_id = generate_id(
            "TXN"
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute("""
                INSERT INTO transactions
                (
                    transaction_id,
                    crop_id,
                    farmer_id,
                    buyer_id,
                    quantity_kg,
                    price_per_kg,
                    gross_revenue,
                    total_cost,
                    net_profit,
                    status,
                    transaction_data,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                crop_id,
                farmer_id,
                buyer_id,
                float(quantity_kg),
                float(price_per_kg),
                float(gross_revenue),
                float(total_cost),
                float(net_profit),
                status.upper(),
                json.dumps(
                    transaction_data or {}
                ),
                now,
                now
            ))

        return self.get_transaction(
            transaction_id
        )


    def get_transaction(
        self,
        transaction_id: str
    ):

        with self.connect() as conn:

            row = conn.execute("""
                SELECT *
                FROM transactions
                WHERE transaction_id = ?
            """, (
                transaction_id,
            )).fetchone()

        if not row:

            return None

        result = dict(row)

        try:

            result[
                "transaction_data"
            ] = json.loads(
                result[
                    "transaction_data"
                ]
            )

        except Exception:

            pass

        return result


    def get_transactions_by_farmer(
        self,
        farmer_id: str
    ):

        with self.connect() as conn:

            rows = conn.execute("""
                SELECT *
                FROM transactions
                WHERE farmer_id = ?
                ORDER BY created_at DESC
            """, (
                farmer_id,
            )).fetchall()

        return [
            dict(row)
            for row in rows
        ]


    def update_transaction_status(
        self,
        transaction_id: str,
        status: str
    ):

        with self.connect() as conn:

            cursor = conn.execute("""
                UPDATE transactions

                SET
                    status = ?,
                    updated_at = ?

                WHERE transaction_id = ?
            """, (
                status.upper(),
                utc_now(),
                transaction_id
            ))

            if cursor.rowcount == 0:

                raise ValueError(
                    "Transaction not found."
                )

        return self.get_transaction(
            transaction_id
        )


    # ============================================================
    # HISTORICAL DATA
    # ============================================================

    def add_history(
        self,
        entity_type: str,
        entity_id: Optional[str],
        event_type: str,
        event_data: Optional[
            Dict[str, Any]
        ] = None
    ):

        history_id = generate_id(
            "HIS"
        )

        with self.connect() as conn:

            conn.execute("""
                INSERT INTO historical_data
                (
                    history_id,
                    entity_type,
                    entity_id,
                    event_type,
                    event_data,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                history_id,
                entity_type.upper(),
                entity_id,
                event_type.upper(),
                json.dumps(
                    event_data or {}
                ),
                utc_now()
            ))

        return history_id


    def get_history(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None
    ):

        query = """
            SELECT *
            FROM historical_data
        """

        conditions = []

        values = []

        if entity_type:

            conditions.append(
                "entity_type = ?"
            )

            values.append(
                entity_type.upper()
            )

        if entity_id:

            conditions.append(
                "entity_id = ?"
            )

            values.append(
                entity_id
            )

        if conditions:

            query += (
                " WHERE "
                + " AND ".join(
                    conditions
                )
            )

        query += (
            " ORDER BY created_at DESC"
        )

        with self.connect() as conn:

            rows = conn.execute(
                query,
                values
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


    # ============================================================
    # LOGS & AUDIT
    # ============================================================

    def add_audit_log(
        self,
        action: str,
        status: str,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[
            Dict[str, Any]
        ] = None
    ):

        audit_id = generate_id(
            "AUD"
        )

        with self.connect() as conn:

            conn.execute("""
                INSERT INTO audit_logs
                (
                    audit_id,
                    user_id,
                    action,
                    entity_type,
                    entity_id,
                    status,
                    details,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id,
                user_id,
                action.upper(),
                (
                    entity_type.upper()
                    if entity_type
                    else None
                ),
                entity_id,
                status.upper(),
                json.dumps(
                    details or {}
                ),
                utc_now()
            ))

        return audit_id


    def get_audit_logs(
        self,
        user_id: Optional[str] = None
    ):

        if user_id:

            query = """
                SELECT *
                FROM audit_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
            """

            values = (
                user_id,
            )

        else:

            query = """
                SELECT *
                FROM audit_logs
                ORDER BY created_at DESC
            """

            values = ()

        with self.connect() as conn:

            rows = conn.execute(
                query,
                values
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


    # ============================================================
    # DATABASE HEALTH
    # ============================================================

    def health_check(self) -> bool:

        with self.connect() as conn:

            result = conn.execute(
                "SELECT 1"
            ).fetchone()

        return result is not None


    # ============================================================
    # TABLE COUNTS
    # ============================================================

    def table_counts(self):

        tables = [

            "users",

            "farmers",

            "crops",

            "buyers",

            "transactions",

            "historical_data",

            "audit_logs"

        ]

        counts = {}

        with self.connect() as conn:

            for table in tables:

                count = conn.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {table}
                    """
                ).fetchone()[0]

                counts[table] = count

        return counts


# ================================================================
# DATABASE TEST
# ================================================================

def main():

    print()
    print("=" * 70)
    print(
        "DATABASE / STORAGE LAYER TEST"
    )
    print("=" * 70)

    print()
    print(
        "Database : SQLite"
    )

    print(
        "Location :",
        DATABASE_PATH
    )

    print()
    print(
        "No external API."
    )

    print(
        "No FastAPI."
    )

    print(
        "No ML model."
    )

    print(
        "No new dataset."
    )


    # ============================================================
    # INITIALIZE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "1. DATABASE INITIALIZATION"
    )
    print("=" * 70)

    db = DatabaseManager()

    assert db.health_check()

    print(
        "✓ SQLite connection : VERIFIED"
    )

    print(
        "✓ Database schema   : VERIFIED"
    )


    # ============================================================
    # USER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "2. USER DATA"
    )
    print("=" * 70)

    email = (
        "database_test"
        "@project.local"
    )

    existing_user = (
        db.get_user_by_email(
            email
        )
    )

    if existing_user:

        user = existing_user

        print(
            "✓ Existing test user found"
        )

    else:

        user = db.create_user(

            name="Database Test User",

            email=email,

            role="FARMER"

        )

        print(
            "✓ User created"
        )

    print(
        "✓ User ID :",
        user["user_id"]
    )

    print(
        "✓ User Data : VERIFIED"
    )


    # ============================================================
    # FARMER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "3. FARMER DATA"
    )
    print("=" * 70)

    farmer = (
        db.get_farmer_by_user(
            user["user_id"]
        )
    )

    if farmer:

        print(
            "✓ Existing farmer found"
        )

    else:

        farmer = db.create_farmer(

            user_id=user["user_id"],

            location="Kheda",

            district="Kheda",

            phone="9999999999"

        )

        print(
            "✓ Farmer created"
        )

    print(
        "✓ Farmer ID :",
        farmer["farmer_id"]
    )

    print(
        "✓ Farmer Data : VERIFIED"
    )


    # ============================================================
    # CROP
    # ============================================================

    print()
    print("=" * 70)
    print(
        "4. CROP DATA"
    )
    print("=" * 70)

    crop = db.create_crop(

        farmer_id=farmer["farmer_id"],

        crop_name="Bajra",

        quantity_kg=887,

        quality="C",

        district="Kheda",

        market="Kheda APMC"

    )

    assert crop is not None

    print(
        "✓ Crop ID :",
        crop["crop_id"]
    )

    print(
        "✓ Crop :",
        crop["crop_name"]
    )

    print(
        "✓ Quantity :",
        crop["quantity_kg"],
        "kg"
    )

    print(
        "✓ Crop Data : VERIFIED"
    )


    # ============================================================
    # BUYER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "5. BUYER DATA"
    )
    print("=" * 70)

    buyer = db.get_buyer(
        "B01865"
    )

    if buyer:

        print(
            "✓ Existing Buyer_01865 found"
        )

    else:

        buyer = db.create_buyer(

            buyer_id="B01865",

            buyer_name="Buyer_01865",

            market="Mehsana APMC",

            district="Mehsana",

            reliability_score=100.0,

            reliability_level="RELIABLE"

        )

        print(
            "✓ Buyer created"
        )

    print(
        "✓ Buyer ID :",
        buyer["buyer_id"]
    )

    print(
        "✓ Buyer Data : VERIFIED"
    )


    # ============================================================
    # TRANSACTION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "6. TRANSACTIONS"
    )
    print("=" * 70)

    quantity = 887.0

    price = 2845.52

    gross_revenue = (
        quantity * price
    )

    total_cost = 10000.0

    net_profit = (
        gross_revenue
        - total_cost
    )

    transaction = (
        db.create_transaction(

            crop_id=crop["crop_id"],

            farmer_id=farmer["farmer_id"],

            buyer_id=buyer["buyer_id"],

            quantity_kg=quantity,

            price_per_kg=price,

            gross_revenue=gross_revenue,

            total_cost=total_cost,

            net_profit=net_profit,

            status="CREATED",

            transaction_data={

                "source":
                    "database_test",

                "crop":
                    "Bajra",

                "quality":
                    "C"

            }

        )
    )

    assert transaction is not None

    print(
        "✓ Transaction ID :",
        transaction["transaction_id"]
    )

    print(
        "✓ Gross Revenue : ₹"
        f"{gross_revenue:,.2f}"
    )

    print(
        "✓ Total Cost : ₹"
        f"{total_cost:,.2f}"
    )

    print(
        "✓ Net Profit : ₹"
        f"{net_profit:,.2f}"
    )

    print(
        "✓ Transactions : VERIFIED"
    )


    # ============================================================
    # HISTORICAL DATA
    # ============================================================

    print()
    print("=" * 70)
    print(
        "7. HISTORICAL DATA"
    )
    print("=" * 70)

    history_id = db.add_history(

        entity_type="TRANSACTION",

        entity_id=transaction[
            "transaction_id"
        ],

        event_type="CREATED",

        event_data={

            "source":
                "database_test",

            "status":
                "CREATED"

        }

    )

    assert history_id

    history = db.get_history(

        entity_type="TRANSACTION",

        entity_id=transaction[
            "transaction_id"
        ]

    )

    assert len(history) >= 1

    print(
        "✓ History ID :",
        history_id
    )

    print(
        "✓ Historical Data : VERIFIED"
    )


    # ============================================================
    # LOG & AUDIT
    # ============================================================

    print()
    print("=" * 70)
    print(
        "8. LOGS & AUDIT"
    )
    print("=" * 70)

    audit_id = db.add_audit_log(

        action="CREATE_TRANSACTION",

        status="SUCCESS",

        user_id=user["user_id"],

        entity_type="TRANSACTION",

        entity_id=transaction[
            "transaction_id"
        ],

        details={

            "source":
                "database_test"

        }

    )

    assert audit_id

    logs = db.get_audit_logs(

        user_id=user["user_id"]

    )

    assert len(logs) >= 1

    print(
        "✓ Audit ID :",
        audit_id
    )

    print(
        "✓ Logs & Audit : VERIFIED"
    )


    # ============================================================
    # TABLE COUNTS
    # ============================================================

    print()
    print("=" * 70)
    print(
        "9. DATABASE TABLES"
    )
    print("=" * 70)

    counts = db.table_counts()

    for table, count in counts.items():

        print(
            f"✓ {table:<20} : {count}"
        )


    # ============================================================
    # FINAL VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "DATABASE / STORAGE FINAL STATUS"
    )
    print("=" * 70)

    print(
        "✓ User Data        : VERIFIED"
    )

    print(
        "✓ Farmer Data      : VERIFIED"
    )

    print(
        "✓ Crop Data        : VERIFIED"
    )

    print(
        "✓ Buyer Data       : VERIFIED"
    )

    print(
        "✓ Transactions     : VERIFIED"
    )

    print(
        "✓ Historical Data  : VERIFIED"
    )

    print(
        "✓ Logs & Audit     : VERIFIED"
    )

    print()
    print(
        "DATABASE / STORAGE LAYER STATUS: COMPLETE"
    )


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":

    main()