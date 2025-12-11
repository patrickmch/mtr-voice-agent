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
        state = sys.get("state", "")
        bedrooms = sys.get("bedrooms", "Unknown")
        rent = sys.get("monthly_rent", "Contact for pricing")

        location = f"{city}, {state}" if city and state else ""
        summaries.append(
            f"The {name} in {location} is a {bedrooms} bedroom for ${rent} per month."
        )

    return " ".join(summaries)


def get_property_details(property_name: str) -> str:
    """Get detailed info about a specific property."""
    p = find_property(property_name)

    if not p:
        # Get available property names for helpful response
        properties = load_properties_from_db()
        available = [prop.get("system", {}).get("nickname", "unknown") for prop in properties]
        return f"I couldn't find a property matching '{property_name}'. We have properties in: {', '.join(available)}."

    sys = p.get("system", {})
    ctx = p.get("context", {})

    # Build response from system data
    name = sys.get("name", "the property")
    address = sys.get("address", "")
    city = sys.get("city", "")
    state = sys.get("state", "")
    city_state = f"{city}, {state}" if city and state else ""

    bedrooms = sys.get("bedrooms", "Unknown")
    bathrooms = sys.get("bathrooms", "Unknown")
    layout = sys.get("layout", "")
    size = sys.get("size_sqft", "")

    rent = sys.get("monthly_rent", "Contact for pricing")
    utilities = "included" if sys.get("utilities_included", "").lower() == "true" else "not included"
    min_stay = sys.get("minimum_stay", "1")
    deposit = sys.get("deposit", "")
    cleaning_fee = sys.get("cleaning_fee", "")
    pet_deposit = sys.get("pet_deposit", "")

    amenities = sys.get("amenities", "")
    pets = sys.get("pets", "Ask about pet policy")
    smoking = sys.get("smoking", "")

    response = f"""The {name} is located at {address} in {city_state}.
It's a {bedrooms} bedroom, {bathrooms} bathroom unit. {layout}
{f'The space is {size} square feet. ' if size else ''}
Monthly rent is ${rent} with utilities {utilities}. Minimum stay is {min_stay} month.
Amenities include: {amenities.replace(',', ', ')}.
Pet policy: {pets}. {f'No smoking allowed.' if smoking == 'Not allowed' else ''}"""

    if deposit:
        response += f" Security deposit is ${deposit} refundable."
    if cleaning_fee:
        response += f" There's a ${cleaning_fee} cleaning fee."
    if pet_deposit:
        response += f" Pet deposit is ${pet_deposit} refundable."

    # Add any user-added context
    if ctx:
        response += "\n\nAdditional information:"
        for key, value in ctx.items():
            formatted_key = key.replace("_", " ").title()
            response += f"\n{formatted_key}: {value}"

    return response


def check_availability(property_name: str, move_in: str, move_out: str) -> str:
    """Check if property works for given dates."""
    p = find_property(property_name)

    if not p:
        return "I couldn't find that property. Would you like to hear about what we have available?"

    sys = p.get("system", {})
    min_stay = sys.get("minimum_stay", "1")
    name = sys.get("name", "the property")

    return f"""The {name} has a minimum stay of {min_stay} month.
For your dates of {move_in} to {move_out}, availability changes regularly based on bookings.
I'd recommend submitting an application so we can confirm exact availability for your dates.
Would you like information on how to apply?"""
