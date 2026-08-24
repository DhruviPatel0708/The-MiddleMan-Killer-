"""
SUPPORT & TICKETS
=================

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
            ↓
      Reports & Analytics
            ↓
       Support & Tickets

No external API.
No FastAPI.
No ML model.
No new dataset.
"""

from __future__ import annotations

import sys
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone


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

from authentication import AuthenticationAuthorizationEngine
from database import DatabaseManager


# ================================================================
# SUPPORT & TICKETS ENGINE
# ================================================================

class SupportTicketsEngine:

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):

        print("=" * 70)
        print("SUPPORT & TICKETS ENGINE")
        print("=" * 70)

        self.auth = AuthenticationAuthorizationEngine()

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

        self._ensure_support_tables()

        self._verify_support_tables()

        print(
            "✓ Support & Tickets Engine initialized"
        )

    # ============================================================
    # TIME
    # ============================================================

    @staticmethod
    def _now():

        return datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

    # ============================================================
    # ID GENERATION
    # ============================================================

    @staticmethod
    def _ticket_id():

        return (
            "TKT_"
            + uuid.uuid4()
            .hex[:12]
            .upper()
        )

    @staticmethod
    def _message_id():

        return (
            "MSG_"
            + uuid.uuid4()
            .hex[:12]
            .upper()
        )

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    def _authenticate(
        self,
        token
    ):

        user = self.auth.authenticate(
            token
        )

        if not user:

            raise PermissionError(
                "Invalid authentication token."
            )

        return user

    # ============================================================
    # USER DATABASE SYNCHRONIZATION
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
            user.get("name")
            or "Support User"
        )

        email = (
            user.get("email")
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
    # SUPPORT TABLES
    # ============================================================

    def _ensure_support_tables(self):

        with self.database.connect() as conn:

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS support_tickets (

                    ticket_id TEXT PRIMARY KEY,

                    user_id TEXT NOT NULL,

                    category TEXT NOT NULL,

                    subject TEXT NOT NULL,

                    description TEXT NOT NULL,

                    priority TEXT NOT NULL
                        DEFAULT 'MEDIUM',

                    status TEXT NOT NULL
                        DEFAULT 'OPEN',

                    assigned_to TEXT,

                    resolution TEXT,

                    created_at TEXT NOT NULL,

                    updated_at TEXT NOT NULL,

                    FOREIGN KEY (
                        user_id
                    )
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS support_messages (

                    message_id TEXT PRIMARY KEY,

                    ticket_id TEXT NOT NULL,

                    sender_id TEXT NOT NULL,

                    message TEXT NOT NULL,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY (
                        ticket_id
                    )
                    REFERENCES support_tickets(ticket_id)
                    ON DELETE CASCADE,

                    FOREIGN KEY (
                        sender_id
                    )
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
                )
                """
            )

            conn.commit()

    # ============================================================
    # VERIFY TABLES
    # ============================================================

    def _verify_support_tables(self):

        with self.database.connect() as conn:

            tables = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name IN (
                    'support_tickets',
                    'support_messages'
                )
                """
            ).fetchall()

        existing = {
            row["name"]
            for row in tables
        }

        if "support_tickets" in existing:

            print(
                "✓ Support tickets table verified"
            )

        else:

            raise RuntimeError(
                "support_tickets table not available."
            )

        if "support_messages" in existing:

            print(
                "✓ Support messages table verified"
            )

        else:

            raise RuntimeError(
                "support_messages table not available."
            )

    # ============================================================
    # CREATE TICKET
    # ============================================================

    def create_ticket(

        self,

        token,

        category,

        subject,

        description,

        priority="MEDIUM"

    ):

        user = self._authenticate(
            token
        )

        db_user = (
            self._sync_authenticated_user(
                user
            )
        )

        priority = str(
            priority
        ).upper()

        allowed_priorities = {
            "LOW",
            "MEDIUM",
            "HIGH",
            "URGENT"
        }

        if priority not in allowed_priorities:

            raise ValueError(
                "Invalid ticket priority."
            )

        ticket_id = self._ticket_id()

        now = self._now()

        with self.database.connect() as conn:

            conn.execute(
                """
                INSERT INTO support_tickets
                (
                    ticket_id,
                    user_id,
                    category,
                    subject,
                    description,
                    priority,
                    status,
                    assigned_to,
                    resolution,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket_id,

                    db_user["user_id"],

                    category,

                    subject,

                    description,

                    priority,

                    "OPEN",

                    None,

                    None,

                    now,

                    now
                )
            )

            conn.commit()

        return self.get_ticket(
            token,
            ticket_id
        )

    # ============================================================
    # GET TICKET
    # ============================================================

    def get_ticket(

        self,

        token,

        ticket_id

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
                FROM support_tickets
                WHERE ticket_id = ?
                """,
                (
                    ticket_id,
                )
            ).fetchone()

        if not row:

            raise ValueError(
                "Support ticket not found."
            )

        return dict(row)

    # ============================================================
    # LIST USER TICKETS
    # ============================================================

    def list_user_tickets(
        self,
        token
    ):

        user = self._authenticate(
            token
        )

        db_user = (
            self._sync_authenticated_user(
                user
            )
        )

        with self.database.connect() as conn:

            rows = conn.execute(
                """
                SELECT *
                FROM support_tickets
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (
                    db_user["user_id"],
                )
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ============================================================
    # UPDATE TICKET
    # ============================================================

    def update_ticket(

        self,

        token,

        ticket_id,

        status=None,

        priority=None,

        assigned_to=None,

        resolution=None

    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        with self.database.connect() as conn:

            existing = conn.execute(
                """
                SELECT *
                FROM support_tickets
                WHERE ticket_id = ?
                """,
                (
                    ticket_id,
                )
            ).fetchone()

            if not existing:

                raise ValueError(
                    "Support ticket not found."
                )

            current = dict(existing)

            new_status = (
                str(status).upper()
                if status is not None
                else current["status"]
            )

            new_priority = (
                str(priority).upper()
                if priority is not None
                else current["priority"]
            )

            allowed_statuses = {
                "OPEN",
                "IN_PROGRESS",
                "RESOLVED",
                "CLOSED",
                "CANCELLED"
            }

            allowed_priorities = {
                "LOW",
                "MEDIUM",
                "HIGH",
                "URGENT"
            }

            if new_status not in allowed_statuses:

                raise ValueError(
                    "Invalid ticket status."
                )

            if new_priority not in allowed_priorities:

                raise ValueError(
                    "Invalid ticket priority."
                )

            new_assigned_to = (
                assigned_to
                if assigned_to is not None
                else current["assigned_to"]
            )

            new_resolution = (
                resolution
                if resolution is not None
                else current["resolution"]
            )

            conn.execute(
                """
                UPDATE support_tickets

                SET
                    status = ?,
                    priority = ?,
                    assigned_to = ?,
                    resolution = ?,
                    updated_at = ?

                WHERE ticket_id = ?
                """,
                (
                    new_status,

                    new_priority,

                    new_assigned_to,

                    new_resolution,

                    self._now(),

                    ticket_id
                )
            )

            conn.commit()

        return self.get_ticket(
            token,
            ticket_id
        )

    # ============================================================
    # ADD MESSAGE
    # ============================================================

    def add_message(

        self,

        token,

        ticket_id,

        message

    ):

        user = self._authenticate(
            token
        )

        db_user = (
            self._sync_authenticated_user(
                user
            )
        )

        if not message or not str(
            message
        ).strip():

            raise ValueError(
                "Message cannot be empty."
            )

        with self.database.connect() as conn:

            ticket = conn.execute(
                """
                SELECT ticket_id
                FROM support_tickets
                WHERE ticket_id = ?
                """,
                (
                    ticket_id,
                )
            ).fetchone()

            if not ticket:

                raise ValueError(
                    "Support ticket not found."
                )

            message_id = (
                self._message_id()
            )

            now = self._now()

            conn.execute(
                """
                INSERT INTO support_messages
                (
                    message_id,
                    ticket_id,
                    sender_id,
                    message,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    message_id,

                    ticket_id,

                    db_user["user_id"],

                    str(message).strip(),

                    now
                )
            )

            conn.execute(
                """
                UPDATE support_tickets
                SET updated_at = ?
                WHERE ticket_id = ?
                """,
                (
                    now,
                    ticket_id
                )
            )

            conn.commit()

        return self.get_message(
            token,
            message_id
        )

    # ============================================================
    # GET MESSAGE
    # ============================================================

    def get_message(

        self,

        token,

        message_id

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
                FROM support_messages
                WHERE message_id = ?
                """,
                (
                    message_id,
                )
            ).fetchone()

        if not row:

            raise ValueError(
                "Support message not found."
            )

        return dict(row)

    # ============================================================
    # LIST TICKET MESSAGES
    # ============================================================

    def list_messages(

        self,

        token,

        ticket_id

    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        with self.database.connect() as conn:

            ticket = conn.execute(
                """
                SELECT ticket_id
                FROM support_tickets
                WHERE ticket_id = ?
                """,
                (
                    ticket_id,
                )
            ).fetchone()

            if not ticket:

                raise ValueError(
                    "Support ticket not found."
                )

            rows = conn.execute(
                """
                SELECT *
                FROM support_messages
                WHERE ticket_id = ?
                ORDER BY created_at ASC
                """,
                (
                    ticket_id,
                )
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ============================================================
    # CLOSE TICKET
    # ============================================================

    def close_ticket(

        self,

        token,

        ticket_id,

        resolution

    ):

        if not resolution or not str(
            resolution
        ).strip():

            raise ValueError(
                "Resolution is required to close a ticket."
            )

        return self.update_ticket(

            token,

            ticket_id,

            status="CLOSED",

            resolution=str(
                resolution
            ).strip()
        )

    # ============================================================
    # SUPPORT SUMMARY
    # ============================================================

    def support_summary(
        self,
        token
    ):

        user = self._authenticate(
            token
        )

        self._sync_authenticated_user(
            user
        )

        with self.database.connect() as conn:

            total_tickets = conn.execute(
                """
                SELECT COUNT(*)
                FROM support_tickets
                """
            ).fetchone()[0]

            status_rows = conn.execute(
                """
                SELECT
                    status,
                    COUNT(*) AS total
                FROM support_tickets
                GROUP BY status
                """
            ).fetchall()

            priority_rows = conn.execute(
                """
                SELECT
                    priority,
                    COUNT(*) AS total
                FROM support_tickets
                GROUP BY priority
                """
            ).fetchall()

            category_rows = conn.execute(
                """
                SELECT
                    category,
                    COUNT(*) AS total
                FROM support_tickets
                GROUP BY category
                """
            ).fetchall()

            total_messages = conn.execute(
                """
                SELECT COUNT(*)
                FROM support_messages
                """
            ).fetchone()[0]

        tickets_by_status = {
            row["status"]:
                row["total"]
            for row in status_rows
        }

        tickets_by_priority = {
            row["priority"]:
                row["total"]
            for row in priority_rows
        }

        tickets_by_category = {
            row["category"]:
                row["total"]
            for row in category_rows
        }

        return {

            "total_tickets":
                total_tickets,

            "tickets_by_status":
                tickets_by_status,

            "tickets_by_priority":
                tickets_by_priority,

            "tickets_by_category":
                tickets_by_category,

            "total_messages":
                total_messages,
        }


# =================================================================
# TEST HELPER
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
        "SUPPORT & TICKETS + DATABASE INTEGRATION TEST"
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
    print(
        "              ↓"
    )
    print(
        "      Reports & Analytics"
    )
    print(
        "              ↓"
    )
    print(
        "       Support & Tickets"
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

    engine = SupportTicketsEngine()

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
        "support_test_farmer"
        "@project.local"
    )

    farmer_password = (
        "Farmer@123"
    )

    existing = _get_auth_user(
        engine,
        farmer_email
    )

    if existing:

        print(
            "✓ Existing test farmer found"
        )

    else:

        engine.auth.register_user(

            name="Support Test Farmer",

            email=farmer_email,

            password=farmer_password,

            role="FARMER"
        )

        print(
            "✓ Test farmer created"
        )

    login = engine.auth.login(
        farmer_email,
        farmer_password
    )

    token = login[
        "access_token"
    ]

    user = engine.auth.authenticate(
        token
    )

    print(
        "✓ Farmer login successful"
    )

    print(
        "✓ JWT token generated"
    )

    print(
        "✓ Role :",
        user["role"]
    )

    # ============================================================
    # 3. DATABASE SYNCHRONIZATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "3. AUTHENTICATION → DATABASE SYNCHRONIZATION"
    )
    print("=" * 70)

    db_user = (
        engine._sync_authenticated_user(
            user
        )
    )

    assert (
        db_user["user_id"]
        ==
        user["user_id"]
    )

    print(
        "✓ Authenticated user exists in SQLite"
    )

    print(
        "✓ User ID consistency verified"
    )

    # ============================================================
    # 4. CREATE TICKET
    # ============================================================

    print()
    print("=" * 70)
    print(
        "4. CREATE SUPPORT TICKET"
    )
    print("=" * 70)

    ticket = engine.create_ticket(

        token=token,

        category="CROP",

        subject="Crop management support",

        description=(
            "Test support request for crop management."
        ),

        priority="HIGH"
    )

    ticket_id = ticket[
        "ticket_id"
    ]

    assert ticket_id.startswith(
        "TKT_"
    )

    assert ticket[
        "status"
    ] == "OPEN"

    print(
        "✓ Support ticket created"
    )

    print(
        "✓ Ticket ID :",
        ticket_id
    )

    print(
        "✓ Category :",
        ticket["category"]
    )

    print(
        "✓ Priority :",
        ticket["priority"]
    )

    print(
        "✓ Status :",
        ticket["status"]
    )

    # ============================================================
    # 5. GET TICKET
    # ============================================================

    print()
    print("=" * 70)
    print(
        "5. GET TICKET"
    )
    print("=" * 70)

    retrieved = engine.get_ticket(
        token,
        ticket_id
    )

    assert (
        retrieved["ticket_id"]
        ==
        ticket_id
    )

    print(
        "✓ Ticket retrieval verified"
    )

    # ============================================================
    # 6. ADD MESSAGE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "6. ADD SUPPORT MESSAGE"
    )
    print("=" * 70)

    message = engine.add_message(

        token=token,

        ticket_id=ticket_id,

        message=(
            "Please review the crop issue."
        )
    )

    message_id = message[
        "message_id"
    ]

    assert message_id.startswith(
        "MSG_"
    )

    print(
        "✓ Support message created"
    )

    print(
        "✓ Message ID :",
        message_id
    )

    # ============================================================
    # 7. MESSAGE RETRIEVAL
    # ============================================================

    print()
    print("=" * 70)
    print(
        "7. MESSAGE RETRIEVAL"
    )
    print("=" * 70)

    retrieved_message = (
        engine.get_message(
            token,
            message_id
        )
    )

    assert (
        retrieved_message[
            "message_id"
        ]
        ==
        message_id
    )

    print(
        "✓ Message retrieval verified"
    )

    # ============================================================
    # 8. LIST TICKET MESSAGES
    # ============================================================

    print()
    print("=" * 70)
    print(
        "8. TICKET MESSAGE LIST"
    )
    print("=" * 70)

    messages = engine.list_messages(

        token,

        ticket_id
    )

    assert len(messages) >= 1

    print(
        "✓ Ticket messages retrieved"
    )

    print(
        "✓ Total Messages :",
        len(messages)
    )

    # ============================================================
    # 9. LIST USER TICKETS
    # ============================================================

    print()
    print("=" * 70)
    print(
        "9. USER TICKET LIST"
    )
    print("=" * 70)

    tickets = engine.list_user_tickets(
        token
    )

    assert len(tickets) >= 1

    found = any(
        item["ticket_id"]
        == ticket_id
        for item in tickets
    )

    assert found

    print(
        "✓ User ticket list retrieved"
    )

    print(
        "✓ Created ticket found"
    )

    print(
        "✓ Total User Tickets :",
        len(tickets)
    )

    # ============================================================
    # 10. UPDATE TICKET
    # ============================================================

    print()
    print("=" * 70)
    print(
        "10. UPDATE TICKET"
    )
    print("=" * 70)

    updated = engine.update_ticket(

        token=token,

        ticket_id=ticket_id,

        status="IN_PROGRESS",

        priority="URGENT"
    )

    assert (
        updated["status"]
        ==
        "IN_PROGRESS"
    )

    assert (
        updated["priority"]
        ==
        "URGENT"
    )

    print(
        "✓ Ticket status updated"
    )

    print(
        "✓ Status :",
        updated["status"]
    )

    print(
        "✓ Priority :",
        updated["priority"]
    )

    # ============================================================
    # 11. CLOSE TICKET
    # ============================================================

    print()
    print("=" * 70)
    print(
        "11. CLOSE TICKET"
    )
    print("=" * 70)

    closed = engine.close_ticket(

        token=token,

        ticket_id=ticket_id,

        resolution=(
            "Crop support request resolved successfully."
        )
    )

    assert (
        closed["status"]
        ==
        "CLOSED"
    )

    assert closed[
        "resolution"
    ]

    print(
        "✓ Ticket closed"
    )

    print(
        "✓ Ticket status :",
        closed["status"]
    )

    print(
        "✓ Resolution stored"
    )

    # ============================================================
    # 12. SUPPORT SUMMARY
    # ============================================================

    print()
    print("=" * 70)
    print(
        "12. SUPPORT SUMMARY"
    )
    print("=" * 70)

    summary = engine.support_summary(
        token
    )

    assert (
        summary["total_tickets"]
        >= 1
    )

    assert (
        summary["total_messages"]
        >= 1
    )

    print(
        "✓ Total Tickets :",
        summary["total_tickets"]
    )

    print(
        "✓ Tickets by Status :",
        summary["tickets_by_status"]
    )

    print(
        "✓ Tickets by Priority :",
        summary["tickets_by_priority"]
    )

    print(
        "✓ Tickets by Category :",
        summary["tickets_by_category"]
    )

    print(
        "✓ Total Messages :",
        summary["total_messages"]
    )

    print(
        "✓ Support summary verified"
    )

    # ============================================================
    # 13. DATABASE PERSISTENCE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "13. DATABASE PERSISTENCE VERIFICATION"
    )
    print("=" * 70)

    with engine.database.connect() as conn:

        stored_ticket = conn.execute(
            """
            SELECT *
            FROM support_tickets
            WHERE ticket_id = ?
            """,
            (
                ticket_id,
            )
        ).fetchone()

        stored_message = conn.execute(
            """
            SELECT *
            FROM support_messages
            WHERE message_id = ?
            """,
            (
                message_id,
            )
        ).fetchone()

    assert stored_ticket is not None

    assert stored_message is not None

    print(
        "✓ Support ticket persistence verified"
    )

    print(
        "✓ Support message persistence verified"
    )

    print(
        "✓ Ticket status persistence verified"
    )

    print(
        "✓ Ticket resolution persistence verified"
    )

    # ============================================================
    # 14. FOREIGN KEY VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "14. FOREIGN KEY VERIFICATION"
    )
    print("=" * 70)

    with engine.database.connect() as conn:

        foreign_keys = conn.execute(
            """
            PRAGMA foreign_key_check
            """
        ).fetchall()

    assert len(
        foreign_keys
    ) == 0

    print(
        "✓ Support ticket foreign-key integrity verified"
    )

    print(
        "✓ Support message foreign-key integrity verified"
    )

    # ============================================================
    # 15. FINAL DATABASE VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "15. FINAL DATABASE VERIFICATION"
    )
    print("=" * 70)

    with engine.database.connect() as conn:

        ticket_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM support_tickets
            """
        ).fetchone()[0]

        message_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM support_messages
            """
        ).fetchone()[0]

    assert ticket_count >= 1

    assert message_count >= 1

    print(
        "✓ Support tickets table persistence verified"
    )

    print(
        "✓ Support messages table persistence verified"
    )

    print(
        "✓ Database persistence verified"
    )

    # ============================================================
    # FINAL STATUS
    # ============================================================

    print()
    print("=" * 70)
    print(
        "SUPPORT & TICKETS FINAL STATUS"
    )
    print("=" * 70)

    print(
        "✓ Authentication Integration : VERIFIED"
    )

    print(
        "✓ SQLite Integration         : VERIFIED"
    )

    print(
        "✓ User Synchronization       : VERIFIED"
    )

    print(
        "✓ Ticket Creation            : VERIFIED"
    )

    print(
        "✓ Ticket Retrieval           : VERIFIED"
    )

    print(
        "✓ Ticket Update              : VERIFIED"
    )

    print(
        "✓ Ticket Status Management   : VERIFIED"
    )

    print(
        "✓ Ticket Priority Management : VERIFIED"
    )

    print(
        "✓ Ticket Messaging           : VERIFIED"
    )

    print(
        "✓ Ticket Listing             : VERIFIED"
    )

    print(
        "✓ Ticket Resolution          : VERIFIED"
    )

    print(
        "✓ Support Summary             : VERIFIED"
    )

    print(
        "✓ Database Persistence       : VERIFIED"
    )

    print(
        "✓ Foreign Key Integrity      : VERIFIED"
    )

    print()

    print(
        "SUPPORT & TICKETS STATUS: COMPLETE"
    )


# =================================================================
# ENTRY POINT
# =================================================================

if __name__ == "__main__":

    main()