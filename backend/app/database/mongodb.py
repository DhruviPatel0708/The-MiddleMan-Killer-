import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")


if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the .env file")

if not MONGODB_DATABASE:
    raise ValueError("MONGODB_DATABASE is not set in the .env file")


client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]


def test_connection():
    try:
        client.admin.command("ping")

        print("=" * 70)
        print("MONGODB ATLAS CONNECTION")
        print("=" * 70)
        print("✓ MongoDB Atlas connection successful")
        print(f"✓ Database: {MONGODB_DATABASE}")
        print("=" * 70)

        return True

    except ConnectionFailure as error:
        print("✗ MongoDB connection failed")
        print(error)

        return False


if __name__ == "__main__":
    test_connection()