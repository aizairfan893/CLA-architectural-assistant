import re


ROOM_KEYWORDS = {
    "bedroom":      ["bed", "bedroom", "bedrooms"],
    "kitchen":      ["kitchen", "kitchens"],
    "living_room":  ["living", "lounge", "drawing", "sitting"],
    "washroom":     ["washroom", "bathroom", "toilet", "washrooms"],
    "dining_room":  ["dining"],
    "store_room":   ["store", "storage"],
    "garage":       ["garage", "car porch", "parking"],
    "study_room":   ["study"],
    "prayer_room":  ["prayer", "namaz", "musalla"],
    "guest_room":   ["guest"],
    "servant_room": ["servant", "maid"],
    "terrace":      ["terrace", "balcony"],
    "lawn":         ["lawn", "garden"],
}

ROOM_TYPE_MAP = {
    "bedroom": "private",
    "guest_room": "private",
    "servant_room": "private",
    "study_room": "private",
    "kitchen": "service",
    "washroom": "service",
    "store_room": "service",
    "garage": "service",
    "living_room": "public",
    "dining_room": "public",
    "prayer_room": "public",
    "terrace": "public",
    "lawn": "public",
}


def parse_requirements(text):
    text = text.lower()
    requirements = {}
    rooms = {}

    for room_key, keywords in ROOM_KEYWORDS.items():
        count = None
        for kw in keywords:
            pattern1 = rf'(\d+)\s*(?:op\s*)?{re.escape(kw)}s?\b'
            match1 = re.search(pattern1, text)
            pattern2 = rf'{re.escape(kw)}s?\s*(\d+)'
            match2 = re.search(pattern2, text)
            if match1:
                count = int(match1.group(1))
                break
            elif match2:
                count = int(match2.group(1))
                break
        if count is not None:
            rooms[room_key] = count

    all_keywords_flat = [kw for kws in ROOM_KEYWORDS.values() for kw in kws]
    generic_matches = re.findall(r'(\d+)\s*([a-z]+)\s*room', text)
    for num, word in generic_matches:
        candidate_key = f"{word}_room"
        already_known = any(
            word == kw or (word + "room") == kw or kw.startswith(word)
            for kw in all_keywords_flat
        )
        if not already_known and candidate_key not in rooms:
            rooms[candidate_key] = int(num)
            ROOM_TYPE_MAP.setdefault(candidate_key, "public")

    rooms.setdefault("bedroom", rooms.get("bedroom", 2))
    rooms.setdefault("kitchen", rooms.get("kitchen", 1))
    rooms.setdefault("living_room", rooms.get("living_room", 1))
    rooms.setdefault("washroom", rooms.get("washroom", 1))

    requirements["rooms"] = rooms
    requirements["bedrooms"] = rooms.get("bedroom", 2)

    plot_match = re.search(r'plot\s*size\s*(\d+)', text)
    plot_match2 = re.search(r'(\d+)\s*marla', text)
    if plot_match:
        requirements["plot_size"] = int(plot_match.group(1))
    elif plot_match2:
        requirements["plot_size"] = int(plot_match2.group(1))
    else:
        requirements["plot_size"] = 5

    if "double" in text:
        requirements["floors"] = "Double Storey"
    elif "triple" in text:
        requirements["floors"] = "Triple Storey"
    elif "single" in text:
        requirements["floors"] = "Single Storey"
    else:
        requirements["floors"] = "Single Storey"

    if "low" in text:
        requirements["budget"] = "low"
    elif "high" in text:
        requirements["budget"] = "high"
    else:
        requirements["budget"] = "medium"

    if "modern" in text:
        requirements["style"] = "modern"
    elif "luxury" in text:
        requirements["style"] = "luxury"
    else:
        requirements["style"] = "simple"

    return requirements