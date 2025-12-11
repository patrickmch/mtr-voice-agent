"""
Dynamic property loading from Midway PostgreSQL database.
All property data is stored in the PropertyContext table as key-value pairs.

System keys (property metadata) are prefixed with underscore: _name, _monthly_rent, etc.
User-added context has no prefix: pet_policy, wifi_info, etc.
"""

import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Database URL for Midway PostgreSQL
DATABASE_URL = os.getenv("MIDWAY_DATABASE_URL")

# Cache for properties (refreshed on each call for now)
_properties_cache: list[dict] = []


def get_db_connection():
    """Get PostgreSQL connection."""
    if not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def load_properties_from_db() -> list[dict]:
    """
    Load all properties from PropertyContext table.
    Groups entries by propertyId and separates system keys from user context.
    """
    conn = get_db_connection()
    if not conn:
        print("Warning: Could not connect to database")
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get all property context entries
            cur.execute('SELECT "propertyId", key, value FROM "PropertyContext" ORDER BY "propertyId"')
            rows = cur.fetchall()
        conn.close()

        # Group by propertyId
        properties_map: dict[str, dict] = {}

        for row in rows:
            prop_id = row["propertyId"]
            key = row["key"]
            value = row["value"]

            if prop_id not in properties_map:
                properties_map[prop_id] = {
                    "id": prop_id,
                    "system": {},  # Keys starting with _
                    "context": {},  # User-added context
                }

            if key.startswith("_"):
                # System key - store without underscore prefix for easier access
                clean_key = key[1:]  # Remove leading underscore
                properties_map[prop_id]["system"][clean_key] = value
            else:
                # User-added context
                properties_map[prop_id]["context"][key] = value

        return list(properties_map.values())

    except Exception as e:
        print(f"Error loading properties from database: {e}")
        if conn:
            conn.close()
        return []


def find_property(query: str) -> Optional[dict]:
    """Find a property by name, city, nickname, or bedroom count."""
    properties = load_properties_from_db()
    query_lower = query.lower()

    for p in properties:
        sys = p.get("system", {})

        # Match by nickname
        nickname = sys.get("nickname", "").lower()
        if query_lower == nickname:
            return p

        # Match by city
        city = sys.get("city", "").lower()
        if city and (query_lower in city or city in query_lower):
            return p

        # Match by name
        name = sys.get("name", "").lower()
        if name and query_lower in name:
            return p

        # Match by bedroom count
        bedrooms = sys.get("bedrooms", "").lower()
        if bedrooms and (query_lower in bedrooms or bedrooms in query_lower):
            return p

        # Match common terms
        if "studio" in query_lower and bedrooms == "studio":
            return p
        if ("1" in query_lower or "one" in query_lower) and bedrooms == "1":
            return p

    return None


def get_all_properties() -> str:
    """Return summary of all available properties."""
    properties = load_properties_from_db()

    if not properties:
        return "I'm sorry, I couldn't load property information right now. Please try again later."

    summaries = []
    for p in properties:
        sys = p.get("system", {})
        name = sys.get("name", "Unknown Property")
        city = sys.get("city", "")
        bedrooms = sys.get("bedrooms", "Unknown")
        rent = sys.get("monthly_rent", "Contact for pricing")
        available_from = sys.get("available_from", "")

        avail_text = f", available {available_from.lower()}" if available_from else ""
        summaries.append(
            f"{bedrooms} bedroom in {city} for ${rent}/month{avail_text}"
        )

    return ". ".join(summaries) + "."


def get_property_details(property_name: str) -> str:
    """Get detailed info about a specific property."""
    p = find_property(property_name)

    if not p:
        properties = load_properties_from_db()
        available = [prop.get("system", {}).get("city", "unknown") for prop in properties]
        return f"I don't have a property matching that. We have places in {', '.join(available)}."

    sys = p.get("system", {})

    city = sys.get("city", "")
    bedrooms = sys.get("bedrooms", "")
    bathrooms = sys.get("bathrooms", "")
    rent = sys.get("monthly_rent", "")
    utilities = "utilities included" if sys.get("utilities_included", "").lower() == "true" else ""
    available_from = sys.get("available_from", "")
    pets = sys.get("pets", "")
    deposit = sys.get("deposit", "")

    parts = []
    parts.append(f"{bedrooms} bed, {bathrooms} bath in {city}")
    parts.append(f"${rent} a month{', ' + utilities if utilities else ''}")
    if available_from:
        parts.append(f"available {available_from.lower()}")
    if pets:
        parts.append(f"pets: {pets.lower()}")
    if deposit:
        parts.append(f"${deposit} deposit")

    return ". ".join(parts) + "."


def check_availability(property_name: str, move_in: str, move_out: str) -> str:
    """Check if property works for given dates."""
    p = find_property(property_name)

    if not p:
        return "I couldn't find that property."

    sys = p.get("system", {})
    name = sys.get("name", "the property")
    available_from = sys.get("available_from", "unknown")
    available_until = sys.get("available_until", "open ended")
    min_stay = sys.get("minimum_stay", "1")

    return f"{name} is available from {available_from}. Minimum stay is {min_stay} month. Your dates: {move_in} to {move_out}."
