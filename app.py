import streamlit as st
from ui.input_form import get_room_requests
from engine.layout_planner import generate_variations
from engine.decision import get_best_layouts
from visualization.floorplan_2d import (
    draw_2d_floorplan,
    rooms_to_render_list,
    add_doors_to_figure,
    add_entrance_marker,
    add_corridor_if_needed,
)

st.set_page_config(page_title="Floor Plan Generator", layout="wide")
st.title("🏠 Rule-Based Floor Plan Generator")
st.caption("Har room ka size aap khud dete hain — system generic andaza nahi lagata.")

rooms, unit = get_room_requests()

if st.button("Generate Layouts", type="primary"):
    if not rooms:
        st.warning("Pehlay kam se kam kuch rooms daalein.")
    else:
        with st.spinner("Variations generate ho rahi hain..."):
            variations = generate_variations(rooms, count=3)
            best_layouts = get_best_layouts(rooms, variations, count=3)

        if not best_layouts:
            st.error("Koi valid layout nahi ban saka. Room sizes check karein.")
        else:
            st.success(f"{len(best_layouts)} variations mil gayi hain — best score sabse upar hai.")

            tabs = st.tabs([f"Variation {i + 1} (score: {score})" for i, (score, _) in enumerate(best_layouts)])

            for tab, (score, placed) in zip(tabs, best_layouts):
                with tab:
                    render_list = rooms_to_render_list(rooms, placed)
                    fig = draw_2d_floorplan(render_list, unit=unit)

                    fig = add_doors_to_figure(fig, render_list, door_width=4.0)

                    living_room = next((r for r in render_list if r["name"] == "Living Room"), None)
                    fig = add_entrance_marker(fig, living_room, render_list, door_width=4.0)

                    fig = add_corridor_if_needed(fig, render_list, placed, rooms, corridor_width=3.0)

                    st.plotly_chart(fig, use_container_width=True)

                    total_area = sum(r["width"] * r["height"] for r in render_list)
                    st.metric("Total covered area", f"{round(total_area, 1)} {unit}²")

                    with st.expander("Room-wise details"):
                        for r in render_list:
                            st.write(f"**{r['name']}** — {r['width']} x {r['height']} {unit} "
                                     f"= {round(r['width'] * r['height'], 1)} {unit}²")