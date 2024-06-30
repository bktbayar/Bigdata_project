# map.py
import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import matplotlib.pyplot as plt
import numpy as np

@st.cache_data
def load_data():
    url = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"
    data = requests.get(url, params={"$limit": 10000}).json()  # Fetching 10,000 records
    community_area = pd.read_csv('C:/Users/yaren/Bigdata_project/community_area.csv', sep=';')
    community_area = community_area[['Number', 'Name']]
    
    df = pd.DataFrame(data)
    df['community_area'] = df['community_area'].astype(int)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df = pd.merge(df, community_area, left_on='community_area', right_on='Number', how='left')
    
    return df.dropna(subset=['latitude', 'longitude'])

def filter_data_by_district(data, district):
    filtered_data = data[data['Name'] == district]
    return filtered_data

def get_unique_districts(data):
    return data['Name'].unique()

def run():
    df = load_data()

    st.title("Chicago Crime Data Map")
    st.sidebar.header("Filters")

    min_date = df['date'].min()
    max_date = df['date'].max()
    start_date, end_date = st.sidebar.date_input('Date range', [min_date, max_date])

    years = df['date'].dt.year.unique()
    selected_years = st.sidebar.multiselect("Select Year", years, default=years)

    crime_types = df['primary_type'].unique()
    selected_crime_types = st.sidebar.multiselect("Select Crime Type", crime_types, default=crime_types)

    filtered_data = df[(df['date'] >= pd.to_datetime(start_date)) & 
                       (df['date'] <= pd.to_datetime(end_date)) & 
                       (df['date'].dt.year.isin(selected_years)) &
                       (df['primary_type'].isin(selected_crime_types))]

    if not filtered_data.empty:
        # Calculate crime counts and intensity
        crime_counts = filtered_data.groupby(['latitude', 'longitude']).size().reset_index(name='crime_count')
        min_count = crime_counts['crime_count'].min()
        max_count = crime_counts['crime_count'].max()
        crime_counts['intensity'] = (crime_counts['crime_count'] - min_count) / (max_count - min_count)

        # Calculate colors based on intensity
        colors = np.array(plt.cm.RdBu(crime_counts['intensity'])) * 255
        crime_counts['color'] = colors.tolist()

        # Merge crime_counts back into filtered_data on latitude and longitude
        filtered_data = pd.merge(filtered_data, crime_counts, on=['latitude', 'longitude'], how='left')

        # Default view state for the whole city of Chicago
        default_view_state = pdk.ViewState(
            latitude=41.8781,
            longitude=-87.6298,
            zoom=10,
            pitch=0
        )

        # Dropdown to select district
        districts = get_unique_districts(filtered_data)
        selected_district = st.selectbox('Select a community area', ["None"] + list(districts))

        # View state for scatter plot layer
        if "view_state" not in st.session_state:
            st.session_state.view_state = default_view_state

        # Filter data based on selected district for scatter plot layer
        if selected_district != "None":
            filtered_data_district = filter_data_by_district(filtered_data, selected_district)
            if not filtered_data_district.empty:
                st.session_state.view_state = pdk.ViewState(
                    latitude=filtered_data_district['latitude'].mean(),
                    longitude=filtered_data_district['longitude'].mean(),
                    zoom=12,  # Adjust zoom level as needed for the district
                    pitch=0
                )
        else:
            filtered_data_district = filtered_data  # Show all data if no district selected
            st.session_state.view_state = default_view_state

        # Heatmap layer
        heatmap_layer = pdk.Layer(
            'HeatmapLayer',
            data=filtered_data,
            get_position='[longitude, latitude]',
            get_weight='crime_count',
            radiusPixels=60,
            intensity=1,
            threshold=0.03,
            opacity=0.6,
            colorRange=[
                [0, 255, 0, 25],
                [0, 255, 0, 125],
                [0, 255, 0, 255],
                [255, 255, 0, 255],
                [255, 0, 0, 255]
            ],
            pickable=True  # Enable picking for tooltips
        )

        # Scatterplot layer
        scatterplot_layer = pdk.Layer(
            'ScatterplotLayer',
            data=filtered_data_district,
            get_position='[longitude, latitude]',
            get_radius=100,
            get_fill_color='color',
            opacity=0.6,
            pickable=True,  # Enable picking for tooltips
            tooltip={
                "html": "<b>Date:</b> {month}-{day} {hour}:00<br/><b>Type:</b> {primary_type}<br/><b>Description:</b> {description}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        )

        # Display maps side by side in Streamlit
        col1, col2 = st.columns(2)
        with col1:
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=default_view_state,
                layers=[heatmap_layer],
            ))
        with col2:
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=st.session_state.view_state,
                layers=[scatterplot_layer],
                tooltip={
                "html": "<b>Date:</b> {month}-{day} {hour}:00<br/><b>Type:</b> {primary_type}<br/><b>Description:</b> {description}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
                
            ))

    else:
        st.write("No data available for the selected filters.")
