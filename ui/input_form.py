import streamlit as st
from engine.layout_planner import RoomRequest


def get_room_requests():
    st.header("Enter Room Details")

    unit = st.selectbox("Size unit", ["feet", "meter"], index=0)
    num_bedrooms = st.number_input("How many bedrooms you needed?", min_value=1, max_value=15, value=3, step=1)

    rooms = []
    bedroom_attach_flags = []

    st.subheader("Bedrooms")
    for i in range(int(num_bedrooms)):
        st.markdown(f"**Bedroom {i + 1}**")
        col1, col2, col3 = st.columns(3)
        w = col1.number_input(f"Width ({unit})", key=f"bw_{i}", value=12.0, min_value=4.0)
        h = col2.number_input(f"Length ({unit})", key=f"bh_{i}", value=10.0, min_value=4.0)
        has_attach = col3.checkbox("Attached washroom?", key=f"battach_{i}")
        key = f"bedroom_{i + 1}"
        rooms.append(RoomRequest(key, f"Bedroom {i + 1}", w, h, "private"))
        bedroom_attach_flags.append((key, has_attach))

    st.subheader("Kitchen")
    col1, col2, col3 = st.columns(3)
    kw = col1.number_input(f"Kitchen width ({unit})", value=8.0, min_value=4.0)
    kh = col2.number_input(f"Kitchen length ({unit})", value=8.0, min_value=4.0)
    kitchen_near_dining = col3.checkbox("Near the Dinning?", value=True)
    kitchen_adj = ["dining"] if kitchen_near_dining else []
    rooms.append(RoomRequest("kitchen", "Kitchen", kw, kh, "service", adjacent_to=kitchen_adj))

    st.subheader("Dining Room")
    add_dining = st.checkbox("Did you need Dining room?", value=True)
    if add_dining:
        col1, col2 = st.columns(2)
        dw = col1.number_input(f"Dining width ({unit})", value=10.0, min_value=4.0)
        dh = col2.number_input(f"Dining length ({unit})", value=10.0, min_value=4.0)
        rooms.append(RoomRequest("dining", "Dining Room", dw, dh, "public", adjacent_to=["kitchen"]))

    st.subheader("Living Room")
    col1, col2 = st.columns(2)
    lw = col1.number_input(f"Living room width ({unit})", value=15.0, min_value=6.0)
    lh = col2.number_input(f"Living room length ({unit})", value=14.0, min_value=6.0)
    rooms.append(RoomRequest("living", "Living Room", lw, lh, "public", adjacent_to=["entrance"]))

    num_extra_washrooms = st.number_input("How many you need extra (non-attached) washroom ?", min_value=0, max_value=5, value=1)
    for i in range(int(num_extra_washrooms)):
        st.markdown(f"**Extra Washroom {i + 1}**")
        col1, col2 = st.columns(2)
        ww = col1.number_input(f"Width ({unit})", key=f"eww_{i}", value=5.0, min_value=3.0)
        wh = col2.number_input(f"Length ({unit})", key=f"ewh_{i}", value=7.0, min_value=3.0)
        rooms.append(RoomRequest(f"washroom_extra_{i + 1}", f"Washroom {i + 1}", ww, wh, "service"))

    for key, wants_attach in bedroom_attach_flags:
        if wants_attach:
            wr_key = f"{key}_washroom"
            rooms.append(RoomRequest(wr_key, f"{key.replace('_', ' ').title()} Washroom", 5.0, 7.0, "service",
                                      adjacent_to=[key]))
            for r in rooms:
                if r.key == key:
                    r.adjacent_to.append(wr_key)

    return rooms, unit