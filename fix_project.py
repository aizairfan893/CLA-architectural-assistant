parser_code = '''import re


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
            pattern1 = rf"(\\\\d+)\\\\s*(?:op\\\\s*)?{re.escape(kw)}s?\\\\b"
            match1 = re.search(pattern1, text)
            pattern2 = rf"{re.escape(kw)}s?\\\\s*(\\\\d+)"
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
    generic_matches = re.findall(r"(\\\\d+)\\\\s*([a-z]+)\\\\s*room", text)
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

    plot_match = re.search(r"plot\\\\s*size\\\\s*(\\\\d+)", text)
    plot_match2 = re.search(r"(\\\\d+)\\\\s*marla", text)
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
'''

layout_code = '''from nlp.parser import ROOM_TYPE_MAP

MAX_COLS_PER_ROW = 4


def _flatten_instances(rooms_needed):
    instances = []
    for room_key, count in rooms_needed.items():
        if count <= 0:
            continue
        display_name = room_key.replace("_", " ").title()
        for i in range(count):
            name = f"{display_name} {i+1}" if count > 1 else display_name
            instances.append((room_key, name))
    return instances


def _place_grid(instances, w, h, y_start):
    placed = []
    x_cursor = 0
    y_cursor = y_start
    col = 0

    for room_key, name in instances:
        room_type = ROOM_TYPE_MAP.get(room_key, "public")
        placed.append({
            "name": name,
            "width": w,
            "height": h,
            "x": x_cursor,
            "y": y_cursor,
            "type": room_type
        })
        col += 1
        x_cursor += w
        if col >= MAX_COLS_PER_ROW:
            col = 0
            x_cursor = 0
            y_cursor += h

    if col != 0:
        y_cursor += h

    return placed, y_cursor


def generate_rooms(requirements, layout_type="Balanced Comfort"):
    rooms_needed = requirements.get("rooms", {})
    if not rooms_needed:
        rooms_needed = {"bedroom": 2, "kitchen": 1, "living_room": 1, "washroom": 1}

    if layout_type == "Luxury Modern":
        base_w, base_h = 4, 4
        scale = 1.2
    elif layout_type == "Balanced Comfort":
        base_w, base_h = 3.5, 3.5
        scale = 1.0
    else:
        base_w, base_h = 3, 3
        scale = 0.85

    SIZE_MULTIPLIER = {"private": 1.0, "service": 0.6, "public": 1.3}

    private_rooms, public_rooms, service_rooms = {}, {}, {}
    for room_key, count in rooms_needed.items():
        room_type = ROOM_TYPE_MAP.get(room_key, "public")
        if room_type == "private":
            private_rooms[room_key] = count
        elif room_type == "service":
            service_rooms[room_key] = count
        else:
            public_rooms[room_key] = count

    all_rooms = []
    y_cursor = 0

    for section, mult_key in [
        (private_rooms, "private"),
        (public_rooms, "public"),
        (service_rooms, "service"),
    ]:
        if not section:
            continue
        w = round(base_w * scale * SIZE_MULTIPLIER[mult_key], 2)
        h = round(base_h * scale * SIZE_MULTIPLIER[mult_key], 2)
        instances = _flatten_instances(section)
        placed, y_cursor = _place_grid(instances, w, h, y_cursor)
        all_rooms.extend(placed)

    return all_rooms
'''

with open("nlp/parser.py", "w", encoding="utf-8") as f:
    f.write(parser_code)

with open("engine/layout_planner.py", "w", encoding="utf-8") as f:
    f.write(layout_code)

print("DONE - Both files written successfully!")