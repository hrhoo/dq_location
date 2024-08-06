"""
* Purpose: Show Dairy Queen locations in Canada on a map and in a bar chart
* Author: Hyunsung Rho
* Date: Aug 5, 2024
* Version: 1.0    
* References: https://gist.github.com/M1r1k/d5731bf39e1dfda5b53b4e4c560d968d (geojson)
"""

import streamlit as st
import pandas as pd
import folium as fo
from streamlit_folium import st_folium as sf

# import requests as rq
import json
import branca
from folium import plugins as Plugin
import altair as alt


APP_NAME = "Dairy Queen Locations in Canada"
APP_SUBTITLE = "Source: Dairy Queen Canada (July 26, 2024)"
PROVINCE_DIC = {
    "ab": "Alberta",
    "bc": "British Columbia",
    "mb": "Manitoba",
    "nb": "New Brunswick",
    "nl": "Newfoundland and Labrador",
    "ns": "Nova Scotia",
    "on": "Ontario",
    "pe": "Prince Edward Island",
    "qc": "Quebec",
    "sk": "Saskatchewan",
    "yt": "Yukon",
}
LAT_LONG_DIC = {
    "ab": [53.9333, -116.5765],
    "bc": [53.7267, -127.6476],
    "mb": [55.0000, -97.0000],
    "nb": [46.5653, -66.4619],
    "nl": [52, -57.6604],
    "ns": [44.681999, -63.744311],
    "on": [45.2538, -80.3232],
    "pe": [46.5107, -63.4168],
    "qc": [50, -73.5491],
    "sk": [52.9399, -106.4509],
    "yt": [64.091344, -130.983844],
}
START_LOCATION = [60, -100]

def get_selected_checkboxes() -> list:
    # Get the selected checkboxes
    # dictionary doesn't have order, so sort the keys
    return sorted([
        i.replace("dynamic_checkbox_", "")
        for i in st.session_state.keys()
        if i.startswith("dynamic_checkbox_") and st.session_state[i]
    ])

def checkbox_container(data) -> str | None:
    cols = st.columns(2)
    if cols[0].button("Select All"):
        for i in data:
            st.session_state["dynamic_checkbox_" + i] = True
        # st.rerun()
    if cols[1].button("UnSelect All"):
        for i in data:
            st.session_state["dynamic_checkbox_" + i] = False
        # st.rerun()

    with cols[0]:
        for i in data:
            st.checkbox(i, key="dynamic_checkbox_" + i)
    with cols[1]:
        selected_checkbox = get_selected_checkboxes()
        if selected_checkbox:
            selected_prv = st.selectbox(
                "Select a province to see the number of DQ locations in each city",
                options=selected_checkbox,
            )
            return selected_prv
    return None


def double_map(df_location: pd.DataFrame, cad_geo: dict):

    style_function = lambda x: {
        "weight": 0.5,
        "color": "black",
        "fillColor": "skyblue",
        "fillOpacity": 0.75,
    }
    highlight_function = lambda x: {
        "fillColor": "#000000",
        "color": "#000000",
        "fillOpacity": 0.50,
        "weight": 0.1,
    }
    
    # main map m
    m = fo.Map(location=START_LOCATION, zoom_start=4)

    #process geojson data
    for each_prv in cad_geo["features"]:
        geo_m = fo.GeoJson(
            each_prv,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip=fo.GeoJsonTooltip(
                fields=["name", "count"],
                aliases=["Province: ", "Number of DQ branches: "],
                style=(
                    "background-color: white; color: #333333; font-family: arial; font-size: 15px; padding: 10px;"
                ),
            ),
        )
        
        # Create a figure to contain sub maps
        f = branca.element.Figure()
        
        # Create a map for each province
        prov_m = fo.Map(location=each_prv["properties"]["start_cord"], zoom_start=5)

        # Find the right province in the dataframe and get the rows (branches) in the province
        rows = pd.DataFrame(
            [
                row
                for _, row in df_location.iterrows()
                if row["Province_compare"] == each_prv["properties"]["short_name"]
            ]
        )

        locations = rows[["Latitude", "Longitude"]].values.tolist()
        
        # Add the cluster markers to the sub map (prov_m)
        Plugin.MarkerCluster(
            locations=locations, popups=rows["full_address"].values.tolist()
        ).add_to(prov_m)
        
        # Add the sub map to the figure
        prov_m.add_to(f)

        # Add the geojson layer to the main map
        iframe = branca.element.IFrame(width=700, height=450)
        f.add_to(iframe)
        
        # Add the figure to the popup
        popup = fo.Popup(iframe)
        geo_m.add_child(popup)
        
        # Add the geojson layer to the main map
        m.add_child(geo_m)
        
    sf(m, width=1280, height=720, returned_objects=[], center=START_LOCATION)
    return


def draw_prv_map(df_location: pd.DataFrame):
    # Get the selected provinces
    selected_prv = list(map(lambda x: x.lower(), get_selected_checkboxes()))

    # Filter the data
    if selected_prv:
        rows = df_location[df_location["Province_compare"].isin(selected_prv)]
        province_map = fo.Map(location=START_LOCATION, zoom_start=3, max_bounds=True)
        for _, row in rows.iterrows():
            fo.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=row["full_address"],
                marker_color="white",
                icon=fo.Icon(color="darkred", icon="shop", prefix="fa"),
            ).add_to(province_map)
        sf(
            province_map,
            returned_objects=[],
            center=START_LOCATION,
            width=1280,
            height=720,
        )

    return


def draw_bar_chart_city(df_by_city: pd.DataFrame, province: str | None):

    if province != None:
        st.title(f"Number of DQ stores in {province}")
        df_by_city = df_by_city[
            df_by_city["Province_compare"] == f"{province.lower()}"
        ][["City", "Address"]]

        # Create an Altair bar chart
        highlight = alt.selection_point(on="mouseover", fields=["City"], nearest=True)
        bar_chart = (
            alt.Chart(df_by_city)
            .mark_bar()
            .encode(
                x=alt.X("Address:Q", title="Number of Stores", axis=alt.Axis(format='d'), scale=alt.Scale(domain=(0, df_by_city["Address"].max() + 1))),
                y=alt.Y("City:N", title="City", sort="-x"),
                color=alt.condition(
                    highlight, alt.value("orange"), alt.value("steelblue")
                ),
                tooltip=["City", "Address"],
            )
            .properties(title="Order by Number of Stores in City")
            .add_params(highlight)
        )
        # Display the Altair chart in Streamlit
        st.altair_chart(bar_chart, use_container_width=True)

    return


def draw_bar_chart_prov(df_by_prov: pd.DataFrame):
    
    st.title(f"Number of DQ stores in each province")
    df_by_prov = df_by_prov[["Province_compare", "City"]]
    df_by_prov.loc[:, "Province_compare"] = df_by_prov["Province_compare"].replace(
        PROVINCE_DIC
    )

    # Create an Altair bar chart
    highlight = alt.selection_point(
        on="mouseover", fields=["Province_compare"], nearest=True
    )
    bar_chart = (
        alt.Chart(df_by_prov)
        .mark_bar()
        .encode(
            x=alt.X("Province_compare:N", title="Province"),
            y=alt.Y("City:Q", title="Number of locations"),
            color=alt.condition(highlight, alt.value("orange"), alt.value("steelblue")),
            tooltip=["Province_compare", "City"],
        )
        .add_params(highlight)
    )

    # Display the Altair chart in Streamlit
    st.altair_chart(bar_chart, use_container_width=True)
    return
def initialize_checkboxes(provinces):
    if 'initialized' not in st.session_state:
        for province in provinces:
            st.session_state["dynamic_checkbox_" + province] = True
        st.session_state['initialized'] = True

# Load the data
@st.cache_data
def load_data():
    df_by_prov = pd.read_csv("./DQ/Streamlit/DQ_location_gby_p.csv")
    df_location = pd.read_csv("./DQ/Streamlit/DQ_location_with_no_dup.csv")
    df_by_city = pd.read_csv("./DQ/Streamlit/DQ_location_gby_c.csv")
    return df_by_prov, df_location, df_by_city

# Load the data
@st.cache_data
def load_geojson():
    with open("./DQ/Streamlit/canada_provinces.geo.json", encoding="utf-8") as json_data:
        cad_geo = json.load(json_data)
    return cad_geo

def main():
    st.set_page_config(page_title=APP_NAME, page_icon="🍦", layout="wide")
    with st.container():
        st.image("./DQ/Streamlit/DQ_logo.png", width=100)
    st.title(APP_NAME)
    st.caption(APP_SUBTITLE)

    # Load the data and process the data
    df_by_prov, df_location, df_by_city = load_data()
    cad_geo = load_geojson()
    for _, row in df_by_prov.iterrows():
        for i in cad_geo["features"]:
            if i["properties"]["name"] == PROVINCE_DIC[row["Province_compare"]]:
                i["properties"]["count"] = row["Address"]
                i["properties"]["start_cord"] = LAT_LONG_DIC[row["Province_compare"]]
                i["properties"]["short_name"] = row["Province_compare"]
    for _, row in df_location.iterrows():
        df_location["full_address"] = (
            df_location["Address"].str.replace("-", " ")
            + ", "
            + df_location["City"].str.replace("-", " ")
        )

    # About
    with st.expander("About", expanded=True):
        st.write("Function: Showing the locations of Dairy Queen stores in Canada")
        st.divider()
        st.write("This app is built for PC and may not work properly on mobile devices")
        st.write(
            "The data was collected from Dairy Queen Canada website on July 26, 2024"
        )
        

    # Tabs for the map and the chart
    tab_map, tab_chart = st.tabs(["Interactive Map", "Province Chart"])
    with tab_map:
        col_1, col_2, col_3 = st.columns([1, 3, 1])
        with col_1:
            st.empty()
        with col_2:
            double_map(df_location, cad_geo)
        with col_3:
            st.empty()
    with tab_chart:
        col_1, col_2, col_3 = st.columns([1, 3, 1])
        with col_1:
            st.empty()
        with col_2:
            draw_bar_chart_prov(df_by_prov)
        with col_3:
            st.empty()

    st.divider()
    st.divider()

    # More information
    with st.expander("More information", expanded=True):
        st.write("checked provinces with DQ locations will be displayed on the map")
        st.divider()
        st.write(
            "If you check more than 1 province and select the province you want to see in detail, The number of DQ locations in each city will be displayed in the bar chart"
        )

    # Checkbox container
    if "Province" not in st.session_state.keys():
        Province = ["AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK", "YT"]
        st.session_state["Province"] = Province
    else:
        Province = st.session_state["Province"]
        
    # initializing checkboxes
    initialize_checkboxes(Province)
    
    # Display the map and the bar chart
    col1_1, col1_2, col1_3 = st.columns([1, 2, 2])
    with col1_1:
        with st.container(border=True):
            specific_prov = checkbox_container(Province)
    with col1_2:
        draw_prv_map(df_location)
    with col1_3:
        with st.container(border=True):
            draw_bar_chart_city(df_by_city, specific_prov)

    # def display_month_list(i):
    #     selected_option = st.multiselect("Select Category", ["a", "b", "c"], key=i)
    #     # st.write(f'your stuff')

    # cols = st.columns(4)
    # for i, c in enumerate(cols):
    #     with c:
    #         with st.expander(f"cat {i+1}"):
    #             display_month_list(i + 1)

    # cols = st.columns(4)
    # for i, c in enumerate(cols):
    #     with c:
    #         with st.expander(f"cat {i+5}"):
    #             display_month_list(i + 5)

    # cols = st.columns(4)
    # for i, c in enumerate(cols):
    #     with c:
    #         with st.expander(f"cat {i+9}"):
    #             display_month_list(i + 9)

    # tab1, tab2 = st.tabs(["tab1", "tab2"])
    # with tab1:
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         st.selectbox("City", ["City1", "City2"])
    #     with col2:
    #         st.selectbox("District", ["District1", "District2"])

    # with tab2:
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         st.selectbox("Another City", ["Another_City1", "Another_City2"])
    #     with col2:
    #         st.selectbox("Another District", ["Another_District1", "Another_District2"])
    # st.sidebar.date_input(
    # "Select date", value=None, min_value=None, max_value=None, key=None
    # )

if __name__ == "__main__":
    main()
