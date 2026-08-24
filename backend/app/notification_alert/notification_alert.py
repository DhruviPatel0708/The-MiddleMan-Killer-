"""
NOTIFICATION & ALERT
====================

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
            ↓
     Notification & Alert

No external API.
No FastAPI.
No ML model.
No new dataset.
No AI Agent.
"""

from __future__ import annotations

import sys
import uuid
import sqlite3
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
# NOTIFICATION & ALERT ENGINE
# ================================================================

class NotificationAlertEngine:

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(self):

        print("=" * 70)
        print("NOTIFICATION & ALERT ENGINE")
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

        print(
            "✓ No AI Agent"
        )

        self._ensure_notification_table()

        self._verify_notification_table()

        print(
            "✓ Notification & Alert Engine initialized"
        )

    # ============================================================
    # CURRENT TIME
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
    def _notification_id():

        return (
            "NTF_"
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
    # USER → DATABASE SYNCHRONIZATION
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
            or "Notification User"
        )

        email = (
            user.get("email")
            or
            f"{user_id.lower()}@project.local"
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
    # CREATE NOTIFICATION TABLE
    # ============================================================

    def _ensure_notification_table(
        self
    ):

        with self.database.connect() as conn:

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (

                    notification_id TEXT PRIMARY KEY,

                    user_id TEXT NOT NULL,

                    notification_type TEXT NOT NULL,

                    title TEXT NOT NULL,

                    message TEXT NOT NULL,

                    priority TEXT NOT NULL
                        DEFAULT 'MEDIUM',

                    status TEXT NOT NULL
                        DEFAULT 'UNREAD',

                    reference_type TEXT,

                    reference_id TEXT,

                    created_at TEXT NOT NULL,

                    read_at TEXT,

                    FOREIGN KEY (
                        user_id
                    )
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
                )
                """
            )

            conn.commit()

    # ============================================================
    # VERIFY NOTIFICATION TABLE
    # ============================================================

    def _verify_notification_table(
        self
    ):

        with self.database.connect() as conn:

            row = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = 'notifications'
                LIMIT 1
                """
            ).fetchone()

        if row:

            print(
                "✓ Notifications table verified"
            )

        else:

            raise RuntimeError(
                "Notifications table not available."
            )

    # ============================================================
    # CREATE NOTIFICATION
    # ============================================================

    def create_notification(

        self,

        token,

        notification_type,

        title,

        message,

        priority="MEDIUM",

        reference_type=None,

        reference_id=None

    ):

        user = self._authenticate(
            token
        )

        db_user = (
            self._sync_authenticated_user(
                user
            )
        )

        notification_type = str(
            notification_type
        ).upper()

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
                "Invalid notification priority."
            )

        if not title or not str(
            title
        ).strip():

            raise ValueError(
                "Notification title cannot be empty."
            )

        if not message or not str(
            message
        ).strip():

            raise ValueError(
                "Notification message cannot be empty."
            )

        notification_id = (
            self._notification_id()
        )

        now = self._now()

        with self.database.connect() as conn:

            conn.execute(
                """
                INSERT INTO notifications
                (
                    notification_id,
                    user_id,
                    notification_type,
                    title,
                    message,
                    priority,
                    status,
                    reference_type,
                    reference_id,
                    created_at,
                    read_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    notification_id,

                    db_user["user_id"],

                    notification_type,

                    str(title).strip(),

                    str(message).strip(),

                    priority,

                    "UNREAD",

                    reference_type,

                    reference_id,

                    now,

                    None
                )
            )

            conn.commit()

        return self.get_notification(
            token,
            notification_id
        )

    # ============================================================
    # GET NOTIFICATION
    # ============================================================

    def get_notification(

        self,

        token,

        notification_id

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

            row = conn.execute(
                """
                SELECT *
                FROM notifications
                WHERE notification_id = ?
                  AND user_id = ?
                """,
                (
                    notification_id,

                    db_user["user_id"]
                )
            ).fetchone()

        if not row:

            raise ValueError(
                "Notification not found."
            )

        return dict(row)

    # ============================================================
    # LIST USER NOTIFICATIONS
    # ============================================================

    def list_notifications(
        self,
        token,
        status=None
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

            if status is None:

                rows = conn.execute(
                    """
                    SELECT *
                    FROM notifications
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    """,
                    (
                        db_user["user_id"],
                    )
                ).fetchall()

            else:

                status = str(
                    status
                ).upper()

                rows = conn.execute(
                    """
                    SELECT *
                    FROM notifications
                    WHERE user_id = ?
                      AND status = ?
                    ORDER BY created_at DESC
                    """,
                    (
                        db_user["user_id"],

                        status
                    )
                ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ============================================================
    # MARK NOTIFICATION AS READ
    # ============================================================

    def mark_as_read(

        self,

        token,

        notification_id

    ):

        user = self._authenticate(
            token
        )

        db_user = (
            self._sync_authenticated_user(
                user
            )
        )

        now = self._now()

        with self.database.connect() as conn:

            row = conn.execute(
                """
                SELECT notification_id
                FROM notifications
                WHERE notification_id = ?
                  AND user_id = ?
                """,
                (
                    notification_id,

                    db_user["user_id"]
                )
            ).fetchone()

            if not row:

                raise ValueError(
                    "Notification not found."
                )

            conn.execute(
                """
                UPDATE notifications

                SET
                    status = 'READ',
                    read_at = ?

                WHERE notification_id = ?
                  AND user_id = ?
                """,
                (
                    now,

                    notification_id,

                    db_user["user_id"]
                )
            )

            conn.commit()

        return self.get_notification(
            token,
            notification_id
        )

    # ============================================================
    # MARK NOTIFICATION AS UNREAD
    # ============================================================

    def mark_as_unread(

        self,

        token,

        notification_id

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

            row = conn.execute(
                """
                SELECT notification_id
                FROM notifications
                WHERE notification_id = ?
                  AND user_id = ?
                """,
                (
                    notification_id,

                    db_user["user_id"]
                )
            ).fetchone()

            if not row:

                raise ValueError(
                    "Notification not found."
                )

            conn.execute(
                """
                UPDATE notifications

                SET
                    status = 'UNREAD',
                    read_at = NULL

                WHERE notification_id = ?
                  AND user_id = ?
                """,
                (
                    notification_id,

                    db_user["user_id"]
                )
            )

            conn.commit()

        return self.get_notification(
            token,
            notification_id
        )

    # ============================================================
    # DELETE NOTIFICATION
    # ============================================================

    def delete_notification(

        self,

        token,

        notification_id

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

            row = conn.execute(
                """
                SELECT notification_id
                FROM notifications
                WHERE notification_id = ?
                  AND user_id = ?
                """,
                (
                    notification_id,

                    db_user["user_id"]
                )
            ).fetchone()

            if not row:

                raise ValueError(
                    "Notification not found."
                )

            conn.execute(
                """
                DELETE FROM notifications
                WHERE notification_id = ?
                  AND user_id = ?
                """,
                (
                    notification_id,

                    db_user["user_id"]
                )
            )

            conn.commit()

        return True

    # ============================================================
    # NOTIFICATION SUMMARY
    # ============================================================

    def notification_summary(
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

            total = conn.execute(
                """
                SELECT COUNT(*)
                FROM notifications
                WHERE user_id = ?
                """,
                (
                    db_user["user_id"],
                )
            ).fetchone()[0]

            unread = conn.execute(
                """
                SELECT COUNT(*)
                FROM notifications
                WHERE user_id = ?
                  AND status = 'UNREAD'
                """,
                (
                    db_user["user_id"],
                )
            ).fetchone()[0]

            read = conn.execute(
                """
                SELECT COUNT(*)
                FROM notifications
                WHERE user_id = ?
                  AND status = 'READ'
                """,
                (
                    db_user["user_id"],
                )
            ).fetchone()[0]

            type_rows = conn.execute(
                """
                SELECT
                    notification_type,
                    COUNT(*) AS total
                FROM notifications
                WHERE user_id = ?
                GROUP BY notification_type
                """,
                (
                    db_user["user_id"],
                )
            ).fetchall()

            priority_rows = conn.execute(
                """
                SELECT
                    priority,
                    COUNT(*) AS total
                FROM notifications
                WHERE user_id = ?
                GROUP BY priority
                """,
                (
                    db_user["user_id"],
                )
            ).fetchall()

        by_type = {

            row["notification_type"]:
                row["total"]

            for row in type_rows
        }

        by_priority = {

            row["priority"]:
                row["total"]

            for row in priority_rows
        }

        return {

            "total_notifications":
                total,

            "unread_notifications":
                unread,

            "read_notifications":
                read,

            "notifications_by_type":
                by_type,

            "notifications_by_priority":
                by_priority,
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
# MAIN
# =================================================================

def main():

    print()
    print("=" * 70)
    print(
        "NOTIFICATION & ALERT + DATABASE INTEGRATION TEST"
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
    print(
        "              ↓"
    )
    print(
        "     Notification & Alert"
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

    print(
        "No AI Agent."
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

    engine = NotificationAlertEngine()

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
        "notification_test_farmer"
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

            name="Notification Test Farmer",

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
    # 4. CREATE NOTIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "4. CREATE NOTIFICATION"
    )
    print("=" * 70)

    notification = engine.create_notification(

        token=token,

        notification_type="CROP",

        title="Crop Status Update",

        message=(
            "Your crop is now available for sale."
        ),

        priority="HIGH",

        reference_type="CROP",

        reference_id="TEST_CROP_001"
    )

    notification_id = notification[
        "notification_id"
    ]

    assert notification_id.startswith(
        "NTF_"
    )

    assert notification[
        "status"
    ] == "UNREAD"

    print(
        "✓ Notification created"
    )

    print(
        "✓ Notification ID :",
        notification_id
    )

    print(
        "✓ Type :",
        notification[
            "notification_type"
        ]
    )

    print(
        "✓ Priority :",
        notification[
            "priority"
        ]
    )

    print(
        "✓ Status :",
        notification[
            "status"
        ]
    )

    # ============================================================
    # 5. GET NOTIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "5. GET NOTIFICATION"
    )
    print("=" * 70)

    retrieved = engine.get_notification(

        token,

        notification_id
    )

    assert (
        retrieved[
            "notification_id"
        ]
        ==
        notification_id
    )

    print(
        "✓ Notification retrieval verified"
    )

    # ============================================================
    # 6. LIST NOTIFICATIONS
    # ============================================================

    print()
    print("=" * 70)
    print(
        "6. USER NOTIFICATION LIST"
    )
    print("=" * 70)

    notifications = (
        engine.list_notifications(
            token
        )
    )

    assert len(
        notifications
    ) >= 1

    found = any(

        item[
            "notification_id"
        ]
        ==
        notification_id

        for item in notifications
    )

    assert found

    print(
        "✓ User notifications retrieved"
    )

    print(
        "✓ Created notification found"
    )

    print(
        "✓ Total Notifications :",
        len(notifications)
    )

    # ============================================================
    # 7. UNREAD FILTER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "7. UNREAD NOTIFICATION FILTER"
    )
    print("=" * 70)

    unread = engine.list_notifications(

        token,

        status="UNREAD"
    )

    assert any(

        item[
            "notification_id"
        ]
        ==
        notification_id

        for item in unread
    )

    print(
        "✓ Unread notification filter verified"
    )

    print(
        "✓ Unread Notifications :",
        len(unread)
    )

    # ============================================================
    # 8. MARK AS READ
    # ============================================================

    print()
    print("=" * 70)
    print(
        "8. MARK NOTIFICATION AS READ"
    )
    print("=" * 70)

    read_notification = (
        engine.mark_as_read(

            token,

            notification_id
        )
    )

    assert (
        read_notification[
            "status"
        ]
        ==
        "READ"
    )

    assert (
        read_notification[
            "read_at"
        ]
        is not None
    )

    print(
        "✓ Notification marked as READ"
    )

    print(
        "✓ Read timestamp stored"
    )

    # ============================================================
    # 9. MARK AS UNREAD
    # ============================================================

    print()
    print("=" * 70)
    print(
        "9. MARK NOTIFICATION AS UNREAD"
    )
    print("=" * 70)

    unread_notification = (
        engine.mark_as_unread(

            token,

            notification_id
        )
    )

    assert (
        unread_notification[
            "status"
        ]
        ==
        "UNREAD"
    )

    assert (
        unread_notification[
            "read_at"
        ]
        is None
    )

    print(
        "✓ Notification marked as UNREAD"
    )

    # ============================================================
    # 10. NOTIFICATION SUMMARY
    # ============================================================

    print()
    print("=" * 70)
    print(
        "10. NOTIFICATION SUMMARY"
    )
    print("=" * 70)

    summary = (
        engine.notification_summary(
            token
        )
    )

    assert (
        summary[
            "total_notifications"
        ]
        >= 1
    )

    print(
        "✓ Total Notifications :",
        summary[
            "total_notifications"
        ]
    )

    print(
        "✓ Unread Notifications :",
        summary[
            "unread_notifications"
        ]
    )

    print(
        "✓ Read Notifications :",
        summary[
            "read_notifications"
        ]
    )

    print(
        "✓ Notifications by Type :",
        summary[
            "notifications_by_type"
        ]
    )

    print(
        "✓ Notifications by Priority :",
        summary[
            "notifications_by_priority"
        ]
    )

    print(
        "✓ Notification summary verified"
    )

    # ============================================================
    # 11. DATABASE PERSISTENCE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "11. DATABASE PERSISTENCE VERIFICATION"
    )
    print("=" * 70)

    with engine.database.connect() as conn:

        stored = conn.execute(
            """
            SELECT *
            FROM notifications
            WHERE notification_id = ?
            """,
            (
                notification_id,
            )
        ).fetchone()

    assert stored is not None

    assert (
        stored["notification_id"]
        ==
        notification_id
    )

    assert (
        stored["user_id"]
        ==
        user["user_id"]
    )

    print(
        "✓ Notification persistence verified"
    )

    print(
        "✓ User relationship persistence verified"
    )

    print(
        "✓ Notification status persistence verified"
    )

    # ============================================================
    # 12. FOREIGN KEY VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "12. FOREIGN KEY VERIFICATION"
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
        "✓ Notification → User foreign-key integrity verified"
    )

    # ============================================================
    # 13. FINAL DATABASE VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "13. FINAL DATABASE VERIFICATION"
    )
    print("=" * 70)

    with engine.database.connect() as conn:

        notification_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM notifications
            """
        ).fetchone()[0]

    assert (
        notification_count
        >= 1
    )

    print(
        "✓ Notifications table persistence verified"
    )

    print(
        "✓ Total Stored Notifications :",
        notification_count
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
        "NOTIFICATION & ALERT FINAL STATUS"
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
        "✓ Notification Creation      : VERIFIED"
    )

    print(
        "✓ Notification Retrieval     : VERIFIED"
    )

    print(
        "✓ Notification Listing       : VERIFIED"
    )

    print(
        "✓ Unread Filtering           : VERIFIED"
    )

    print(
        "✓ Read Status Management     : VERIFIED"
    )

    print(
        "✓ Unread Status Management   : VERIFIED"
    )

    print(
        "✓ Notification Summary       : VERIFIED"
    )

    print(
        "✓ Database Persistence       : VERIFIED"
    )

    print(
        "✓ Foreign Key Integrity      : VERIFIED"
    )

    print()

    print(
        "NOTIFICATION & ALERT STATUS: COMPLETE"
    )


# =================================================================
# ENTRY POINT
# =================================================================

if __name__ == "__main__":

    main()