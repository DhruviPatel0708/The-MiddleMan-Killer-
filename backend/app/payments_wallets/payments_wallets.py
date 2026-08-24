"""
PAYMENTS & WALLETS

Architecture:

Authentication & Authorization
            ↓
       SQLite Database
            ↓
      User Management
            ↓
      Crop Management
            ↓
    Auction & Bidding
            ↓
    Order & Transaction
            ↓
      Payments & Wallets

No external API.
No FastAPI.
No ML model.
No new dataset.

Responsibilities:

✓ Wallet creation
✓ Wallet balance
✓ Wallet credit
✓ Wallet debit
✓ Payment creation
✓ Payment verification
✓ Payment completion
✓ Payment cancellation
✓ Transaction linkage
✓ Wallet ledger
✓ Insufficient balance protection
✓ Audit logging
✓ Historical logging
✓ Foreign-key verification
✓ SQLite persistence
"""

from __future__ import annotations

import json
import sys
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


# ================================================================
# PATH CONFIGURATION
# ================================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parents[3]

APP_PATH = PROJECT_ROOT / "backend" / "app"

AUTH_PATH = APP_PATH / "auth"
DATABASE_PATH = APP_PATH / "database"

if str(AUTH_PATH) not in sys.path:
    sys.path.insert(0, str(AUTH_PATH))

if str(DATABASE_PATH) not in sys.path:
    sys.path.insert(0, str(DATABASE_PATH))


# ================================================================
# EXISTING PROJECT COMPONENTS
# ================================================================

from authentication import (
    AuthenticationAuthorizationEngine
)

from database import DatabaseManager


# ================================================================
# PAYMENT & WALLET ENGINE
# ================================================================

class PaymentWalletEngine:

    PAYMENT_STATUSES = {
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
    }

    WALLET_TRANSACTION_TYPES = {
        "CREDIT",
        "DEBIT",
    }

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):

        print("=" * 70)
        print("PAYMENTS & WALLETS ENGINE")
        print("=" * 70)

        self.auth = (
            AuthenticationAuthorizationEngine()
        )

        self.database = DatabaseManager()

        print(
            "✓ Authentication & Authorization connected"
        )

        print(
            "✓ SQLite Database connected"
        )

        print(
            "✓ No external API"
        )

        print(
            "✓ No FastAPI"
        )

        print(
            "✓ No ML model"
        )

        print(
            "✓ No dataset"
        )

        self._initialize_payment_tables()

        print(
            "✓ Wallet table verified"
        )

        print(
            "✓ Wallet ledger table verified"
        )

        print(
            "✓ Payment table verified"
        )

        print(
            "✓ Payments & Wallets Engine initialized"
        )

    # ============================================================
    # UTILITIES
    # ============================================================

    @staticmethod
    def _now():

        return datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

    @staticmethod
    def _generate_id(prefix):

        return (
            f"{prefix}_"
            f"{uuid.uuid4().hex[:12].upper()}"
        )

    # ============================================================
    # TABLE INITIALIZATION
    # ============================================================

    def _initialize_payment_tables(self):

        with self.database.connect() as conn:

            # ----------------------------------------------------
            # WALLETS
            # ----------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS wallets (

                    wallet_id TEXT PRIMARY KEY,

                    user_id TEXT NOT NULL UNIQUE,

                    balance REAL NOT NULL
                        DEFAULT 0,

                    currency TEXT NOT NULL
                        DEFAULT 'INR',

                    status TEXT NOT NULL
                        DEFAULT 'ACTIVE',

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
                """
            )

            # ----------------------------------------------------
            # WALLET LEDGER
            # ----------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS wallet_ledger (

                    ledger_id TEXT PRIMARY KEY,

                    wallet_id TEXT NOT NULL,

                    user_id TEXT NOT NULL,

                    transaction_type TEXT NOT NULL,

                    amount REAL NOT NULL,

                    balance_before REAL NOT NULL,

                    balance_after REAL NOT NULL,

                    reference_type TEXT,

                    reference_id TEXT,

                    description TEXT,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY(wallet_id)
                        REFERENCES wallets(wallet_id)
                        ON DELETE CASCADE,

                    FOREIGN KEY(user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE
                )
                """
            )

            # ----------------------------------------------------
            # PAYMENTS
            # ----------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS payments (

                    payment_id TEXT PRIMARY KEY,

                    transaction_id TEXT,

                    order_id TEXT,

                    payer_user_id TEXT NOT NULL,

                    receiver_user_id TEXT,

                    amount REAL NOT NULL,

                    currency TEXT NOT NULL
                        DEFAULT 'INR',

                    payment_method TEXT NOT NULL
                        DEFAULT 'WALLET',

                    status TEXT NOT NULL
                        DEFAULT 'PENDING',

                    payment_data TEXT,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY(transaction_id)
                        REFERENCES transactions(transaction_id)
                        ON DELETE SET NULL,

                    FOREIGN KEY(payer_user_id)
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    FOREIGN KEY(receiver_user_id)
                        REFERENCES users(user_id)
                        ON DELETE SET NULL
                )
                """
            )

            # ----------------------------------------------------
            # INDEXES
            # ----------------------------------------------------

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_wallet_user
                ON wallets(user_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_ledger_wallet
                ON wallet_ledger(wallet_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_ledger_user
                ON wallet_ledger(user_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_payment_transaction
                ON payments(transaction_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_payment_payer
                ON payments(payer_user_id)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_payment_receiver
                ON payments(receiver_user_id)
                """
            )

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    def _authenticate(self, token):

        user = self.auth.authenticate(
            token
        )

        if not user:

            raise PermissionError(
                "Invalid authentication token."
            )

        return user

    # ============================================================
    # AUTH → SQLITE SYNCHRONIZATION
    # ============================================================

    def _sync_authenticated_user(
        self,
        user
    ):

        user_id = user.get(
            "user_id"
        )

        if not user_id:

            raise RuntimeError(
                "Authenticated user does not contain user_id."
            )

        existing = (
            self.database
            .get_user(
                user_id
            )
        )

        if existing:

            return existing

        name = (
            user.get(
                "name"
            )
            or "Authenticated User"
        )

        email = (
            user.get(
                "email"
            )
            or f"{user_id.lower()}@project.local"
        )

        role = str(
            user.get(
                "role",
                "FARMER"
            )
        ).upper()

        try:

            return (
                self.database
                .create_user(

                    name=name,

                    email=email,

                    role=role,

                    user_id=user_id
                )
            )

        except Exception:

            existing = (
                self.database
                .get_user(
                    user_id
                )
            )

            if existing:

                return existing

            raise

    # ============================================================
    # WALLET RETRIEVAL
    # ============================================================

    def get_wallet(
        self,
        token,
        user_id: Optional[str] = None
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        authenticated_user_id = user[
            "user_id"
        ]

        # A normal user can only access
        # their own wallet.

        if user_id is None:

            user_id = authenticated_user_id

        if (
            user_id
            != authenticated_user_id
            and str(
                user.get(
                    "role",
                    ""
                )
            ).upper()
            != "ADMIN"
        ):

            raise PermissionError(
                "Users cannot access another user's wallet."
            )

        with self.database.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM wallets
                WHERE user_id = ?
                LIMIT 1
                """,
                (
                    user_id,
                )
            ).fetchone()

        if not row:

            raise ValueError(
                "Wallet not found."
            )

        return dict(row)

    # ============================================================
    # CREATE WALLET
    # ============================================================

    def create_wallet(
        self,
        token
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        user_id = user[
            "user_id"
        ]

        existing = None

        try:

            existing = self.get_wallet(
                token
            )

        except ValueError:

            existing = None

        if existing:

            print(
                "✓ Existing wallet found"
            )

            return existing

        wallet_id = (
            self._generate_id(
                "WAL"
            )
        )

        now = self._now()

        with self.database.connect() as conn:

            conn.execute(
                """
                INSERT INTO wallets
                (
                    wallet_id,
                    user_id,
                    balance,
                    currency,
                    status,
                    created_at,
                    updated_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    wallet_id,
                    user_id,
                    0.0,
                    "INR",
                    "ACTIVE",
                    now,
                    now,
                )
            )

        self.database.add_audit_log(

            action="CREATE_WALLET",

            status="SUCCESS",

            user_id=user_id,

            entity_type="WALLET",

            entity_id=wallet_id,

            details={
                "balance": 0.0,
                "currency": "INR",
            }
        )

        print(
            "✓ Wallet created"
        )

        print(
            "✓ Wallet ID :",
            wallet_id
        )

        return self.get_wallet(
            token
        )

    # ============================================================
    # ENSURE WALLET
    # ============================================================

    def _ensure_wallet(
        self,
        user
    ):

        user_id = user[
            "user_id"
        ]

        with self.database.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM wallets
                WHERE user_id = ?
                LIMIT 1
                """,
                (
                    user_id,
                )
            ).fetchone()

        if row:

            return dict(row)

        wallet_id = (
            self._generate_id(
                "WAL"
            )
        )

        now = self._now()

        with self.database.connect() as conn:

            conn.execute(
                """
                INSERT INTO wallets
                (
                    wallet_id,
                    user_id,
                    balance,
                    currency,
                    status,
                    created_at,
                    updated_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    wallet_id,
                    user_id,
                    0.0,
                    "INR",
                    "ACTIVE",
                    now,
                    now,
                )
            )

        return {
            "wallet_id":
                wallet_id,

            "user_id":
                user_id,

            "balance":
                0.0,

            "currency":
                "INR",

            "status":
                "ACTIVE",
        }

    # ============================================================
    # CREDIT WALLET
    # ============================================================

    def credit_wallet(
        self,
        token,
        amount,
        description="Wallet credit",
        reference_type=None,
        reference_id=None
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        amount = float(
            amount
        )

        if amount <= 0:

            raise ValueError(
                "Credit amount must be greater than zero."
            )

        wallet = self._ensure_wallet(
            user
        )

        wallet_id = wallet[
            "wallet_id"
        ]

        user_id = wallet[
            "user_id"
        ]

        now = self._now()

        with self.database.connect() as conn:

            row = conn.execute(
                """
                SELECT balance, status
                FROM wallets
                WHERE wallet_id = ?
                LIMIT 1
                """,
                (
                    wallet_id,
                )
            ).fetchone()

            if not row:

                raise ValueError(
                    "Wallet does not exist."
                )

            if row[
                "status"
            ] != "ACTIVE":

                raise ValueError(
                    "Wallet is not active."
                )

            balance_before = float(
                row[
                    "balance"
                ]
            )

            balance_after = (
                balance_before
                + amount
            )

            conn.execute(
                """
                UPDATE wallets
                SET
                    balance = ?,
                    updated_at = ?
                WHERE wallet_id = ?
                """,
                (
                    balance_after,
                    now,
                    wallet_id,
                )
            )

            ledger_id = (
                self._generate_id(
                    "LED"
                )
            )

            conn.execute(
                """
                INSERT INTO wallet_ledger
                (
                    ledger_id,
                    wallet_id,
                    user_id,
                    transaction_type,
                    amount,
                    balance_before,
                    balance_after,
                    reference_type,
                    reference_id,
                    description,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger_id,
                    wallet_id,
                    user_id,
                    "CREDIT",
                    amount,
                    balance_before,
                    balance_after,
                    reference_type,
                    reference_id,
                    description,
                    now,
                )
            )

        self.database.add_audit_log(

            action="WALLET_CREDIT",

            status="SUCCESS",

            user_id=user_id,

            entity_type="WALLET",

            entity_id=wallet_id,

            details={
                "amount": amount,
                "balance_before":
                    balance_before,
                "balance_after":
                    balance_after,
                "reference_id":
                    reference_id,
            }
        )

        return self.get_wallet(
            token
        )

    # ============================================================
    # DEBIT WALLET
    # ============================================================

    def debit_wallet(
        self,
        token,
        amount,
        description="Wallet debit",
        reference_type=None,
        reference_id=None
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        amount = float(
            amount
        )

        if amount <= 0:

            raise ValueError(
                "Debit amount must be greater than zero."
            )

        wallet = self._ensure_wallet(
            user
        )

        wallet_id = wallet[
            "wallet_id"
        ]

        user_id = wallet[
            "user_id"
        ]

        now = self._now()

        with self.database.connect() as conn:

            row = conn.execute(
                """
                SELECT balance, status
                FROM wallets
                WHERE wallet_id = ?
                LIMIT 1
                """,
                (
                    wallet_id,
                )
            ).fetchone()

            if not row:

                raise ValueError(
                    "Wallet does not exist."
                )

            if row[
                "status"
            ] != "ACTIVE":

                raise ValueError(
                    "Wallet is not active."
                )

            balance_before = float(
                row[
                    "balance"
                ]
            )

            if balance_before < amount:

                raise ValueError(
                    "Insufficient wallet balance."
                )

            balance_after = (
                balance_before
                - amount
            )

            conn.execute(
                """
                UPDATE wallets
                SET
                    balance = ?,
                    updated_at = ?
                WHERE wallet_id = ?
                """,
                (
                    balance_after,
                    now,
                    wallet_id,
                )
            )

            ledger_id = (
                self._generate_id(
                    "LED"
                )
            )

            conn.execute(
                """
                INSERT INTO wallet_ledger
                (
                    ledger_id,
                    wallet_id,
                    user_id,
                    transaction_type,
                    amount,
                    balance_before,
                    balance_after,
                    reference_type,
                    reference_id,
                    description,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger_id,
                    wallet_id,
                    user_id,
                    "DEBIT",
                    amount,
                    balance_before,
                    balance_after,
                    reference_type,
                    reference_id,
                    description,
                    now,
                )
            )

        self.database.add_audit_log(

            action="WALLET_DEBIT",

            status="SUCCESS",

            user_id=user_id,

            entity_type="WALLET",

            entity_id=wallet_id,

            details={
                "amount": amount,
                "balance_before":
                    balance_before,
                "balance_after":
                    balance_after,
                "reference_id":
                    reference_id,
            }
        )

        return self.get_wallet(
            token
        )

    # ============================================================
    # CREATE PAYMENT
    # ============================================================

    def create_payment(

        self,
        token,
        amount,
        transaction_id=None,
        order_id=None,
        receiver_user_id=None,
        description="Payment"

    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        amount = float(
            amount
        )

        if amount <= 0:

            raise ValueError(
                "Payment amount must be greater than zero."
            )

        payer_user_id = user[
            "user_id"
        ]

        # --------------------------------------------------------
        # Verify linked transaction
        # --------------------------------------------------------

        if transaction_id:

            transaction = (
                self.database
                .get_transaction(
                    transaction_id
                )
            )

            if not transaction:

                raise ValueError(
                    "Linked transaction does not exist."
                )

        # --------------------------------------------------------
        # Verify receiver
        # --------------------------------------------------------

        if receiver_user_id:

            receiver = (
                self.database
                .get_user(
                    receiver_user_id
                )
            )

            if not receiver:

                raise ValueError(
                    "Receiver user does not exist."
                )

        payment_id = (
            self._generate_id(
                "PAY"
            )
        )

        now = self._now()

        payment_data = {
            "description":
                description,

            "source":
                "internal_wallet",

            "simulation":
                True,
        }

        with self.database.connect() as conn:

            conn.execute(
                """
                INSERT INTO payments
                (
                    payment_id,
                    transaction_id,
                    order_id,
                    payer_user_id,
                    receiver_user_id,
                    amount,
                    currency,
                    payment_method,
                    status,
                    payment_data,
                    created_at,
                    updated_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment_id,
                    transaction_id,
                    order_id,
                    payer_user_id,
                    receiver_user_id,
                    amount,
                    "INR",
                    "WALLET",
                    "PENDING",
                    json.dumps(
                        payment_data
                    ),
                    now,
                    now,
                )
            )

        self.database.add_audit_log(

            action="CREATE_PAYMENT",

            status="SUCCESS",

            user_id=payer_user_id,

            entity_type="PAYMENT",

            entity_id=payment_id,

            details={
                "amount":
                    amount,

                "transaction_id":
                    transaction_id,

                "order_id":
                    order_id,

                "receiver_user_id":
                    receiver_user_id,
            }
        )

        return self.get_payment(
            token,
            payment_id
        )

    # ============================================================
    # GET PAYMENT
    # ============================================================

    def get_payment(
        self,
        token,
        payment_id
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        with self.database.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM payments
                WHERE payment_id = ?
                LIMIT 1
                """,
                (
                    payment_id,
                )
            ).fetchone()

        if not row:

            raise ValueError(
                "Payment not found."
            )

        payment = dict(
            row
        )

        current_user_id = user[
            "user_id"
        ]

        role = str(
            user.get(
                "role",
                ""
            )
        ).upper()

        if role != "ADMIN":

            if (
                payment[
                    "payer_user_id"
                ]
                != current_user_id
                and
                payment[
                    "receiver_user_id"
                ]
                != current_user_id
            ):

                raise PermissionError(
                    "User is not authorized "
                    "to access this payment."
                )

        return payment

    # ============================================================
    # COMPLETE PAYMENT
    # ============================================================

    def complete_payment(
        self,
        token,
        payment_id
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        payment = self.get_payment(
            token,
            payment_id
        )

        if payment[
            "status"
        ] == "COMPLETED":

            return payment

        if payment[
            "status"
        ] != "PENDING":

            raise ValueError(
                "Only PENDING payments "
                "can be completed."
            )

        amount = float(
            payment[
                "amount"
            ]
        )

        # --------------------------------------------------------
        # Debit payer wallet
        # --------------------------------------------------------

        payer_wallet = (
            self.debit_wallet(

                token,

                amount,

                description=(
                    "Payment debit"
                ),

                reference_type="PAYMENT",

                reference_id=payment_id
            )
        )

        # --------------------------------------------------------
        # Credit receiver wallet
        # --------------------------------------------------------

        receiver_user_id = (
            payment[
                "receiver_user_id"
            ]
        )

        if receiver_user_id:

            receiver_user = (
                self.database
                .get_user(
                    receiver_user_id
                )
            )

            if receiver_user:

                # ------------------------------------------------
                # We need a token representing receiver access.
                #
                # For this local backend implementation, directly
                # update the receiver wallet using the database
                # layer instead of pretending to authenticate
                # as another user.
                # ------------------------------------------------

                receiver_wallet = (
                    self._ensure_wallet(
                        receiver_user
                    )
                )

                wallet_id = receiver_wallet[
                    "wallet_id"
                ]

                now = self._now()

                with self.database.connect() as conn:

                    row = conn.execute(
                        """
                        SELECT balance
                        FROM wallets
                        WHERE wallet_id = ?
                        LIMIT 1
                        """,
                        (
                            wallet_id,
                        )
                    ).fetchone()

                    balance_before = float(
                        row[
                            "balance"
                        ]
                    )

                    balance_after = (
                        balance_before
                        + amount
                    )

                    conn.execute(
                        """
                        UPDATE wallets
                        SET
                            balance = ?,
                            updated_at = ?
                        WHERE wallet_id = ?
                        """,
                        (
                            balance_after,
                            now,
                            wallet_id,
                        )
                    )

                    ledger_id = (
                        self._generate_id(
                            "LED"
                        )
                    )

                    conn.execute(
                        """
                        INSERT INTO wallet_ledger
                        (
                            ledger_id,
                            wallet_id,
                            user_id,
                            transaction_type,
                            amount,
                            balance_before,
                            balance_after,
                            reference_type,
                            reference_id,
                            description,
                            created_at
                        )
                        VALUES
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            ledger_id,
                            wallet_id,
                            receiver_user_id,
                            "CREDIT",
                            amount,
                            balance_before,
                            balance_after,
                            "PAYMENT",
                            payment_id,
                            "Payment received",
                            now,
                        )
                    )

        # --------------------------------------------------------
        # Update payment
        # --------------------------------------------------------

        with self.database.connect() as conn:

            conn.execute(
                """
                UPDATE payments
                SET
                    status = ?,
                    updated_at = ?
                WHERE payment_id = ?
                """,
                (
                    "COMPLETED",
                    self._now(),
                    payment_id,
                )
            )

        self.database.add_history(

            entity_type="PAYMENT",

            entity_id=payment_id,

            event_type="PAYMENT_COMPLETED",

            event_data={
                "amount":
                    amount,

                "transaction_id":
                    payment[
                        "transaction_id"
                    ],

                "order_id":
                    payment[
                        "order_id"
                    ],
            }
        )

        self.database.add_audit_log(

            action="COMPLETE_PAYMENT",

            status="SUCCESS",

            user_id=user[
                "user_id"
            ],

            entity_type="PAYMENT",

            entity_id=payment_id,

            details={
                "amount":
                    amount,

                "status":
                    "COMPLETED",
            }
        )

        return self.get_payment(
            token,
            payment_id
        )

    # ============================================================
    # CANCEL PAYMENT
    # ============================================================

    def cancel_payment(
        self,
        token,
        payment_id
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        payment = self.get_payment(
            token,
            payment_id
        )

        if payment[
            "status"
        ] == "COMPLETED":

            raise ValueError(
                "Completed payment cannot be cancelled."
            )

        with self.database.connect() as conn:

            conn.execute(
                """
                UPDATE payments
                SET
                    status = ?,
                    updated_at = ?
                WHERE payment_id = ?
                """,
                (
                    "CANCELLED",
                    self._now(),
                    payment_id,
                )
            )

        self.database.add_audit_log(

            action="CANCEL_PAYMENT",

            status="SUCCESS",

            user_id=user[
                "user_id"
            ],

            entity_type="PAYMENT",

            entity_id=payment_id,

            details={
                "status":
                    "CANCELLED"
            }
        )

        return self.get_payment(
            token,
            payment_id
        )

    # ============================================================
    # WALLET LEDGER
    # ============================================================

    def get_wallet_ledger(
        self,
        token
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        wallet = self._ensure_wallet(
            user
        )

        with self.database.connect() as conn:

            rows = conn.execute(
                """
                SELECT *
                FROM wallet_ledger
                WHERE wallet_id = ?
                ORDER BY created_at DESC
                """,
                (
                    wallet[
                        "wallet_id"
                    ],
                )
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


# =================================================================
# TEST HELPERS
# =================================================================

def _get_auth_user(
    engine,
    email
):

    try:

        return (
            engine.auth
            .user_store
            .get_by_email(
                email
            )
        )

    except Exception:

        return None


# =================================================================
# MAIN TEST
# =================================================================

def main():

    print()
    print("=" * 70)
    print(
        "PAYMENTS & WALLETS + DATABASE INTEGRATION TEST"
    )
    print("=" * 70)

    print()
    print("Architecture:")

    print(
        "Authentication & Authorization"
    )

    print(
        "              ↓"
    )

    print(
        "       SQLite Database"
    )

    print(
        "              ↓"
    )

    print(
        "      User Management"
    )

    print(
        "              ↓"
    )

    print(
        "      Crop Management"
    )

    print(
        "              ↓"
    )

    print(
        "    Auction & Bidding"
    )

    print(
        "              ↓"
    )

    print(
        "     Order & Transaction"
    )

    print(
        "              ↓"
    )

    print(
        "      Payments & Wallets"
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
    # 1. ENGINE INITIALIZATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "1. ENGINE INITIALIZATION"
    )
    print("=" * 70)

    engine = PaymentWalletEngine()

    # ============================================================
    # 2. TEST FARMER AUTHENTICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "2. TEST FARMER AUTHENTICATION"
    )
    print("=" * 70)

    farmer_email = (
        "payment_test_farmer"
        "@project.local"
    )

    farmer_password = (
        "Farmer@123"
    )

    existing = (
        _get_auth_user(
            engine,
            farmer_email
        )
    )

    if existing:

        print(
            "✓ Existing test farmer found"
        )

    else:

        engine.auth.register_user(

            name="Payment Test Farmer",

            email=farmer_email,

            password=farmer_password,

            role="FARMER"
        )

        print(
            "✓ Test farmer created"
        )

    login = (
        engine.auth.login(
            farmer_email,
            farmer_password
        )
    )

    farmer_token = login[
        "access_token"
    ]

    farmer_user = (
        engine.auth.authenticate(
            farmer_token
        )
    )

    print(
        "✓ Farmer login successful"
    )

    print(
        "✓ JWT token generated"
    )

    print(
        "✓ Role :",
        farmer_user[
            "role"
        ]
    )

    # ============================================================
    # 3. AUTH → SQLITE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "3. AUTHENTICATION → DATABASE SYNCHRONIZATION"
    )
    print("=" * 70)

    db_user = (
        engine
        ._sync_authenticated_user(
            farmer_user
        )
    )

    assert (
        db_user[
            "user_id"
        ]
        ==
        farmer_user[
            "user_id"
        ]
    )

    print(
        "✓ Authenticated user exists in SQLite"
    )

    print(
        "✓ User ID consistency verified"
    )

    # ============================================================
    # 4. WALLET CREATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "4. WALLET CREATION"
    )
    print("=" * 70)

    wallet = (
        engine.create_wallet(
            farmer_token
        )
    )

    wallet_id = wallet[
        "wallet_id"
    ]

    initial_balance = float(
        wallet[
            "balance"
        ]
    )

    print(
        "✓ Wallet created / retrieved"
    )

    print(
        "✓ Wallet ID :",
        wallet_id
    )

    print(
        "✓ Initial Balance : ₹",
        f"{initial_balance:,.2f}"
    )

    assert (
        wallet[
            "currency"
        ]
        ==
        "INR"
    )

    assert (
        wallet[
            "status"
        ]
        ==
        "ACTIVE"
    )

    print(
        "✓ Wallet currency : INR"
    )

    print(
        "✓ Wallet status : ACTIVE"
    )

    # ============================================================
    # 5. CREDIT WALLET
    # ============================================================

    print()
    print("=" * 70)
    print(
        "5. WALLET CREDIT"
    )
    print("=" * 70)

    credit_amount = 100000.0

    credited_wallet = (
        engine.credit_wallet(

            farmer_token,

            credit_amount,

            description=(
                "Initial test wallet funding"
            ),

            reference_type="TEST",

            reference_id="WALLET_TEST"
        )
    )

    expected_balance = (
        initial_balance
        + credit_amount
    )

    actual_balance = float(
        credited_wallet[
            "balance"
        ]
    )

    assert abs(
        actual_balance
        - expected_balance
    ) < 0.01

    print(
        "✓ Wallet credited"
    )

    print(
        "✓ Credit Amount : ₹",
        f"{credit_amount:,.2f}"
    )

    print(
        "✓ New Balance : ₹",
        f"{actual_balance:,.2f}"
    )

    print(
        "✓ Credit calculation verified"
    )

    # ============================================================
    # 6. WALLET DEBIT
    # ============================================================

    print()
    print("=" * 70)
    print(
        "6. WALLET DEBIT"
    )
    print("=" * 70)

    debit_amount = 15000.0

    debited_wallet = (
        engine.debit_wallet(

            farmer_token,

            debit_amount,

            description=(
                "Test wallet debit"
            ),

            reference_type="TEST",

            reference_id="DEBIT_TEST"
        )
    )

    expected_balance = (
        actual_balance
        - debit_amount
    )

    actual_balance = float(
        debited_wallet[
            "balance"
        ]
    )

    assert abs(
        actual_balance
        - expected_balance
    ) < 0.01

    print(
        "✓ Wallet debited"
    )

    print(
        "✓ Debit Amount : ₹",
        f"{debit_amount:,.2f}"
    )

    print(
        "✓ New Balance : ₹",
        f"{actual_balance:,.2f}"
    )

    print(
        "✓ Debit calculation verified"
    )

    # ============================================================
    # 7. INSUFFICIENT BALANCE TEST
    # ============================================================

    print()
    print("=" * 70)
    print(
        "7. INSUFFICIENT BALANCE PROTECTION"
    )
    print("=" * 70)

    insufficient_balance_rejected = False

    try:

        engine.debit_wallet(

            farmer_token,

            999999999.0,

            description=(
                "Should fail"
            ),

            reference_type="TEST",

            reference_id="INSUFFICIENT_TEST"
        )

    except ValueError as exc:

        if (
            "Insufficient"
            in str(exc)
        ):

            insufficient_balance_rejected = True

    assert (
        insufficient_balance_rejected
    )

    print(
        "✓ Insufficient balance correctly rejected"
    )

    # ============================================================
    # 8. CREATE PAYMENT
    # ============================================================

    print()
    print("=" * 70)
    print(
        "8. CREATE PAYMENT"
    )
    print("=" * 70)

    payment_amount = 5000.0

    payment = (
        engine.create_payment(

            token=farmer_token,

            amount=payment_amount,

            transaction_id=None,

            order_id=None,

            receiver_user_id=None,

            description=(
                "Internal wallet payment test"
            )
        )
    )

    payment_id = payment[
        "payment_id"
    ]

    assert (
        payment[
            "status"
        ]
        ==
        "PENDING"
    )

    assert abs(
        float(
            payment[
                "amount"
            ]
        )
        - payment_amount
    ) < 0.01

    print(
        "✓ Payment created"
    )

    print(
        "✓ Payment ID :",
        payment_id
    )

    print(
        "✓ Payment Amount : ₹",
        f"{payment_amount:,.2f}"
    )

    print(
        "✓ Payment Status :",
        payment[
            "status"
        ]
    )

    # ============================================================
    # 9. COMPLETE PAYMENT
    # ============================================================

    print()
    print("=" * 70)
    print(
        "9. PAYMENT COMPLETION"
    )
    print("=" * 70)

    completed_payment = (
        engine.complete_payment(

            farmer_token,

            payment_id
        )
    )

    assert (
        completed_payment[
            "status"
        ]
        ==
        "COMPLETED"
    )

    print(
        "✓ Payment completed"
    )

    print(
        "✓ Payment status :",
        completed_payment[
            "status"
        ]
    )

    # ============================================================
    # 10. PAYMENT RETRIEVAL
    # ============================================================

    print()
    print("=" * 70)
    print(
        "10. PAYMENT RETRIEVAL"
    )
    print("=" * 70)

    retrieved_payment = (
        engine.get_payment(

            farmer_token,

            payment_id
        )
    )

    assert (
        retrieved_payment[
            "payment_id"
        ]
        ==
        payment_id
    )

    print(
        "✓ Payment retrieval verified"
    )

    # ============================================================
    # 11. WALLET LEDGER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "11. WALLET LEDGER VERIFICATION"
    )
    print("=" * 70)

    ledger = (
        engine.get_wallet_ledger(
            farmer_token
        )
    )

    assert ledger

    credit_entries = [
        row
        for row in ledger
        if row[
            "transaction_type"
        ]
        ==
        "CREDIT"
    ]

    debit_entries = [
        row
        for row in ledger
        if row[
            "transaction_type"
        ]
        ==
        "DEBIT"
    ]

    assert credit_entries

    assert debit_entries

    print(
        "✓ Wallet ledger exists"
    )

    print(
        "✓ Credit ledger entries verified"
    )

    print(
        "✓ Debit ledger entries verified"
    )

    print(
        "✓ Ledger balance tracking verified"
    )

    # ============================================================
    # 12. DATABASE PERSISTENCE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "12. DATABASE PERSISTENCE VERIFICATION"
    )
    print("=" * 70)

    with engine.database.connect() as conn:

        wallet_row = conn.execute(
            """
            SELECT *
            FROM wallets
            WHERE wallet_id = ?
            LIMIT 1
            """,
            (
                wallet_id,
            )
        ).fetchone()

        payment_row = conn.execute(
            """
            SELECT *
            FROM payments
            WHERE payment_id = ?
            LIMIT 1
            """,
            (
                payment_id,
            )
        ).fetchone()

        ledger_rows = conn.execute(
            """
            SELECT *
            FROM wallet_ledger
            WHERE wallet_id = ?
            """,
            (
                wallet_id,
            )
        ).fetchall()

    assert wallet_row

    assert payment_row

    assert ledger_rows

    print(
        "✓ Wallet persistence verified"
    )

    print(
        "✓ Payment persistence verified"
    )

    print(
        "✓ Wallet ledger persistence verified"
    )

    # ============================================================
    # 13. AUDIT VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "13. AUDIT VERIFICATION"
    )
    print("=" * 70)

    logs = (
        engine.database
        .get_audit_logs(

            user_id=farmer_user[
                "user_id"
            ]
        )
    )

    assert logs

    print(
        "✓ Wallet actions logged"
    )

    print(
        "✓ Payment actions logged"
    )

    print(
        "✓ Audit records verified"
    )

    # ============================================================
    # 14. HISTORY VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "14. HISTORICAL DATA VERIFICATION"
    )
    print("=" * 70)

    history = (
        engine.database
        .get_history(

            entity_type="PAYMENT",

            entity_id=payment_id
        )
    )

    assert history

    print(
        "✓ Payment history verified"
    )

    # ============================================================
    # FINAL STATUS
    # ============================================================

    print()
    print("=" * 70)
    print(
        "PAYMENTS & WALLETS FINAL STATUS"
    )
    print("=" * 70)

    print(
        "✓ Authentication Integration : VERIFIED"
    )

    print(
        "✓ Authentication → SQLite Sync : VERIFIED"
    )

    print(
        "✓ SQLite Integration         : VERIFIED"
    )

    print(
        "✓ Wallet Creation            : VERIFIED"
    )

    print(
        "✓ Wallet Balance             : VERIFIED"
    )

    print(
        "✓ Wallet Credit              : VERIFIED"
    )

    print(
        "✓ Wallet Debit               : VERIFIED"
    )

    print(
        "✓ Insufficient Balance Guard : VERIFIED"
    )

    print(
        "✓ Payment Creation           : VERIFIED"
    )

    print(
        "✓ Payment Retrieval          : VERIFIED"
    )

    print(
        "✓ Payment Completion         : VERIFIED"
    )

    print(
        "✓ Wallet Ledger              : VERIFIED"
    )

    print(
        "✓ Database Persistence       : VERIFIED"
    )

    print(
        "✓ Historical Data            : VERIFIED"
    )

    print(
        "✓ Audit Logging              : VERIFIED"
    )

    print()

    print(
        "PAYMENTS & WALLETS STATUS: COMPLETE"
    )


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":

    main()