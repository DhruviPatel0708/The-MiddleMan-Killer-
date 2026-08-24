"""
COMMUNICATION & INTEGRATION MODULE

Backend-only module.

ONLY THESE COMPONENTS ARE INCLUDED:

1. Message Queue
2. Third-Party Service
3. Email / SMS / Push Notification

No frontend.
No FastAPI.
No external API.
No ML model.
No new dataset.
No REST API Integration.

SQLite is used for persistence and verification.
Third-party services are represented through a safe backend
integration abstraction and mock provider so the module can be
tested without requiring external credentials or network access.
"""

from __future__ import annotations

import json
import sqlite3
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ======================================================================
# PATH CONFIGURATION
# ======================================================================

CURRENT_FILE = Path(__file__).resolve()

# D:\PythonProject3\backend\app\communication_integration\
# parents[3] -> D:\PythonProject3
PROJECT_ROOT = CURRENT_FILE.parents[3]

DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = DATA_DIR / "database"

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATABASE_PATH = DATABASE_DIR / "agri_decision.db"


# ======================================================================
# UTILITY FUNCTIONS
# ======================================================================

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


# ======================================================================
# COMMUNICATION & INTEGRATION ENGINE
# ======================================================================

class CommunicationIntegrationEngine:

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

    # ==================================================================
    # DATABASE CONNECTION
    # ==================================================================

    def connect(self):

        conn = sqlite3.connect(
            self.db_path
        )

        conn.row_factory = sqlite3.Row

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        return conn

    # ==================================================================
    # TABLE INITIALIZATION
    # ==================================================================

    def initialize_database(self):

        with self.connect() as conn:

            # ----------------------------------------------------------
            # MESSAGE QUEUE
            # ----------------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                communication_message_queue
                (
                    queue_id TEXT PRIMARY KEY,
                    message_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL DEFAULT 3,
                    available_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    processed_at TEXT,
                    error_message TEXT
                )
                """
            )

            # ----------------------------------------------------------
            # THIRD-PARTY SERVICES
            # ----------------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                communication_third_party_services
                (
                    service_id TEXT PRIMARY KEY,
                    service_name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    request_payload TEXT,
                    response_payload TEXT,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )

            # ----------------------------------------------------------
            # EMAIL / SMS / PUSH NOTIFICATIONS
            # ----------------------------------------------------------

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS
                communication_notifications
                (
                    notification_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    channel TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    subject TEXT,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    sent_at TEXT,
                    error_message TEXT
                )
                """
            )

            conn.commit()


    # ==================================================================
    # TABLE VERIFICATION
    # ==================================================================

    def table_exists(
        self,
        table_name: str,
    ) -> bool:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name = ?
                """,
                (table_name,),
            ).fetchone()

        return row is not None


    # ==================================================================
    # USER VERIFICATION
    # ==================================================================

    def user_exists(
        self,
        user_id: str,
    ) -> bool:

        if not self.table_exists(
            "users"
        ):
            return False

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


    # ==================================================================
    # AUDIT LOG
    # ==================================================================

    def create_audit_log(
        self,
        action: str,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Optional[str]:

        if not self.table_exists(
            "audit_logs"
        ):
            return None

        columns = self.get_table_columns(
            "audit_logs"
        )

        if "audit_id" not in columns:
            return None

        audit_id = generate_id(
            "AUD"
        )

        safe_user_id = None

        if (
            user_id
            and self.user_exists(user_id)
        ):
            safe_user_id = user_id

        values_map = {
            "audit_id": audit_id,
            "user_id": safe_user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": "SUCCESS",
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

        if not insert_columns:
            return None

        placeholders = ", ".join(
            ["?"] * len(values)
        )

        try:

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

        except sqlite3.IntegrityError:

            # Do not allow audit logging to break
            # the communication module.
            return None


    # ==================================================================
    # GET TABLE COLUMNS
    # ==================================================================

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


    # ==================================================================
    # 1. MESSAGE QUEUE
    # ==================================================================

    def publish_message(
        self,
        message_type: str,
        payload: Dict[str, Any],
        priority: str = "NORMAL",
        max_attempts: int = 3,
    ) -> Dict[str, Any]:

        priority = priority.upper()

        allowed_priorities = {
            "LOW",
            "NORMAL",
            "HIGH",
            "URGENT",
        }

        if priority not in allowed_priorities:

            raise ValueError(
                "Invalid queue priority."
            )

        if max_attempts < 1:

            raise ValueError(
                "max_attempts must be at least 1."
            )

        queue_id = generate_id(
            "QUE"
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO
                communication_message_queue
                (
                    queue_id,
                    message_type,
                    payload,
                    priority,
                    status,
                    attempts,
                    max_attempts,
                    available_at,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    queue_id,
                    message_type,
                    json.dumps(payload),
                    priority,
                    "QUEUED",
                    0,
                    max_attempts,
                    now,
                    now,
                ),
            )

        self.create_audit_log(
            action="MESSAGE_PUBLISHED",
            entity_type="MESSAGE_QUEUE",
            entity_id=queue_id,
            details={
                "message_type": message_type,
                "priority": priority,
            },
        )

        return self.get_queue_message(
            queue_id
        )


    # ==================================================================

    def get_queue_message(
        self,
        queue_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM communication_message_queue
                WHERE queue_id = ?
                """,
                (queue_id,),
            ).fetchone()

        if not row:

            raise ValueError(
                "Queue message not found."
            )

        result = dict(row)

        try:
            result["payload"] = json.loads(
                result["payload"]
            )
        except Exception:
            pass

        return result


    # ==================================================================

    def consume_message(
        self,
        queue_id: str,
    ) -> Dict[str, Any]:

        message = self.get_queue_message(
            queue_id
        )

        if message["status"] == "COMPLETED":

            return message

        if message["status"] == "FAILED":

            return message

        attempts = (
            int(message["attempts"])
            + 1
        )

        with self.connect() as conn:

            conn.execute(
                """
                UPDATE
                communication_message_queue
                SET
                    attempts = ?,
                    status = ?,
                    processed_at = ?
                WHERE queue_id = ?
                """,
                (
                    attempts,
                    "PROCESSING",
                    None,
                    queue_id,
                ),
            )

        # Backend test consumer:
        # message processing succeeds without
        # external dependencies.

        with self.connect() as conn:

            conn.execute(
                """
                UPDATE
                communication_message_queue
                SET
                    status = ?,
                    processed_at = ?,
                    error_message = NULL
                WHERE queue_id = ?
                """,
                (
                    "COMPLETED",
                    utc_now(),
                    queue_id,
                ),
            )

        self.create_audit_log(
            action="MESSAGE_CONSUMED",
            entity_type="MESSAGE_QUEUE",
            entity_id=queue_id,
        )

        return self.get_queue_message(
            queue_id
        )


    # ==================================================================
    # 2. THIRD-PARTY SERVICE
    # ==================================================================

    def call_third_party_service(
        self,
        service_name: str,
        service_type: str,
        payload: Dict[str, Any],
        provider: str = "MOCK_PROVIDER",
    ) -> Dict[str, Any]:

        service_id = generate_id(
            "EXT"
        )

        now = utc_now()

        request_payload = json.dumps(
            payload
        )

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO
                communication_third_party_services
                (
                    service_id,
                    service_name,
                    service_type,
                    provider,
                    request_payload,
                    response_payload,
                    status,
                    attempts,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    service_id,
                    service_name,
                    service_type,
                    provider,
                    request_payload,
                    None,
                    "PROCESSING",
                    1,
                    now,
                ),
            )

        # --------------------------------------------------------------
        # Safe provider abstraction.
        #
        # No actual network request is made.
        # This allows backend integration testing without
        # external credentials or APIs.
        # --------------------------------------------------------------

        response = {
            "provider": provider,
            "service": service_name,
            "status": "SUCCESS",
            "message": (
                "Third-party service integration "
                "processed successfully."
            ),
            "request_received": payload,
        }

        with self.connect() as conn:

            conn.execute(
                """
                UPDATE
                communication_third_party_services
                SET
                    response_payload = ?,
                    status = ?,
                    completed_at = ?,
                    error_message = NULL
                WHERE service_id = ?
                """,
                (
                    json.dumps(response),
                    "COMPLETED",
                    utc_now(),
                    service_id,
                ),
            )

        self.create_audit_log(
            action="THIRD_PARTY_SERVICE_CALLED",
            entity_type="THIRD_PARTY_SERVICE",
            entity_id=service_id,
            details={
                "service_name": service_name,
                "service_type": service_type,
                "provider": provider,
            },
        )

        return self.get_third_party_service(
            service_id
        )


    # ==================================================================

    def get_third_party_service(
        self,
        service_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM communication_third_party_services
                WHERE service_id = ?
                """,
                (service_id,),
            ).fetchone()

        if not row:

            raise ValueError(
                "Third-party service record not found."
            )

        result = dict(row)

        for field in [
            "request_payload",
            "response_payload",
        ]:

            if result[field]:

                try:

                    result[field] = json.loads(
                        result[field]
                    )

                except Exception:

                    pass

        return result


    # ==================================================================
    # 3. EMAIL / SMS / PUSH NOTIFICATION
    # ==================================================================

    def send_notification(
        self,
        channel: str,
        recipient: str,
        message: str,
        user_id: Optional[str] = None,
        subject: Optional[str] = None,
        provider: str = "MOCK_PROVIDER",
    ) -> Dict[str, Any]:

        channel = channel.upper()

        allowed_channels = {
            "EMAIL",
            "SMS",
            "PUSH",
        }

        if channel not in allowed_channels:

            raise ValueError(
                "Channel must be EMAIL, SMS or PUSH."
            )

        if not recipient.strip():

            raise ValueError(
                "Recipient cannot be empty."
            )

        if not message.strip():

            raise ValueError(
                "Message cannot be empty."
            )

        if user_id and not self.user_exists(
            user_id
        ):

            raise ValueError(
                "Specified user does not exist."
            )

        notification_id = generate_id(
            "NTF"
        )

        now = utc_now()

        with self.connect() as conn:

            conn.execute(
                """
                INSERT INTO
                communication_notifications
                (
                    notification_id,
                    user_id,
                    channel,
                    recipient,
                    subject,
                    message,
                    status,
                    provider,
                    attempts,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    notification_id,
                    user_id,
                    channel,
                    recipient,
                    subject,
                    message,
                    "PROCESSING",
                    provider,
                    1,
                    now,
                ),
            )

        # --------------------------------------------------------------
        # Mock delivery provider.
        #
        # No email/SMS/push network request is made.
        # The backend records the delivery result.
        # --------------------------------------------------------------

        with self.connect() as conn:

            conn.execute(
                """
                UPDATE
                communication_notifications
                SET
                    status = ?,
                    sent_at = ?,
                    error_message = NULL
                WHERE notification_id = ?
                """,
                (
                    "SENT",
                    utc_now(),
                    notification_id,
                ),
            )

        self.create_audit_log(
            action="NOTIFICATION_SENT",
            user_id=user_id,
            entity_type="NOTIFICATION",
            entity_id=notification_id,
            details={
                "channel": channel,
                "provider": provider,
            },
        )

        return self.get_notification(
            notification_id
        )


    # ==================================================================

    def get_notification(
        self,
        notification_id: str,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            row = conn.execute(
                """
                SELECT *
                FROM communication_notifications
                WHERE notification_id = ?
                """,
                (notification_id,),
            ).fetchone()

        if not row:

            raise ValueError(
                "Notification not found."
            )

        return dict(row)


    # ==================================================================
    # SUMMARY
    # ==================================================================

    def get_summary(
        self,
    ) -> Dict[str, Any]:

        with self.connect() as conn:

            queue_total = conn.execute(
                """
                SELECT COUNT(*)
                FROM communication_message_queue
                """
            ).fetchone()[0]

            queue_completed = conn.execute(
                """
                SELECT COUNT(*)
                FROM communication_message_queue
                WHERE status = 'COMPLETED'
                """
            ).fetchone()[0]

            service_total = conn.execute(
                """
                SELECT COUNT(*)
                FROM communication_third_party_services
                """
            ).fetchone()[0]

            service_completed = conn.execute(
                """
                SELECT COUNT(*)
                FROM communication_third_party_services
                WHERE status = 'COMPLETED'
                """
            ).fetchone()[0]

            notification_total = conn.execute(
                """
                SELECT COUNT(*)
                FROM communication_notifications
                """
            ).fetchone()[0]

            notification_sent = conn.execute(
                """
                SELECT COUNT(*)
                FROM communication_notifications
                WHERE status = 'SENT'
                """
            ).fetchone()[0]

            channel_rows = conn.execute(
                """
                SELECT channel, COUNT(*) AS count
                FROM communication_notifications
                GROUP BY channel
                """
            ).fetchall()

        notifications_by_channel = {
            row["channel"]: row["count"]
            for row in channel_rows
        }

        return {
            "queue_total": queue_total,
            "queue_completed": queue_completed,
            "third_party_total": service_total,
            "third_party_completed":
                service_completed,
            "notifications_total":
                notification_total,
            "notifications_sent":
                notification_sent,
            "notifications_by_channel":
                notifications_by_channel,
        }


# ======================================================================
# MAIN INTEGRATION TEST
# ======================================================================

def main():

    print()
    print("=" * 70)
    print(
        "COMMUNICATION & INTEGRATION + DATABASE INTEGRATION TEST"
    )
    print("=" * 70)

    print()
    print("Components:")
    print("1. Message Queue")
    print("2. Third-Party Service")
    print(
        "3. Email / SMS / Push Notification"
    )

    print()
    print("No frontend.")
    print("No FastAPI.")
    print("No external API.")
    print("No ML model.")
    print("No new dataset.")
    print("No REST API Integration.")

    # ==================================================================
    # 1. ENGINE INITIALIZATION
    # ==================================================================

    print()
    print("=" * 70)
    print("1. ENGINE INITIALIZATION")
    print("=" * 70)

    engine = (
        CommunicationIntegrationEngine()
    )

    required_tables = [
        "communication_message_queue",
        "communication_third_party_services",
        "communication_notifications",
    ]

    for table in required_tables:

        assert engine.table_exists(
            table
        )

        print(
            f"✓ {table} table verified"
        )

    print(
        "✓ SQLite Communication database connected"
    )

    # ==================================================================
    # 2. TEST USER VERIFICATION
    # ==================================================================

    print()
    print("=" * 70)
    print("2. TEST USER VERIFICATION")
    print("=" * 70)

    user_id = None
    user_role = None

    if engine.table_exists("users"):

        with engine.connect() as conn:

            row = conn.execute(
                """
                SELECT user_id, role
                FROM users
                WHERE is_active = 1
                ORDER BY created_at
                LIMIT 1
                """
            ).fetchone()

        if row:

            user_id = row["user_id"]
            user_role = row["role"]

            print(
                "✓ Existing active user found"
            )

            print(
                "✓ User ID :",
                user_id
            )

            print(
                "✓ Role :",
                user_role
            )

        else:

            print(
                "✓ No active application user required"
            )

    # ==================================================================
    # 3. MESSAGE QUEUE
    # ==================================================================

    print()
    print("=" * 70)
    print("3. MESSAGE QUEUE")
    print("=" * 70)

    queue_message = (
        engine.publish_message(
            message_type="NOTIFICATION",
            payload={
                "event": "CROP_AVAILABLE",
                "crop": "Bajra",
                "quantity_kg": 900,
            },
            priority="HIGH",
        )
    )

    assert (
        queue_message["status"]
        == "QUEUED"
    )

    print(
        "✓ Message published"
    )

    print(
        "✓ Queue ID :",
        queue_message["queue_id"]
    )

    print(
        "✓ Message Type :",
        queue_message["message_type"]
    )

    print(
        "✓ Priority :",
        queue_message["priority"]
    )

    processed_message = (
        engine.consume_message(
            queue_message["queue_id"]
        )
    )

    assert (
        processed_message["status"]
        == "COMPLETED"
    )

    print(
        "✓ Message consumed"
    )

    print(
        "✓ Message processing completed"
    )

    print(
        "✓ Message queue verified"
    )

    # ==================================================================
    # 4. THIRD-PARTY SERVICE
    # ==================================================================

    print()
    print("=" * 70)
    print("4. THIRD-PARTY SERVICE")
    print("=" * 70)

    third_party = (
        engine.call_third_party_service(
            service_name="Market Service",
            service_type="MARKET_DATA",
            payload={
                "market": "Kheda APMC",
                "crop": "Bajra",
                "request": "market_status",
            },
            provider="MOCK_MARKET_PROVIDER",
        )
    )

    assert (
        third_party["status"]
        == "COMPLETED"
    )

    assert (
        third_party["response_payload"]
        is not None
    )

    print(
        "✓ Third-party service request created"
    )

    print(
        "✓ Service ID :",
        third_party["service_id"]
    )

    print(
        "✓ Service :",
        third_party["service_name"]
    )

    print(
        "✓ Provider :",
        third_party["provider"]
    )

    print(
        "✓ Third-party service response received"
    )

    print(
        "✓ Third-party service integration verified"
    )

    # ==================================================================
    # 5. EMAIL NOTIFICATION
    # ==================================================================

    print()
    print("=" * 70)
    print("5. EMAIL NOTIFICATION")
    print("=" * 70)

    email = engine.send_notification(
        channel="EMAIL",
        recipient="farmer@example.com",
        subject="Crop Update",
        message=(
            "Your crop listing has been updated."
        ),
        user_id=user_id,
        provider="MOCK_EMAIL_PROVIDER",
    )

    assert (
        email["status"]
        == "SENT"
    )

    assert (
        email["channel"]
        == "EMAIL"
    )

    print(
        "✓ Email notification created"
    )

    print(
        "✓ Notification ID :",
        email["notification_id"]
    )

    print(
        "✓ Email delivery status :",
        email["status"]
    )

    print(
        "✓ Email notification verified"
    )

    # ==================================================================
    # 6. SMS NOTIFICATION
    # ==================================================================

    print()
    print("=" * 70)
    print("6. SMS NOTIFICATION")
    print("=" * 70)

    sms = engine.send_notification(
        channel="SMS",
        recipient="+919999999999",
        message=(
            "Your auction bid has been updated."
        ),
        user_id=user_id,
        provider="MOCK_SMS_PROVIDER",
    )

    assert (
        sms["status"]
        == "SENT"
    )

    assert (
        sms["channel"]
        == "SMS"
    )

    print(
        "✓ SMS notification created"
    )

    print(
        "✓ Notification ID :",
        sms["notification_id"]
    )

    print(
        "✓ SMS delivery status :",
        sms["status"]
    )

    print(
        "✓ SMS notification verified"
    )

    # ==================================================================
    # 7. PUSH NOTIFICATION
    # ==================================================================

    print()
    print("=" * 70)
    print("7. PUSH NOTIFICATION")
    print("=" * 70)

    push = engine.send_notification(
        channel="PUSH",
        recipient="DEVICE_TOKEN_TEST",
        message=(
            "New market opportunity is available."
        ),
        user_id=user_id,
        provider="MOCK_PUSH_PROVIDER",
    )

    assert (
        push["status"]
        == "SENT"
    )

    assert (
        push["channel"]
        == "PUSH"
    )

    print(
        "✓ Push notification created"
    )

    print(
        "✓ Notification ID :",
        push["notification_id"]
    )

    print(
        "✓ Push delivery status :",
        push["status"]
    )

    print(
        "✓ Push notification verified"
    )

    # ==================================================================
    # 8. DATABASE PERSISTENCE
    # ==================================================================

    print()
    print("=" * 70)
    print(
        "8. DATABASE PERSISTENCE VERIFICATION"
    )
    print("=" * 70)

    with engine.connect() as conn:

        queue_exists = conn.execute(
            """
            SELECT 1
            FROM communication_message_queue
            WHERE queue_id = ?
            """,
            (
                queue_message[
                    "queue_id"
                ],
            ),
        ).fetchone()

        service_exists = conn.execute(
            """
            SELECT 1
            FROM communication_third_party_services
            WHERE service_id = ?
            """,
            (
                third_party[
                    "service_id"
                ],
            ),
        ).fetchone()

        email_exists = conn.execute(
            """
            SELECT 1
            FROM communication_notifications
            WHERE notification_id = ?
            """,
            (
                email[
                    "notification_id"
                ],
            ),
        ).fetchone()

        sms_exists = conn.execute(
            """
            SELECT 1
            FROM communication_notifications
            WHERE notification_id = ?
            """,
            (
                sms[
                    "notification_id"
                ],
            ),
        ).fetchone()

        push_exists = conn.execute(
            """
            SELECT 1
            FROM communication_notifications
            WHERE notification_id = ?
            """,
            (
                push[
                    "notification_id"
                ],
            ),
        ).fetchone()

    assert queue_exists
    assert service_exists
    assert email_exists
    assert sms_exists
    assert push_exists

    print(
        "✓ Message queue persistence verified"
    )

    print(
        "✓ Third-party service persistence verified"
    )

    print(
        "✓ Email persistence verified"
    )

    print(
        "✓ SMS persistence verified"
    )

    print(
        "✓ Push notification persistence verified"
    )

    # ==================================================================
    # 9. SUMMARY
    # ==================================================================

    print()
    print("=" * 70)
    print("9. COMMUNICATION SUMMARY")
    print("=" * 70)

    summary = (
        engine.get_summary()
    )

    print(
        "✓ Total Queue Messages :",
        summary["queue_total"]
    )

    print(
        "✓ Completed Queue Messages :",
        summary["queue_completed"]
    )

    print(
        "✓ Third-Party Service Calls :",
        summary["third_party_total"]
    )

    print(
        "✓ Completed Third-Party Calls :",
        summary[
            "third_party_completed"
        ]
    )

    print(
        "✓ Total Notifications :",
        summary[
            "notifications_total"
        ]
    )

    print(
        "✓ Sent Notifications :",
        summary[
            "notifications_sent"
        ]
    )

    print(
        "✓ Notifications by Channel :",
        summary[
            "notifications_by_channel"
        ]
    )

    # ==================================================================
    # 10. FINAL STATUS
    # ==================================================================

    print()
    print("=" * 70)
    print(
        "COMMUNICATION & INTEGRATION FINAL STATUS"
    )
    print("=" * 70)

    print(
        "✓ Message Queue              : VERIFIED"
    )

    print(
        "✓ Third-Party Service        : VERIFIED"
    )

    print(
        "✓ Email Notification         : VERIFIED"
    )

    print(
        "✓ SMS Notification           : VERIFIED"
    )

    print(
        "✓ Push Notification          : VERIFIED"
    )

    print(
        "✓ SQLite Integration         : VERIFIED"
    )

    print(
        "✓ Database Persistence       : VERIFIED"
    )

    print()
    print(
        "COMMUNICATION & INTEGRATION STATUS: COMPLETE"
    )


# ======================================================================
# ENTRY POINT
# ======================================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print()
        print("=" * 70)
        print(
            "COMMUNICATION & INTEGRATION TEST FAILED"
        )
        print("=" * 70)

        print(
            "Error Type :",
            type(exc).__name__,
        )

        print(
            "Error      :",
            str(exc),
        )

        raise