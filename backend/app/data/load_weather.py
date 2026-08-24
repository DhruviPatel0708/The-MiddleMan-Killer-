import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in .env")

if not MONGODB_DATABASE:
    raise ValueError("MONGODB_DATABASE is not set in .env")


def load_weather_data():

    print("=" * 70)
    print("LOADING WEATHER DATA FROM MONGODB ATLAS")
    print("=" * 70)

    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)

    # Select database
    db = client[MONGODB_DATABASE]

    # Test connection
    client.admin.command("ping")

    print(f"Python connected database: {db.name}")

    # Show collections
    print("\nAvailable collections:")
    collections = db.list_collection_names()

    for collection_name in collections:
        print(f"  - {collection_name}")

    # Select weather collection
    collection = db["weather"]

    # Count documents
    document_count = collection.count_documents({})

    print("\n" + "-" * 70)
    print(f"Weather collection document count: {document_count}")
    print("-" * 70)

    if document_count == 0:
        raise ValueError("Weather collection exists but contains no documents.")

    # Load weather documents
    documents = list(collection.find({}))

    # Convert to DataFrame
    weather_df = pd.DataFrame(documents)

    # Remove MongoDB internal ID
    if "_id" in weather_df.columns:
        weather_df = weather_df.drop(columns=["_id"])

    print("\nWeather data loaded successfully!")
    print(f"Rows    : {weather_df.shape[0]}")
    print(f"Columns : {weather_df.shape[1]}")

    print("\nWeather columns:")
    for column in weather_df.columns:
        print(f"  - {column}")

    print("\nFirst 5 records:")
    print(weather_df.head())

    print("\n" + "=" * 70)

    client.close()

    return weather_df


if __name__ == "__main__":
    weather_df = load_weather_data()