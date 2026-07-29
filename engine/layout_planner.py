import random


class RoomRequest:
    def __init__(self, key, name, width, height, room_type, adjacent_to=None):
        self.key = key
        self.name = name
        self.width = float(width)
        self.height = float(height)
        self.type = room_type
        self.adjacent_to = list(adjacent_to) if adjacent_to else []

    @property
    def area(self):
        return round(self.width * self.height, 2)

    def __repr__(self):
        return f"RoomRequest({self.key}, {self.width}x{self.height}, adj={self.adjacent_to})"


GAP = 0.5


def _rooms_overlap(a, b, gap=GAP):
    return not (
        a["x"] + a["w"] + gap <= b["x"] or
        b["x"] + b["w"] + gap <= a["x"] or
        a["y"] + a["h"] + gap <= b["y"] or
        b["y"] + b["h"] + gap <= a["y"]
    )

def _has_collision(candidate, placed):
    for other in placed.values():
        if _rooms_overlap(candidate, other):
            return True
    return False

def _candidate_slots_beside(target, w, h):
    return [
        {"x": target["x"] + target["w"] + GAP, "y": target["y"], "w": w, "h": h},
        {"x": target["x"], "y": target["y"] + target["h"] + GAP, "w": w, "h": h},
        {"x": target["x"] - w - GAP, "y": target["y"], "w": w, "h": h},
        {"x": target["x"], "y": target["y"] - h - GAP, "w": w, "h": h},
    ]


def place_rooms_with_adjacency(rooms, seed=0):
    rng = random.Random(seed)
    order = list(rooms)
    rng.shuffle(order)

    placed = {}
    anchors = [r for r in order if not r.adjacent_to]
    dependents = [r for r in order if r.adjacent_to]

    if not anchors:
        anchors, dependents = [order[0]], order[1:]

    first = anchors[0]
    placed[first.key] = {"x": 0.0, "y": 0.0, "w": first.width, "h": first.height}

    queue = dependents + anchors[1:]

    for _ in range(3):
        still_pending = []
        for room in queue:
            if room.key in placed:
                continue
            target_key = next((k for k in room.adjacent_to if k in placed), None)
            if target_key is None:
                still_pending.append(room)
                continue

            target = placed[target_key]
            slots = _candidate_slots_beside(target, room.width, room.height)
            rng.shuffle(slots)
            placed_ok = False
            for slot in slots:
                if slot["x"] >= -50 and slot["y"] >= -50 and not _has_collision(slot, placed):
                    placed[room.key] = slot
                    placed_ok = True
                    break
            if not placed_ok:
                still_pending.append(room)
        queue = still_pending

    unresolved = queue

    if placed:
        max_y = max(v["y"] + v["h"] for v in placed.values())
    else:
        max_y = 0
    x_cursor, y_row = 0.0, max_y + GAP

    for room in unresolved:
        candidate = {"x": x_cursor, "y": y_row, "w": room.width, "h": room.height}
        placed[room.key] = candidate
        x_cursor += room.width + GAP

    return placed


def generate_variations(rooms, count=3, attempts_multiplier=4):
    variations = []
    for seed in range(count * attempts_multiplier):
        placed = place_rooms_with_adjacency(rooms, seed=seed)
        variations.append(placed)
    return variations