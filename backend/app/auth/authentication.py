"""
AUTHENTICATION & AUTHORIZATION ENGINE

Architecture components:
1. User Login
2. JWT Authentication
3. Role-Based Access Control (RBAC)
4. Permissions Management

Project constraints:
- No external API
- No ML model
- No new dataset
- No FastAPI dependency

Storage:
- Local JSON file
- Can later be connected to the project's database layer
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from pathlib import Path
from typing import Any, Dict, Optional


# ================================================================
# PATH CONFIGURATION
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

AUTH_DATA_DIR = PROJECT_ROOT / "data" / "auth"

AUTH_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

USERS_FILE = AUTH_DATA_DIR / "users.json"


# ================================================================
# JWT CONFIGURATION
# ================================================================

JWT_SECRET = os.getenv(
    "PROJECT_JWT_SECRET",
    "CHANGE_THIS_SECRET_BEFORE_PRODUCTION"
)

JWT_ALGORITHM = "HS256"

JWT_EXPIRY_SECONDS = 60 * 60


# ================================================================
# ROLES AND PERMISSIONS
# ================================================================

ROLE_PERMISSIONS = {

    "FARMER": [

        "crop:create",
        "crop:read",
        "crop:update",

        "auction:read",

        "bid:read",

        "order:read",

        "transaction:read",

        "payment:read",

        "recommendation:read",

        "report:read",

        "support:create",
    ],

    "BUYER": [

        "crop:read",

        "auction:read",

        "bid:create",
        "bid:read",

        "order:create",
        "order:read",

        "transaction:read",

        "payment:read",

        "report:read",

        "support:create",
    ],

    "LOGISTICS": [

        "crop:read",

        "order:read",

        "transaction:read",

        "logistics:read",
        "logistics:update",

        "delivery:read",
        "delivery:update",

        "support:create",
    ],

    "ADMIN": [

        "*"

    ],

    "SUPPORT": [

        "support:create",
        "support:read",
        "support:update",

        "dispute:read",
        "dispute:update",

        "settlement:read",
        "settlement:update",

        "user:read",

        "report:read",
    ],
}


# ================================================================
# BASE64 URL HELPERS
# ================================================================

def base64url_encode(data: bytes) -> str:

    return base64.urlsafe_b64encode(
        data
    ).rstrip(b"=").decode("ascii")


def base64url_decode(data: str) -> bytes:

    padding = "=" * (-len(data) % 4)

    return base64.urlsafe_b64decode(
        data + padding
    )


# ================================================================
# JWT SIGNATURE
# ================================================================

def create_signature(
    message: str
) -> str:

    digest = hmac.new(

        JWT_SECRET.encode("utf-8"),

        message.encode("utf-8"),

        hashlib.sha256

    ).digest()

    return base64url_encode(digest)


# ================================================================
# CREATE JWT
# ================================================================

def create_jwt(
    user: Dict[str, Any]
) -> str:

    current_time = int(
        time.time()
    )

    header = {

        "alg": JWT_ALGORITHM,

        "typ": "JWT"

    }

    payload = {

        "sub": user["user_id"],

        "email": user["email"],

        "role": user["role"],

        "permissions": user["permissions"],

        "iat": current_time,

        "exp": current_time + JWT_EXPIRY_SECONDS

    }

    header_encoded = base64url_encode(

        json.dumps(
            header,
            separators=(",", ":")
        ).encode("utf-8")

    )

    payload_encoded = base64url_encode(

        json.dumps(
            payload,
            separators=(",", ":")
        ).encode("utf-8")

    )

    message = (

        f"{header_encoded}."

        f"{payload_encoded}"

    )

    signature = create_signature(
        message
    )

    return (

        f"{message}."

        f"{signature}"

    )


# ================================================================
# VERIFY JWT
# ================================================================

def verify_jwt(
    token: str
) -> Dict[str, Any]:

    if not isinstance(token, str):

        raise ValueError(
            "JWT token must be a string."
        )

    parts = token.split(".")

    if len(parts) != 3:

        raise ValueError(
            "Invalid JWT format."
        )

    header_part = parts[0]

    payload_part = parts[1]

    received_signature = parts[2]

    message = (

        f"{header_part}."

        f"{payload_part}"

    )

    expected_signature = create_signature(
        message
    )

    if not hmac.compare_digest(

        received_signature,

        expected_signature

    ):

        raise ValueError(
            "Invalid JWT signature."
        )

    try:

        header = json.loads(

            base64url_decode(
                header_part
            )

        )

        payload = json.loads(

            base64url_decode(
                payload_part
            )

        )

    except Exception as error:

        raise ValueError(
            "Invalid JWT payload."
        ) from error

    if header.get("alg") != JWT_ALGORITHM:

        raise ValueError(
            "Unsupported JWT algorithm."
        )

    expiration = int(
        payload.get("exp", 0)
    )

    if expiration <= int(
        time.time()
    ):

        raise ValueError(
            "JWT token has expired."
        )

    return payload


# ================================================================
# PASSWORD HASHING
# ================================================================

def hash_password(
    password: str
) -> str:

    if not isinstance(
        password,
        str
    ):

        raise ValueError(
            "Password must be a string."
        )

    if len(password) < 8:

        raise ValueError(
            "Password must contain at least 8 characters."
        )

    iterations = 310_000

    salt = secrets.token_bytes(
        16
    )

    password_hash = hashlib.pbkdf2_hmac(

        "sha256",

        password.encode("utf-8"),

        salt,

        iterations

    )

    return (

        "pbkdf2_sha256$"

        f"{iterations}$"

        f"{base64url_encode(salt)}$"

        f"{base64url_encode(password_hash)}"

    )


# ================================================================
# PASSWORD VERIFICATION
# ================================================================

def verify_password(
    password: str,

    stored_hash: str

) -> bool:

    try:

        algorithm, iterations, salt, expected_hash = (

            stored_hash.split("$")

        )

        if algorithm != "pbkdf2_sha256":

            return False

        salt_bytes = base64url_decode(
            salt
        )

        expected_bytes = base64url_decode(
            expected_hash
        )

        actual_hash = hashlib.pbkdf2_hmac(

            "sha256",

            password.encode("utf-8"),

            salt_bytes,

            int(iterations)

        )

        return hmac.compare_digest(

            actual_hash,

            expected_bytes

        )

    except Exception:

        return False


# ================================================================
# USER STORAGE
# ================================================================

class UserStore:

    def __init__(
        self,

        file_path: Path = USERS_FILE

    ):

        self.file_path = Path(
            file_path
        )

        self.file_path.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        if not self.file_path.exists():

            self._write_users([])


    # ------------------------------------------------------------
    # READ USERS
    # ------------------------------------------------------------

    def _read_users(self):

        try:

            with self.file_path.open(
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if isinstance(
                data,
                list
            ):

                return data

            return []

        except Exception:

            return []


    # ------------------------------------------------------------
    # WRITE USERS
    # ------------------------------------------------------------

    def _write_users(
        self,

        users
    ):

        temporary_file = (

            self.file_path.with_suffix(
                ".tmp"
            )

        )

        with temporary_file.open(

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                users,

                file,

                indent=2

            )

        temporary_file.replace(
            self.file_path
        )


    # ------------------------------------------------------------
    # FIND BY EMAIL
    # ------------------------------------------------------------

    def get_by_email(
        self,

        email: str

    ) -> Optional[Dict[str, Any]]:

        email = email.strip().lower()

        users = self._read_users()

        for user in users:

            if (

                user.get(
                    "email",
                    ""
                ).lower()

                == email

            ):

                return user

        return None


    # ------------------------------------------------------------
    # FIND BY USER ID
    # ------------------------------------------------------------

    def get_by_id(
        self,

        user_id: str

    ) -> Optional[Dict[str, Any]]:

        users = self._read_users()

        for user in users:

            if (

                user.get(
                    "user_id"
                )

                == user_id

            ):

                return user

        return None


    # ------------------------------------------------------------
    # ADD USER
    # ------------------------------------------------------------

    def add_user(
        self,

        user: Dict[str, Any]

    ):

        users = self._read_users()

        users.append(
            user
        )

        self._write_users(
            users
        )


    # ------------------------------------------------------------
    # UPDATE USER
    # ------------------------------------------------------------

    def update_user(
        self,

        user_id: str,

        updates: Dict[str, Any]

    ):

        users = self._read_users()

        for user in users:

            if user.get(
                "user_id"
            ) == user_id:

                user.update(
                    updates
                )

                self._write_users(
                    users
                )

                return

        raise ValueError(
            "User not found."
        )


# ================================================================
# AUTHENTICATION + AUTHORIZATION ENGINE
# ================================================================

class AuthenticationAuthorizationEngine:

    def __init__(
        self,

        user_store: Optional[
            UserStore
        ] = None

    ):

        self.user_store = (

            user_store

            or UserStore()

        )

        print("=" * 70)

        print(
            "AUTHENTICATION & AUTHORIZATION ENGINE"
        )

        print("=" * 70)

        print(
            "✓ User Login"
        )

        print(
            "✓ Password Hashing"
        )

        print(
            "✓ JWT Authentication"
        )

        print(
            "✓ Role Based Access Control"
        )

        print(
            "✓ Permission Management"
        )

        print(
            "✓ No external API"
        )

        print(
            "✓ No ML model"
        )

        print(
            "✓ No dataset"
        )


    # ============================================================
    # USER REGISTRATION
    # ============================================================

    def register_user(

        self,

        name: str,

        email: str,

        password: str,

        role: str

    ):

        email = email.strip().lower()

        role = role.strip().upper()

        if not name.strip():

            raise ValueError(
                "Name is required."
            )

        if "@" not in email:

            raise ValueError(
                "Valid email is required."
            )

        if role not in ROLE_PERMISSIONS:

            raise ValueError(

                "Invalid role. "

                "Allowed roles: "

                + ", ".join(
                    ROLE_PERMISSIONS.keys()
                )

            )

        if self.user_store.get_by_email(
            email
        ):

            raise ValueError(
                "User already exists."
            )

        user_id = (

            "USR_"

            + secrets.token_hex(
                6
            ).upper()

        )

        user = {

            "user_id": user_id,

            "name": name.strip(),

            "email": email,

            "password_hash":
                hash_password(
                    password
                ),

            "role": role,

            "permissions":
                ROLE_PERMISSIONS[
                    role
                ].copy(),

            "is_active": True,

            "created_at":
                int(time.time())

        }

        self.user_store.add_user(
            user
        )

        return self.public_user(
            user
        )


    # ============================================================
    # USER LOGIN
    # ============================================================

    def login(

        self,

        email: str,

        password: str

    ):

        user = (

            self.user_store
            .get_by_email(
                email
            )

        )

        if not user:

            raise ValueError(
                "Invalid email or password."
            )

        if not user.get(
            "is_active",
            False
        ):

            raise ValueError(
                "User account is inactive."
            )

        if not verify_password(

            password,

            user.get(
                "password_hash",
                ""
            )

        ):

            raise ValueError(
                "Invalid email or password."
            )

        token = create_jwt(
            user
        )

        return {

            "access_token":
                token,

            "token_type":
                "bearer",

            "expires_in":
                JWT_EXPIRY_SECONDS,

            "user":
                self.public_user(
                    user
                )

        }


    # ============================================================
    # AUTHENTICATE USER
    # ============================================================

    def authenticate(

        self,

        token: str

    ):

        payload = verify_jwt(
            token
        )

        user_id = payload.get(
            "sub"
        )

        user = (

            self.user_store
            .get_by_id(
                user_id
            )

        )

        if not user:

            raise ValueError(
                "User does not exist."
            )

        if not user.get(
            "is_active",
            False
        ):

            raise ValueError(
                "User account is inactive."
            )

        return user


    # ============================================================
    # CHECK PERMISSION
    # ============================================================

    def has_permission(

        self,

        user_or_token,

        permission: str

    ) -> bool:

        if isinstance(
            user_or_token,
            str
        ):

            user = self.authenticate(
                user_or_token
            )

        else:

            user = user_or_token

        permissions = user.get(
            "permissions",
            []
        )

        return (

            "*"
            in permissions

            or

            permission
            in permissions

        )


    # ============================================================
    # REQUIRE PERMISSION
    # ============================================================

    def require_permission(

        self,

        user_or_token,

        permission: str

    ):

        if not self.has_permission(

            user_or_token,

            permission

        ):

            raise PermissionError(

                "Permission denied: "

                + permission

            )


    # ============================================================
    # CHECK ROLE
    # ============================================================

    def has_role(

        self,

        user_or_token,

        role: str

    ) -> bool:

        if isinstance(
            user_or_token,
            str
        ):

            user = self.authenticate(
                user_or_token
            )

        else:

            user = user_or_token

        return (

            user.get(
                "role"
            )

            == role.strip().upper()

        )


    # ============================================================
    # REQUIRE ROLE
    # ============================================================

    def require_role(

        self,

        user_or_token,

        role: str

    ):

        if not self.has_role(

            user_or_token,

            role

        ):

            raise PermissionError(

                "Role denied. "

                "Required role: "

                + role.upper()

            )


    # ============================================================
    # ADMIN: DEACTIVATE USER
    # ============================================================

    def deactivate_user(

        self,

        admin_token: str,

        user_id: str

    ):

        admin = self.authenticate(
            admin_token
        )

        if admin["role"] != "ADMIN":

            raise PermissionError(

                "Only ADMIN can "
                "deactivate users."
            )

        self.user_store.update_user(

            user_id,

            {
                "is_active": False
            }

        )


    # ============================================================
    # ADMIN: ACTIVATE USER
    # ============================================================

    def activate_user(

        self,

        admin_token: str,

        user_id: str

    ):

        admin = self.authenticate(
            admin_token
        )

        if admin["role"] != "ADMIN":

            raise PermissionError(

                "Only ADMIN can "
                "activate users."
            )

        self.user_store.update_user(

            user_id,

            {
                "is_active": True
            }

        )


    # ============================================================
    # PUBLIC USER DATA
    # ============================================================

    @staticmethod
    def public_user(
        user
    ):

        return {

            "user_id":
                user["user_id"],

            "name":
                user["name"],

            "email":
                user["email"],

            "role":
                user["role"],

            "permissions":
                user["permissions"],

            "is_active":
                user["is_active"]

        }


# ================================================================
# TEST
# ================================================================

def main():

    print()
    print("=" * 70)

    print(
        "AUTHENTICATION & AUTHORIZATION TEST"
    )

    print("=" * 70)


    # ------------------------------------------------------------
    # TEST STORE
    # ------------------------------------------------------------

    test_file = (

        AUTH_DATA_DIR

        / "auth_test_users.json"

    )

    if test_file.exists():

        test_file.unlink()


    engine = (
        AuthenticationAuthorizationEngine(
            UserStore(test_file)
        )
    )


    # ============================================================
    # 1. REGISTER USERS
    # ============================================================

    print()

    print("=" * 70)

    print(
        "1. USER REGISTRATION"
    )

    print("=" * 70)


    users = [

        (
            "Test Farmer",
            "farmer@test.local",
            "Farmer@123",
            "FARMER"
        ),

        (
            "Test Buyer",
            "buyer@test.local",
            "Buyer@123",
            "BUYER"
        ),

        (
            "Test Logistics",
            "logistics@test.local",
            "Logistics@123",
            "LOGISTICS"
        ),

        (
            "Test Admin",
            "admin@test.local",
            "Admin@123",
            "ADMIN"
        ),

        (
            "Test Support",
            "support@test.local",
            "Support@123",
            "SUPPORT"
        )

    ]


    accounts = {}


    for (

        name,
        email,
        password,
        role

    ) in users:

        accounts[role] = {

            "email":
                email,

            "password":
                password,

            "user":
                engine.register_user(

                    name,

                    email,

                    password,

                    role

                )

        }

        print(
            f"✓ {role:<12} REGISTERED"
        )


    # ============================================================
    # 2. LOGIN
    # ============================================================

    print()

    print("=" * 70)

    print(
        "2. USER LOGIN"
    )

    print("=" * 70)


    login_result = engine.login(

        accounts["FARMER"]["email"],

        accounts["FARMER"]["password"]

    )


    farmer_token = (

        login_result[
            "access_token"
        ]

    )


    print(
        "✓ Farmer login successful"
    )

    print(
        "✓ Token generated"
    )

    print(
        "✓ Token type :",
        login_result[
            "token_type"
        ]
    )


    # ============================================================
    # 3. JWT VERIFICATION
    # ============================================================

    print()

    print("=" * 70)

    print(
        "3. JWT AUTHENTICATION"
    )

    print("=" * 70)


    farmer = engine.authenticate(
        farmer_token
    )


    print(
        "✓ JWT signature verified"
    )

    print(
        "✓ JWT user verified"
    )

    print(
        "✓ User ID :",
        farmer["user_id"]
    )

    print(
        "✓ Role    :",
        farmer["role"]
    )


    # ============================================================
    # 4. ROLE BASED ACCESS
    # ============================================================

    print()

    print("=" * 70)

    print(
        "4. ROLE BASED ACCESS CONTROL"
    )

    print("=" * 70)


    engine.require_role(

        farmer_token,

        "FARMER"

    )


    print(
        "✓ FARMER role accepted"
    )


    try:

        engine.require_role(

            farmer_token,

            "ADMIN"

        )

        raise AssertionError(
            "Farmer incorrectly received ADMIN role."
        )

    except PermissionError:

        print(
            "✓ FARMER correctly denied ADMIN role"
        )


    # ============================================================
    # 5. PERMISSION MANAGEMENT
    # ============================================================

    print()

    print("=" * 70)

    print(
        "5. PERMISSION MANAGEMENT"
    )

    print("=" * 70)


    engine.require_permission(

        farmer_token,

        "crop:create"

    )


    print(
        "✓ FARMER allowed: crop:create"
    )


    try:

        engine.require_permission(

            farmer_token,

            "user:delete"

        )

        raise AssertionError(
            "Unauthorized permission accepted."
        )

    except PermissionError:

        print(
            "✓ FARMER denied: user:delete"
        )


    # ============================================================
    # 6. ADMIN ACCESS
    # ============================================================

    print()

    print("=" * 70)

    print(
        "6. ADMIN AUTHORIZATION"
    )

    print("=" * 70)


    admin_login = engine.login(

        accounts["ADMIN"]["email"],

        accounts["ADMIN"]["password"]

    )


    admin_token = (

        admin_login[
            "access_token"
        ]

    )


    engine.require_permission(

        admin_token,

        "anything:here"

    )


    print(
        "✓ ADMIN wildcard permission accepted"
    )


    # ============================================================
    # 7. INVALID LOGIN
    # ============================================================

    print()

    print("=" * 70)

    print(
        "7. INVALID LOGIN TEST"
    )

    print("=" * 70)


    try:

        engine.login(

            accounts["FARMER"]["email"],

            "WrongPassword"

        )

        raise AssertionError(
            "Invalid password was accepted."
        )

    except ValueError:

        print(
            "✓ Invalid password correctly rejected"
        )


    # ============================================================
    # FINAL STATUS
    # ============================================================

    print()

    print("=" * 70)

    print(
        "AUTHENTICATION & AUTHORIZATION FINAL STATUS"
    )

    print("=" * 70)


    print(
        "✓ User Login              : VERIFIED"
    )

    print(
        "✓ Password Hashing        : VERIFIED"
    )

    print(
        "✓ JWT Authentication     : VERIFIED"
    )

    print(
        "✓ JWT Verification       : VERIFIED"
    )

    print(
        "✓ Role Based Access      : VERIFIED"
    )

    print(
        "✓ Permission Management  : VERIFIED"
    )

    print(
        "✓ Invalid Login Rejection: VERIFIED"
    )

    print()

    print(
        "AUTHENTICATION & "
        "AUTHORIZATION STATUS: COMPLETE"
    )


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":

    main()