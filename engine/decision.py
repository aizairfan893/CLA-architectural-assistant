def _touching(a, b, tolerance=0.6):
    horizontally_touching = (
        abs((a["x"] + a["w"]) - b["x"]) < tolerance or
        abs((b["x"] + b["w"]) - a["x"]) < tolerance
    )
    vertically_overlapping = a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]

    vertically_touching = (
        abs((a["y"] + a["h"]) - b["y"]) < tolerance or
        abs((b["y"] + b["h"]) - a["y"]) < tolerance
    )
    horizontally_overlapping = a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]

    return (horizontally_touching and vertically_overlapping) or (vertically_touching and horizontally_overlapping)


def score_variation(rooms, placed):
    score = 0
    total_checks = 0

    for room in rooms:
        for adj_key in room.adjacent_to:
            if room.key not in placed or adj_key not in placed:
                continue
            total_checks += 1
            if _touching(placed[room.key], placed[adj_key]):
                score += 10
            else:
                score -= 3

    if placed:
        min_x = min(v["x"] for v in placed.values())
        min_y = min(v["y"] for v in placed.values())
        max_x = max(v["x"] + v["w"] for v in placed.values())
        max_y = max(v["y"] + v["h"] for v in placed.values())
        bounding_area = (max_x - min_x) * (max_y - min_y)
        room_area = sum(v["w"] * v["h"] for v in placed.values())
        if bounding_area > 0:
            efficiency = room_area / bounding_area
            score += efficiency * 15

    return round(score, 2), total_checks


def get_best_layouts(rooms, variations, count=3):
    scored = []
    seen_signatures = set()

    for placed in variations:
        s, checks = score_variation(rooms, placed)
        signature = tuple(sorted((k, round(v["x"], 1), round(v["y"], 1)) for k, v in placed.items()))
        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)
        scored.append((s, placed))

    scored.sort(key=lambda x: -x[0])
    return scored[:count]