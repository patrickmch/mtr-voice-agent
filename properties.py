PROPERTIES = [
    {
        "id": "downtown-studio",
        "name": "Downtown Boulder Studio",
        "type": "studio",
        "bedrooms": 0,
        "bathrooms": 1,
        "rent": 1800,
        "available_from": "January 15th",
        "available_until": "June 30th",
        "min_stay": 1,
        "max_stay": 11,
        "amenities": ["WiFi", "washer/dryer", "parking", "gym access"],
        "pets": "cats only",
        "utilities_included": True,
        "description": "Bright, modern studio in the heart of downtown Boulder. Walking distance to Pearl Street Mall."
    },
    {
        "id": "north-2br",
        "name": "North Boulder 2-Bedroom",
        "type": "2-bedroom",
        "bedrooms": 2,
        "bathrooms": 1,
        "rent": 2600,
        "available_from": "February 1st",
        "available_until": "August 31st",
        "min_stay": 2,
        "max_stay": 11,
        "amenities": ["WiFi", "washer/dryer", "parking", "balcony", "mountain views"],
        "pets": "dogs and cats welcome",
        "utilities_included": False,
        "description": "Spacious 2-bedroom with stunning Flatiron views. Quiet neighborhood, perfect for remote workers."
    }
]


def get_all_properties():
    """Return summary of all available properties."""
    summaries = []
    for p in PROPERTIES:
        bed_desc = "studio" if p["bedrooms"] == 0 else f"{p['bedrooms']}-bedroom"
        summaries.append(f"The {p['name']} is a {bed_desc} for ${p['rent']}/month, available {p['available_from']} through {p['available_until']}.")
    return " ".join(summaries)


def get_property_details(property_name: str):
    """Get detailed info about a specific property."""
    name_lower = property_name.lower()
    
    for p in PROPERTIES:
        if name_lower in p["name"].lower() or name_lower == p["type"]:
            amenities = ", ".join(p["amenities"])
            utilities = "included" if p["utilities_included"] else "not included"
            
            return f"""The {p['name']} is a {p['type']} at ${p['rent']} per month.
            It has {p['bathrooms']} bathroom and is available from {p['available_from']} through {p['available_until']}.
            Minimum stay is {p['min_stay']} month, maximum {p['max_stay']} months.
            Amenities include: {amenities}.
            Pet policy: {p['pets']}.
            Utilities are {utilities}.
            {p['description']}"""
    
    return f"I couldn't find a property matching '{property_name}'. We have a downtown studio and a North Boulder 2-bedroom available."


def check_availability(property_name: str, move_in: str, move_out: str):
    """Check if property works for given dates."""
    name_lower = property_name.lower()
    
    for p in PROPERTIES:
        if name_lower in p["name"].lower() or name_lower == p["type"]:
            return f"The {p['name']} is available from {p['available_from']} through {p['available_until']}. Your dates of {move_in} to {move_out} would need to fall within that window. Does that work for you?"
    
    return "I couldn't find that property. Would you like to hear about what we have available?"
