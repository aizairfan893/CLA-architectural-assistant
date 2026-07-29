import math
import plotly.graph_objects as go


def rooms_to_render_list(rooms, placed):
    render_list = []
    for room in rooms:
        if room.key not in placed:
            continue
        pos = placed[room.key]
        render_list.append({
            "name": room.name,
            "x": pos["x"],
            "y": pos["y"],
            "width": pos["w"],
            "height": pos["h"],
            "type": room.type,
        })
    return render_list


def draw_2d_floorplan(render_rooms, unit="feet"):
    fig = go.Figure()

    type_colors = {
        "private": "#9F224C",
        "public": "#DC357D",
        "service": "#E85151",
    }

    if not render_rooms:
        fig.update_layout(title="No rooms to display")
        return fig

    max_x = max(r["x"] + r["width"] for r in render_rooms)
    max_y = max(r["y"] + r["height"] for r in render_rooms)

    for room in render_rooms:
        x0, y0 = room["x"], room["y"]
        width, height = room["width"], room["height"]
        rtype = room["type"]
        name = room["name"]
        area = round(width * height, 2)

        fig.add_shape(
            type="rect",
            x0=x0, y0=y0, x1=x0 + width, y1=y0 + height,
            line=dict(color="black", width=1.5),
            fillcolor=type_colors.get(rtype, "#87CEFA"),
            layer="below",
        )

        smaller_side = min(width, height)
        font_size = max(7, min(15, int(smaller_side * 2.2)))

        if smaller_side >= 6:
            label = name
        else:
            words = name.split()
            label = next((w for w in reversed(words) if not w.isdigit()), words[-1])

        fig.add_trace(go.Scatter(
            x=[x0 + width / 2],
            y=[y0 + height / 2],
            text=label,
            mode="text",
            showlegend=False,
            textfont=dict(color="black", size=font_size),
            hovertemplate=(
                f"Name: {name}<br>"
                f"Width: {width} {unit}<br>"
                f"Height: {height} {unit}<br>"
                f"Area: {area} {unit}²<br>"
                f"Type: {rtype}<extra></extra>"
            ),
        ))

    fig.update_layout(
        title="🗺️ Floor Plan (real sizes as entered)",
        xaxis=dict(visible=False, range=[-1, max_x + 1]),
        yaxis=dict(visible=False, scaleanchor="x", range=[-1, max_y + 1]),
        height=max(450, min(850, int(max_y * 12))),
        plot_bgcolor="#f8f8f8",
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return fig


# ----------------------------------------------------------------
# Doors, Entrance, Corridor — real architecture symbols add karta hai
# ----------------------------------------------------------------

def _find_touching_edge(a, b, tolerance=0.6):
    """Do rooms (dict with x,y,w,h) ke beech shared wall dhoondta hai"""
    if abs((a["x"] + a["w"]) - b["x"]) < tolerance and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
        oy1, oy2 = max(a["y"], b["y"]), min(a["y"] + a["h"], b["y"] + b["h"])
        return {"axis": "v", "pos": a["x"] + a["w"], "from": oy1, "to": oy2, "swing": 1}
    if abs((b["x"] + b["w"]) - a["x"]) < tolerance and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]:
        oy1, oy2 = max(a["y"], b["y"]), min(a["y"] + a["h"], b["y"] + b["h"])
        return {"axis": "v", "pos": a["x"], "from": oy1, "to": oy2, "swing": -1}
    if abs((a["y"] + a["h"]) - b["y"]) < tolerance and a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]:
        ox1, ox2 = max(a["x"], b["x"]), min(a["x"] + a["w"], b["x"] + b["w"])
        return {"axis": "h", "pos": a["y"] + a["h"], "from": ox1, "to": ox2, "swing": 1}
    if abs((b["y"] + b["h"]) - a["y"]) < tolerance and a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]:
        ox1, ox2 = max(a["x"], b["x"]), min(a["x"] + a["w"], b["x"] + b["w"])
        return {"axis": "h", "pos": a["y"], "from": ox1, "to": ox2, "swing": -1}
    return None


def _door_swing_path(x1, y1, x2, y2, swing_dir):
    """Door symbol: hinge line + curved swing path (Bezier curve, kyunke Plotly arc support nahi karta)"""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return None, None
    ux, uy = dx / length, dy / length
    nx, ny = -uy * swing_dir, ux * swing_dir
    arc_x, arc_y = x1 + nx * length, y1 + ny * length

    leaf = f"M {x1},{y1} L {arc_x},{arc_y}"

    if abs(x1 - x2) < 1e-6:
        corner_x, corner_y = arc_x, y2
    else:
        corner_x, corner_y = x2, arc_y

    curve = f"M {x2},{y2} Q {corner_x},{corner_y} {arc_x},{arc_y}"
    return leaf, curve


def add_doors_to_figure(fig, room_list, door_width=4.0):
    """
    room_list: rooms_to_render_list() se aayi hui list (name, x, y, width, height, type)
    Har do touching rooms ke beech ek door symbol (gap + swing arc) daalta hai
    """
    for i in range(len(room_list)):
        for j in range(i + 1, len(room_list)):
            a = {"x": room_list[i]["x"], "y": room_list[i]["y"],
                 "w": room_list[i]["width"], "h": room_list[i]["height"]}
            b = {"x": room_list[j]["x"], "y": room_list[j]["y"],
                 "w": room_list[j]["width"], "h": room_list[j]["height"]}

            edge = _find_touching_edge(a, b)
            if not edge:
                continue

            mid = (edge["from"] + edge["to"]) / 2
            half_door = door_width / 2

            if edge["axis"] == "v":
                px = edge["pos"]
                py1, py2 = mid - half_door, mid + half_door

                fig.add_shape(
                    type="rect",
                    x0=px - 0.05, x1=px + 0.05, y0=py1, y1=py2,
                    fillcolor="#f8f8f8", line=dict(width=0), layer="above"
                )
                leaf, arc = _door_swing_path(px, py1, px, py2, edge["swing"])
            else:
                py = edge["pos"]
                px1, px2 = mid - half_door, mid + half_door

                fig.add_shape(
                    type="rect",
                    x0=px1, x1=px2, y0=py - 0.05, y1=py + 0.05,
                    fillcolor="#f8f8f8", line=dict(width=0), layer="above"
                )
                leaf, arc = _door_swing_path(px1, py, px2, py, edge["swing"])

            if leaf and arc:
                fig.add_shape(type="path", path=leaf, line=dict(color="#2b2b2b", width=2.5), layer="above")
                fig.add_shape(type="path", path=arc, line=dict(color="#666666", width=1.5, dash="dash"), layer="above")

    return fig


def add_entrance_marker(fig, entrance_room, room_list, door_width=4.0, label="Main Entrance"):
    """
    entrance_room ki 4 deewaron (upar, neechay, left, right) mein se
    check karta hai kaunsi deewar khaali hai (kisi room se nahi judi),
    aur sirf usi khaali deewar pe entrance lagata hai.
    """
    if not entrance_room:
        return fig

    ex0, ey0 = entrance_room["x"], entrance_room["y"]
    ew, eh = entrance_room["width"], entrance_room["height"]

    def side_is_empty(side_name):
        for r in room_list:
            if r["name"] == entrance_room["name"]:
                continue
            rx0, ry0, rw, rh = r["x"], r["y"], r["width"], r["height"]

            if side_name == "bottom":
                if abs((ry0 + rh) - ey0) < 0.6 and rx0 < ex0 + ew and rx0 + rw > ex0:
                    return False
            elif side_name == "top":
                if abs(ry0 - (ey0 + eh)) < 0.6 and rx0 < ex0 + ew and rx0 + rw > ex0:
                    return False
            elif side_name == "left":
                if abs((rx0 + rw) - ex0) < 0.6 and ry0 < ey0 + eh and ry0 + rh > ey0:
                    return False
            elif side_name == "right":
                if abs(rx0 - (ex0 + ew)) < 0.6 and ry0 < ey0 + eh and ry0 + rh > ey0:
                    return False
        return True

    chosen_side = None
    for side_name in ["bottom", "top", "left", "right"]:
        if side_is_empty(side_name):
            chosen_side = side_name
            break

    if chosen_side is None:
        return fig

    if chosen_side == "bottom":
        ex, ey = ex0 + ew * 0.15, ey0
        swing_dir = 1
    elif chosen_side == "top":
        ex, ey = ex0 + ew * 0.15, ey0 + eh
        swing_dir = -1
    elif chosen_side == "left":
        ex, ey = ex0, ey0 + eh * 0.15
        swing_dir = 1
    else:
        ex, ey = ex0 + ew, ey0 + eh * 0.15
        swing_dir = -1

    if chosen_side in ("bottom", "top"):
        fig.add_shape(
            type="rect",
            x0=ex, x1=ex + door_width, y0=ey - 0.05, y1=ey + 0.05,
            fillcolor="#f8f8f8", line=dict(width=0), layer="above"
        )
        leaf, curve = _door_swing_path(ex, ey, ex + door_width, ey, swing_dir)
        label_x, label_y = ex, (ey - 1.2 if chosen_side == "bottom" else ey + 1.5)
    else:
        fig.add_shape(
            type="rect",
            x0=ex - 0.05, x1=ex + 0.05, y0=ey, y1=ey + door_width,
            fillcolor="#f8f8f8", line=dict(width=0), layer="above"
        )
        leaf, curve = _door_swing_path(ex, ey, ex, ey + door_width, swing_dir)
        label_x, label_y = ex + (1.5 if chosen_side == "left" else -3.5), ey

    if leaf and curve:
        fig.add_shape(type="path", path=leaf, line=dict(color="#1a1a1a", width=3), layer="above")
        fig.add_shape(type="path", path=curve, line=dict(color="#555555", width=1.5, dash="dash"), layer="above")

    fig.add_annotation(
        x=label_x, y=label_y,
        text=label,
        showarrow=False,
        font=dict(size=11, color="#333333"),
    )
    return fig


def add_corridor_if_needed(fig, room_list, placed, rooms, corridor_width=3.0):
    """
    Jin rooms ki koi adjacency requirement nahi thi aur wo directly kisi se touch nahi kar rahe,
    unhe living room (ya sabse bara public room) tak dashed corridor line se jorta hai.
    """
    public_rooms = [r for r in room_list if r["type"] == "public"]
    if not public_rooms:
        return fig
    anchor = max(public_rooms, key=lambda r: r["width"] * r["height"])

    for r in room_list:
        room_obj = next((ro for ro in rooms if ro.name == r["name"]), None)
        if room_obj is None:
            continue

        connected = False
        a = {"x": r["x"], "y": r["y"], "w": r["width"], "h": r["height"]}
        for other in room_list:
            if other["name"] == r["name"]:
                continue
            b = {"x": other["x"], "y": other["y"], "w": other["width"], "h": other["height"]}
            if _find_touching_edge(a, b):
                connected = True
                break

        if connected or r["name"] == anchor["name"]:
            continue

        cx1 = r["x"] + r["width"] / 2
        cy1 = r["y"] + r["height"] / 2
        cx2 = anchor["x"] + anchor["width"] / 2
        cy2 = anchor["y"] + anchor["height"] / 2

        fig.add_shape(
            type="line",
            x0=cx1, y0=cy1, x1=cx2, y1=cy2,
            line=dict(color="#999999", width=corridor_width * 1.5, dash="dash"),
            layer="above",
            opacity=0.4,
        )

    return fig