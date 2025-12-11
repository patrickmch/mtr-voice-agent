#!/usr/bin/env python3
"""
Seed script to populate PropertyContext table with property data.
Run once to migrate from hardcoded properties to database.

Usage: python seed_properties.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("MIDWAY_DATABASE_URL")
# Owner user ID from Midway config
USER_ID = "user_361g0w0bgM843cVdiNG4ZyL6Z1p"

# Property data to seed (using underscore prefix for system keys)
PROPERTIES_TO_SEED = [
    {
        "propertyId": "725012_1",
        "data": {
            "_name": "Beautiful Centrally Located 1 Bdrm Monthly Rental",
            "_nickname": "boulder",
            "_address": "2610 Iris Avenue, Apt 107",
            "_city": "Boulder",
            "_state": "Colorado",
            "_bedrooms": "1",
            "_bathrooms": "1",
            "_layout": "One bedroom apartment, fully furnished",
            "_monthly_rent": "2200",
            "_utilities_included": "true",
            "_minimum_stay": "1",
            "_amenities": "Full kitchen,Washer/dryer in unit,WiFi included,Free parking,Air conditioning,Heating",
            "_pets": "Allowed (pet deposit required)",
            "_smoking": "Not allowed",
            "_available_from": "January 15, 2025",
            "_available_until": "Open ended",
        }
    },
    {
        "propertyId": "433442_1",
        "data": {
            "_name": "Blue Door Studio Downtown Lander Loft",
            "_nickname": "lander",
            "_address": "744 Lincoln Street",
            "_city": "Lander",
            "_state": "Wyoming",
            "_bedrooms": "Studio",
            "_bathrooms": "1",
            "_size_sqft": "800",
            "_beds": "1 Queen Bed",
            "_layout": "Open concept craftsman loft with high ceilings and bohemian modern furniture",
            "_monthly_rent": "1200",
            "_utilities_included": "true",
            "_cleaning_fee": "100",
            "_deposit": "1000",
            "_pet_deposit": "400",
            "_minimum_stay": "1",
            "_amenities": "Full kitchen with essentials,Washer/dryer in unit,WiFi included,Samsung Smart TV,Free parking on premises,Gym access,Air conditioning,Heating,Professional cleaning",
            "_pets": "Allowed ($400 refundable pet deposit)",
            "_smoking": "Not allowed",
            "_accessibility": "Stairs at entrance",
            "_available_from": "Available now",
            "_available_until": "Open ended",
        }
    }
]


def seed_properties():
    """Insert property data into PropertyContext table."""
    if not DATABASE_URL:
        print("Error: MIDWAY_DATABASE_URL not set in .env")
        return False

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        total_inserted = 0
        total_updated = 0

        for prop in PROPERTIES_TO_SEED:
            property_id = prop["propertyId"]
            print(f"\nSeeding property: {property_id}")

            for key, value in prop["data"].items():
                # Upsert: insert or update on conflict
                cur.execute('''
                    INSERT INTO "PropertyContext" ("id", "propertyId", "key", "value", "userId", "createdAt", "updatedAt")
                    VALUES (gen_random_uuid()::text, %s, %s, %s, %s, NOW(), NOW())
                    ON CONFLICT ("propertyId", "key")
                    DO UPDATE SET "value" = EXCLUDED."value", "updatedAt" = NOW()
                    RETURNING (xmax = 0) AS inserted
                ''', (property_id, key, value, USER_ID))

                result = cur.fetchone()
                if result and result[0]:
                    total_inserted += 1
                    print(f"  + Inserted: {key}")
                else:
                    total_updated += 1
                    print(f"  ~ Updated: {key}")

        conn.commit()
        cur.close()
        conn.close()

        print(f"\n✅ Seed complete!")
        print(f"   Inserted: {total_inserted} new entries")
        print(f"   Updated: {total_updated} existing entries")
        return True

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False


if __name__ == "__main__":
    seed_properties()
