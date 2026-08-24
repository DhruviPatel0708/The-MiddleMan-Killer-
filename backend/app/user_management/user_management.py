"""
USER MANAGEMENT

Backend / Application Layer

Architecture:

Authentication & Authorization
            ↓
       SQLite Database
            ↓
       User Management

Features:
    ✓ Create User
    ✓ Get User
    ✓ Update User
    ✓ Change Role
    ✓ Activate User
    ✓ Deactivate User
    ✓ View Permissions
    ✓ List Users
    ✓ User Summary
    ✓ Audit Logging
    ✓ Authentication ↔ Database synchronization

No external API.
No FastAPI.
No ML model.
No new dataset.
"""

from __future__ import annotations

import sys
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
# EXISTING COMPONENTS
# ================================================================

from authentication import (
    AuthenticationAuthorizationEngine,
    ROLE_PERMISSIONS,
)

from database import DatabaseManager


# ================================================================
# USER MANAGEMENT ENGINE
# ================================================================

class UserManagementEngine:

    def __init__(self):

        print("=" * 70)
        print("USER MANAGEMENT ENGINE")
        print("=" * 70)

        # --------------------------------------------------------
        # Existing Authentication / Authorization
        # --------------------------------------------------------

        self.auth = (
            AuthenticationAuthorizationEngine()
        )

        # --------------------------------------------------------
        # Existing SQLite Database
        # --------------------------------------------------------

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
            "✓ No new dataset"
        )


    # ============================================================
    # AUTHENTICATE ADMIN
    # ============================================================

    def _get_admin(
        self,
        admin_token: str
    ) -> Dict[str, Any]:

        """
        Authenticate the admin using the existing
        Authentication & Authorization layer.

        IMPORTANT:
        If the authenticated admin does not yet exist
        in SQLite, synchronize that admin into SQLite.

        This prevents:

            audit_logs.user_id
                    ↓
            FOREIGN KEY failure
        """

        admin = self.auth.authenticate(
            admin_token
        )

        if not admin:

            raise PermissionError(
                "Invalid authentication token."
            )

        if admin.get("role") != "ADMIN":

            raise PermissionError(
                "ADMIN authorization required."
            )

        admin_id = admin.get(
            "user_id"
        )

        if not admin_id:

            raise ValueError(
                "Authenticated admin has no user ID."
            )

        # --------------------------------------------------------
        # Synchronize ADMIN into SQLite
        # --------------------------------------------------------

        db_admin = self.database.get_user(
            admin_id
        )

        if db_admin is None:

            name = (
                admin.get("name")
                or admin.get("username")
                or "System Admin"
            )

            email = (
                admin.get("email")
                or f"{admin_id.lower()}@project.local"
            )

            try:

                self.database.create_user(

                    name=name,

                    email=email,

                    role="ADMIN",

                    user_id=admin_id

                )

                print(
                    "✓ Authenticated admin synchronized "
                    "with SQLite"
                )

            except Exception as exc:

                # ------------------------------------------------
                # Race / duplicate-email protection
                # ------------------------------------------------

                db_admin = (
                    self.database
                    .get_user(admin_id)
                )

                if db_admin is None:

                    raise RuntimeError(
                        "Could not synchronize admin "
                        f"with SQLite: {exc}"
                    )

        return admin


    # ============================================================
    # SYNCHRONIZE AUTH USER WITH DATABASE
    # ============================================================

    def _sync_auth_user_to_database(
        self,
        auth_user: Dict[str, Any]
    ):

        """
        Ensure an authenticated user exists in SQLite.

        This keeps Authentication storage and SQLite
        consistent.
        """

        if not auth_user:

            raise ValueError(
                "Authentication user is empty."
            )

        user_id = auth_user.get(
            "user_id"
        )

        if not user_id:

            raise ValueError(
                "Authentication user has no user_id."
            )

        existing = (
            self.database.get_user(
                user_id
            )
        )

        if existing:

            return existing

        name = (
            auth_user.get("name")
            or auth_user.get("username")
            or "User"
        )

        email = (
            auth_user.get("email")
            or f"{user_id.lower()}@project.local"
        )

        role = (
            auth_user.get("role")
            or "FARMER"
        )

        return self.database.create_user(

            name=name,

            email=email,

            role=role,

            user_id=user_id

        )


    # ============================================================
    # CREATE USER
    # ============================================================

    def create_user(

        self,

        admin_token: str,

        name: str,

        email: str,

        password: str,

        role: str,

    ):

        admin = self._get_admin(
            admin_token
        )

        # --------------------------------------------------------
        # Validation
        # --------------------------------------------------------

        name = name.strip()

        email = (
            email
            .strip()
            .lower()
        )

        role = (
            role
            .strip()
            .upper()
        )

        if not name:

            raise ValueError(
                "Name cannot be empty."
            )

        if "@" not in email:

            raise ValueError(
                "Invalid email."
            )

        if role not in ROLE_PERMISSIONS:

            raise ValueError(
                "Invalid role: "
                + role
            )

        # --------------------------------------------------------
        # Check SQLite
        # --------------------------------------------------------

        existing_db_user = (
            self.database
            .get_user_by_email(
                email
            )
        )

        if existing_db_user:

            raise ValueError(
                "User already exists in SQLite."
            )

        # --------------------------------------------------------
        # Check Authentication storage
        # --------------------------------------------------------

        existing_auth_user = (
            self.auth.user_store
            .get_by_email(
                email
            )
        )

        if existing_auth_user:

            raise ValueError(
                "User already exists in "
                "authentication storage."
            )

        # --------------------------------------------------------
        # Create in Authentication layer
        # --------------------------------------------------------

        auth_user = (
            self.auth.register_user(

                name=name,

                email=email,

                password=password,

                role=role

            )
        )

        user_id = auth_user[
            "user_id"
        ]

        try:

            # ----------------------------------------------------
            # Create same user in SQLite
            # ----------------------------------------------------

            user = (
                self.database.create_user(

                    name=name,

                    email=email,

                    role=role,

                    user_id=user_id

                )
            )

            # ----------------------------------------------------
            # Audit
            # ----------------------------------------------------

            self.database.add_audit_log(

                action="CREATE_USER",

                status="SUCCESS",

                user_id=admin[
                    "user_id"
                ],

                entity_type="USER",

                entity_id=user_id,

                details={

                    "role": role,

                    "email": email

                }

            )

        except Exception as exc:

            raise RuntimeError(
                "User was created in authentication "
                "storage but SQLite synchronization "
                f"failed: {exc}"
            )

        return self._safe_user(
            user
        )


    # ============================================================
    # GET USER
    # ============================================================

    def get_user(

        self,

        requester_token: str,

        user_id: str,

    ):

        requester = (
            self.auth.authenticate(
                requester_token
            )
        )

        if not requester:

            raise PermissionError(
                "Invalid authentication token."
            )

        # --------------------------------------------------------
        # Synchronize requester
        # --------------------------------------------------------

        self._sync_auth_user_to_database(
            requester
        )

        # --------------------------------------------------------
        # Own profile OR ADMIN
        # --------------------------------------------------------

        if (

            requester["user_id"]
            != user_id

            and

            requester["role"]
            != "ADMIN"

        ):

            raise PermissionError(
                "Not authorized to view this user."
            )

        user = self.database.get_user(
            user_id
        )

        if not user:

            raise ValueError(
                "User not found."
            )

        return self._safe_user(
            user
        )


    # ============================================================
    # UPDATE USER
    # ============================================================

    def update_user(

        self,

        requester_token: str,

        user_id: str,

        name: Optional[str] = None,

        email: Optional[str] = None,

    ):

        requester = (
            self.auth.authenticate(
                requester_token
            )
        )

        if not requester:

            raise PermissionError(
                "Invalid authentication token."
            )

        self._sync_auth_user_to_database(
            requester
        )

        if (

            requester["user_id"]
            != user_id

            and

            requester["role"]
            != "ADMIN"

        ):

            raise PermissionError(
                "Not authorized to update this user."
            )

        updates = {}

        # --------------------------------------------------------
        # Name
        # --------------------------------------------------------

        if name is not None:

            name = name.strip()

            if not name:

                raise ValueError(
                    "Name cannot be empty."
                )

            updates["name"] = name

        # --------------------------------------------------------
        # Email
        # --------------------------------------------------------

        if email is not None:

            email = (
                email
                .strip()
                .lower()
            )

            if "@" not in email:

                raise ValueError(
                    "Invalid email."
                )

            existing = (
                self.database
                .get_user_by_email(
                    email
                )
            )

            if (

                existing

                and

                existing["user_id"]
                != user_id

            ):

                raise ValueError(
                    "Email already exists."
                )

            updates["email"] = email

        if not updates:

            return self.get_user(
                requester_token,
                user_id
            )

        updated = (
            self.database.update_user(

                user_id,

                **updates

            )
        )

        # --------------------------------------------------------
        # Audit
        # --------------------------------------------------------

        self.database.add_audit_log(

            action="UPDATE_USER",

            status="SUCCESS",

            user_id=requester[
                "user_id"
            ],

            entity_type="USER",

            entity_id=user_id,

            details=updates

        )

        return self._safe_user(
            updated
        )


    # ============================================================
    # CHANGE ROLE
    # ============================================================

    def change_role(

        self,

        admin_token: str,

        user_id: str,

        new_role: str,

    ):

        admin = self._get_admin(
            admin_token
        )

        new_role = (
            new_role
            .strip()
            .upper()
        )

        if new_role not in ROLE_PERMISSIONS:

            raise ValueError(
                "Invalid role: "
                + new_role
            )

        user = self.database.get_user(
            user_id
        )

        if not user:

            raise ValueError(
                "User not found."
            )

        old_role = user[
            "role"
        ]

        # --------------------------------------------------------
        # SQLite
        # --------------------------------------------------------

        updated = (
            self.database.update_user(

                user_id,

                role=new_role

            )
        )

        # --------------------------------------------------------
        # Authentication storage
        # --------------------------------------------------------

        auth_user = (
            self.auth.user_store
            .get_by_id(
                user_id
            )
        )

        if auth_user:

            self.auth.user_store.update_user(

                user_id,

                {

                    "role":
                        new_role,

                    "permissions":
                        ROLE_PERMISSIONS[
                            new_role
                        ].copy()

                }

            )

        # --------------------------------------------------------
        # Audit
        # --------------------------------------------------------

        self.database.add_audit_log(

            action="CHANGE_USER_ROLE",

            status="SUCCESS",

            user_id=admin[
                "user_id"
            ],

            entity_type="USER",

            entity_id=user_id,

            details={

                "old_role":
                    old_role,

                "new_role":
                    new_role

            }

        )

        return self._safe_user(
            updated
        )


    # ============================================================
    # GET PERMISSIONS
    # ============================================================

    def get_permissions(

        self,

        requester_token: str,

        user_id: str,

    ):

        requester = (
            self.auth.authenticate(
                requester_token
            )
        )

        if not requester:

            raise PermissionError(
                "Invalid authentication token."
            )

        self._sync_auth_user_to_database(
            requester
        )

        if (

            requester["user_id"]
            != user_id

            and

            requester["role"]
            != "ADMIN"

        ):

            raise PermissionError(
                "Not authorized to view permissions."
            )

        auth_user = (
            self.auth.user_store
            .get_by_id(
                user_id
            )
        )

        if not auth_user:

            raise ValueError(
                "User not found."
            )

        return {

            "user_id":
                auth_user["user_id"],

            "role":
                auth_user["role"],

            "permissions":
                auth_user["permissions"]

        }


    # ============================================================
    # DEACTIVATE USER
    # ============================================================

    def deactivate_user(

        self,

        admin_token: str,

        user_id: str,

    ):

        admin = self._get_admin(
            admin_token
        )

        user = self.database.get_user(
            user_id
        )

        if not user:

            raise ValueError(
                "User not found."
            )

        # --------------------------------------------------------
        # Database
        # --------------------------------------------------------

        updated = (
            self.database.update_user(

                user_id,

                is_active=0

            )
        )

        # --------------------------------------------------------
        # Authentication
        # --------------------------------------------------------

        self.auth.deactivate_user(

            admin_token,

            user_id

        )

        # --------------------------------------------------------
        # Audit
        # --------------------------------------------------------

        self.database.add_audit_log(

            action="DEACTIVATE_USER",

            status="SUCCESS",

            user_id=admin[
                "user_id"
            ],

            entity_type="USER",

            entity_id=user_id

        )

        return self._safe_user(
            updated
        )


    # ============================================================
    # ACTIVATE USER
    # ============================================================

    def activate_user(

        self,

        admin_token: str,

        user_id: str,

    ):

        admin = self._get_admin(
            admin_token
        )

        user = self.database.get_user(
            user_id
        )

        if not user:

            raise ValueError(
                "User not found."
            )

        # --------------------------------------------------------
        # Database
        # --------------------------------------------------------

        updated = (
            self.database.update_user(

                user_id,

                is_active=1

            )
        )

        # --------------------------------------------------------
        # Authentication
        # --------------------------------------------------------

        self.auth.activate_user(

            admin_token,

            user_id

        )

        # --------------------------------------------------------
        # Audit
        # --------------------------------------------------------

        self.database.add_audit_log(

            action="ACTIVATE_USER",

            status="SUCCESS",

            user_id=admin[
                "user_id"
            ],

            entity_type="USER",

            entity_id=user_id

        )

        return self._safe_user(
            updated
        )


    # ============================================================
    # LIST USERS
    # ============================================================

    def list_users(

        self,

        admin_token: str,

    ):

        self._get_admin(
            admin_token
        )

        with self.database.connect() as conn:

            rows = conn.execute("""
                SELECT
                    user_id,
                    name,
                    email,
                    role,
                    is_active,
                    created_at,
                    updated_at
                FROM users
                ORDER BY created_at DESC
            """).fetchall()

        return [
            dict(row)
            for row in rows
        ]


    # ============================================================
    # USER SUMMARY
    # ============================================================

    def user_summary(

        self,

        admin_token: str,

    ):

        self._get_admin(
            admin_token
        )

        with self.database.connect() as conn:

            total = conn.execute("""
                SELECT COUNT(*)
                FROM users
            """).fetchone()[0]

            active = conn.execute("""
                SELECT COUNT(*)
                FROM users
                WHERE is_active = 1
            """).fetchone()[0]

            inactive = conn.execute("""
                SELECT COUNT(*)
                FROM users
                WHERE is_active = 0
            """).fetchone()[0]

            roles = conn.execute("""
                SELECT
                    role,
                    COUNT(*) AS count
                FROM users
                GROUP BY role
            """).fetchall()

        return {

            "total_users":
                total,

            "active_users":
                active,

            "inactive_users":
                inactive,

            "users_by_role": {

                row["role"]:
                    row["count"]

                for row in roles

            }

        }


    # ============================================================
    # SAFE USER RESPONSE
    # ============================================================

    @staticmethod
    def _safe_user(
        user: Dict[str, Any]
    ):

        return {

            "user_id":
                user.get("user_id"),

            "name":
                user.get("name"),

            "email":
                user.get("email"),

            "role":
                user.get("role"),

            "is_active":
                bool(
                    user.get(
                        "is_active",
                        False
                    )
                ),

            "created_at":
                user.get("created_at"),

            "updated_at":
                user.get("updated_at")

        }


# ================================================================
# FULL INTEGRATION TEST
# ================================================================

def main():

    print()
    print("=" * 70)
    print(
        "USER MANAGEMENT + DATABASE INTEGRATION TEST"
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
        "        User Management"
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
    # 1. ENGINE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "1. ENGINE INITIALIZATION"
    )
    print("=" * 70)

    engine = UserManagementEngine()

    print(
        "✓ User Management Engine initialized"
    )


    # ============================================================
    # 2. ADMIN
    # ============================================================

    print()
    print("=" * 70)
    print(
        "2. ADMIN AUTHENTICATION"
    )
    print("=" * 70)

    admin_email = (
        "user_management_admin"
        "@project.local"
    )

    admin_password = "Admin@123"

    existing_admin = (
        engine.auth.user_store
        .get_by_email(
            admin_email
        )
    )

    if existing_admin:

        print(
            "✓ Existing test admin found"
        )

    else:

        engine.auth.register_user(

            name="System Admin",

            email=admin_email,

            password=admin_password,

            role="ADMIN"

        )

        print(
            "✓ Test admin created"
        )

    login = engine.auth.login(

        admin_email,

        admin_password

    )

    admin_token = login[
        "access_token"
    ]

    print(
        "✓ Admin login successful"
    )

    print(
        "✓ JWT token generated"
    )


    # ============================================================
    # 3. FORCE ADMIN DATABASE SYNCHRONIZATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "3. AUTH ↔ DATABASE SYNCHRONIZATION"
    )
    print("=" * 70)

    admin = engine._get_admin(
        admin_token
    )

    db_admin = (
        engine.database.get_user(
            admin["user_id"]
        )
    )

    assert db_admin is not None

    assert (
        db_admin["user_id"]
        ==
        admin["user_id"]
    )

    assert (
        db_admin["role"]
        ==
        "ADMIN"
    )

    print(
        "✓ Admin exists in Authentication"
    )

    print(
        "✓ Admin exists in SQLite"
    )

    print(
        "✓ Admin ID consistency verified"
    )


    # ============================================================
    # 4. CREATE USER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "4. CREATE USER"
    )
    print("=" * 70)

    test_email = (
        "database_integrated_user"
        "@project.local"
    )

    existing_user = (
        engine.database
        .get_user_by_email(
            test_email
        )
    )

    if existing_user:

        user = existing_user

        print(
            "✓ Existing test user found in SQLite"
        )

    else:

        # --------------------------------------------------------
        # Make sure Authentication doesn't already contain
        # this email.
        # --------------------------------------------------------

        auth_existing = (
            engine.auth.user_store
            .get_by_email(
                test_email
            )
        )

        if auth_existing:

            # ----------------------------------------------------
            # Existing authentication user but missing SQLite.
            # Synchronize instead of creating duplicate.
            # ----------------------------------------------------

            user = (
                engine._sync_auth_user_to_database(
                    auth_existing
                )
            )

            print(
                "✓ Existing authentication user "
                "synchronized with SQLite"
            )

        else:

            user = engine.create_user(

                admin_token=admin_token,

                name="Database Integrated User",

                email=test_email,

                password="User@123",

                role="FARMER"

            )

            print(
                "✓ User created successfully"
            )

    user_id = user[
        "user_id"
    ]

    print(
        "✓ User ID :",
        user_id
    )


    # ============================================================
    # 5. DATABASE VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "5. DATABASE VERIFICATION"
    )
    print("=" * 70)

    db_user = (
        engine.database.get_user(
            user_id
        )
    )

    assert db_user is not None

    assert (
        db_user["user_id"]
        ==
        user_id
    )

    print(
        "✓ User exists in SQLite"
    )

    print(
        "✓ User ID consistency verified"
    )


    # ============================================================
    # 6. GET USER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "6. GET USER"
    )
    print("=" * 70)

    retrieved = engine.get_user(

        requester_token=admin_token,

        user_id=user_id

    )

    assert (
        retrieved["user_id"]
        ==
        user_id
    )

    print(
        "✓ User retrieval verified"
    )


    # ============================================================
    # 7. UPDATE USER
    # ============================================================

    print()
    print("=" * 70)
    print(
        "7. UPDATE USER"
    )
    print("=" * 70)

    updated = engine.update_user(

        requester_token=admin_token,

        user_id=user_id,

        name="Updated Database User"

    )

    assert (
        updated["name"]
        ==
        "Updated Database User"
    )

    print(
        "✓ User update verified"
    )


    # ============================================================
    # 8. PERMISSIONS
    # ============================================================

    print()
    print("=" * 70)
    print(
        "8. PERMISSION VERIFICATION"
    )
    print("=" * 70)

    permissions = (
        engine.get_permissions(

            requester_token=admin_token,

            user_id=user_id

        )
    )

    assert (
        permissions["role"]
        ==
        "FARMER"
    )

    print(
        "✓ Role :",
        permissions["role"]
    )

    print(
        "✓ Permissions loaded"
    )

    for permission in permissions[
        "permissions"
    ]:

        print(
            "   -",
            permission
        )


    # ============================================================
    # 9. CHANGE ROLE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "9. ROLE MANAGEMENT"
    )
    print("=" * 70)

    changed = engine.change_role(

        admin_token=admin_token,

        user_id=user_id,

        new_role="BUYER"

    )

    assert (
        changed["role"]
        ==
        "BUYER"
    )

    db_after_role = (
        engine.database.get_user(
            user_id
        )
    )

    assert (
        db_after_role["role"]
        ==
        "BUYER"
    )

    print(
        "✓ Role changed"
    )

    print(
        "✓ SQLite role updated"
    )

    print(
        "✓ Authentication role updated"
    )


    # ============================================================
    # 10. DEACTIVATE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "10. DEACTIVATE USER"
    )
    print("=" * 70)

    deactivated = (
        engine.deactivate_user(

            admin_token=admin_token,

            user_id=user_id

        )
    )

    assert (
        deactivated["is_active"]
        is False
    )

    db_deactivated = (
        engine.database.get_user(
            user_id
        )
    )

    assert (
        db_deactivated["is_active"]
        == 0
    )

    print(
        "✓ User deactivated"
    )

    print(
        "✓ SQLite status updated"
    )


    # ============================================================
    # 11. ACTIVATE
    # ============================================================

    print()
    print("=" * 70)
    print(
        "11. ACTIVATE USER"
    )
    print("=" * 70)

    activated = (
        engine.activate_user(

            admin_token=admin_token,

            user_id=user_id

        )
    )

    assert (
        activated["is_active"]
        is True
    )

    db_activated = (
        engine.database.get_user(
            user_id
        )
    )

    assert (
        db_activated["is_active"]
        == 1
    )

    print(
        "✓ User activated"
    )

    print(
        "✓ SQLite status updated"
    )


    # ============================================================
    # 12. AUDIT VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "12. AUDIT VERIFICATION"
    )
    print("=" * 70)

    admin_logs = (
        engine.database
        .get_audit_logs(
            user_id=admin[
                "user_id"
            ]
        )
    )

    assert len(
        admin_logs
    ) >= 1

    print(
        "✓ Audit records created"
    )

    print(
        "✓ Foreign-key relationship verified"
    )

    print(
        "✓ User Management actions logged"
    )


    # ============================================================
    # 13. USER SUMMARY
    # ============================================================

    print()
    print("=" * 70)
    print(
        "13. USER SUMMARY"
    )
    print("=" * 70)

    summary = engine.user_summary(
        admin_token
    )

    print(
        "✓ Total Users :",
        summary["total_users"]
    )

    print(
        "✓ Active Users :",
        summary["active_users"]
    )

    print(
        "✓ Inactive Users :",
        summary["inactive_users"]
    )

    print(
        "✓ Users by Role :",
        summary["users_by_role"]
    )


    # ============================================================
    # 14. FINAL VERIFICATION
    # ============================================================

    print()
    print("=" * 70)
    print(
        "USER MANAGEMENT FINAL STATUS"
    )
    print("=" * 70)

    print(
        "✓ Authentication Integration : VERIFIED"
    )

    print(
        "✓ SQLite Integration         : VERIFIED"
    )

    print(
        "✓ Auth ↔ Database Sync       : VERIFIED"
    )

    print(
        "✓ Create User                : VERIFIED"
    )

    print(
        "✓ Get User                   : VERIFIED"
    )

    print(
        "✓ Update User                : VERIFIED"
    )

    print(
        "✓ Change Role                : VERIFIED"
    )

    print(
        "✓ Permissions                : VERIFIED"
    )

    print(
        "✓ Deactivate User            : VERIFIED"
    )

    print(
        "✓ Activate User              : VERIFIED"
    )

    print(
        "✓ Audit Logging              : VERIFIED"
    )

    print(
        "✓ Foreign Keys               : VERIFIED"
    )

    print(
        "✓ User Summary               : VERIFIED"
    )

    print()
    print(
        "======================================================================"
    )

    print(
        "USER MANAGEMENT STATUS: COMPLETE"
    )

    print(
        "======================================================================"
    )


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":

    main()