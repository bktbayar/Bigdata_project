import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import numpy as np
import pydeck as pdk
from matplotlib.colors import LinearSegmentedColormap

# Set page configuration at the top
st.set_page_config(layout="wide")

# Function to load data from the Chicago Data Portal
@st.cache_data
def load_data():
    url = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"
    data = requests.get(url, params={"$limit": 10000}).json()  # Fetching 10,000 records
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    return df

# Load the data
df = load_data()

# Example descriptions for crime types (you can replace these with actual descriptions)
crime_descriptions = {
    "THEFT": "Taking property without permission.",
    "BATTERY": "Physical attack or threat.",
    "CRIMINAL DAMAGE": "Damaging property intentionally.",
    "ASSAULT": "Threatening physical harm.",
    "OTHER OFFENSE": "Other criminal activities.",
    "NARCOTICS": "Drug-related offenses.",
    "BURGLARY": "Illegal entry with intent to commit a crime.",
    "MOTOR VEHICLE THEFT": "Theft of a motor vehicle.",
    "ROBBERY": "Taking property by force.",
    "DECEPTIVE PRACTICE": "Fraud or deceitful actions.",
    "CRIMINAL TRESPASS": "Entering property without permission.",
    "WEAPONS VIOLATION": "Illegal possession or use of weapons.",
    "PROSTITUTION": "Engaging in or promoting sexual activities for money.",
    "SEX OFFENSE": "Sexual crimes excluding rape.",
    "GAMBLING": "Illegal betting or gaming.",
    "LIQUOR LAW VIOLATION": "Breaking laws related to alcohol.",
    "ARSON": "Setting fire to property intentionally.",
    "HOMICIDE": "Killing of one person by another.",
    "KIDNAPPING": "Unlawful seizure and detention of a person.",
    "INTIMIDATION": "Threatening someone to cause fear.",
    "STALKING": "Repeated, unwanted attention and contact."
}

# Set up the Streamlit app
st.title("Chicago Crime Data Analysis")

# Sidebar for filters and navigation
st.sidebar.header("Filters")
st.sidebar.subheader("Data Filters")

# Date range filter
min_date = df['date'].min()
max_date = df['date'].max()
start_date, end_date = st.sidebar.date_input('Date range', [min_date, max_date])

# Year filter
years = df['year'].unique()
selected_year = st.sidebar.multiselect("Select Year", years, default=years)

# Crime type filter
crime_types = df['primary_type'].unique()
selected_crime_types = st.sidebar.multiselect("Select Crime Type", crime_types, default=crime_types)

# Search function
search_term = st.sidebar.text_input("Search Crime Description, Case Number, etc.")

# Filter the data based on the selected options and search term
filtered_data = df[(df['year'].isin(selected_year)) & 
                   (df['primary_type'].isin(selected_crime_types)) & 
                   (df['date'] >= np.datetime64(start_date)) & 
                   (df['date'] <= np.datetime64(end_date))]

if search_term:
    filtered_data = filtered_data[filtered_data.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]

st.sidebar.write(f"### Showing {len(filtered_data)} records")

# Sidebar for navigation
st.sidebar.subheader("Sections")
section = st.sidebar.radio("Go to", [
    "Crime Types Distribution", 
    "Crime Over Time", 
    "Crime Locations", 
    "Crime Heatmap",
    "Crime by Day of Week",
    "Crime by Hour",
    "Crime Trends",
    "Arrest Analysis"
])

# Main content layout
st.write(f"### Showing {len(filtered_data)} records")

# Display data table in the main content area
st.dataframe(filtered_data, height=300)  # Set height to make the table smaller

# Expanders for each section based on navigation
if section == "Crime Types Distribution":
    with st.expander("Crime Types Distribution", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        st.subheader("Crime Types Distribution")
        
        crime_type_counts = filtered_data['primary_type'].value_counts()
        
        # Calculate the percentage of each crime type
        crime_type_percent = (crime_type_counts / crime_type_counts.sum()) * 100
        
        # Aggregate crime types below 4% into "Others"
        other_crimes = crime_type_percent[crime_type_percent < 4].sum()
        main_crimes = crime_type_percent[crime_type_percent >= 4]
        main_crimes['Others'] = other_crimes
        
        # Define a color map with shades of blue
        colors = LinearSegmentedColormap.from_list("", ["#d1e5f0", "#2166ac"])
        
        # Pie chart for crime type distribution
        fig, ax = plt.subplots(figsize=(5, 5))  # Smaller figure size
        wedges, texts, autotexts = ax.pie(main_crimes, labels=main_crimes.index, autopct='%1.1f%%', startangle=90, colors=colors(np.linspace(0, 1, len(main_crimes))), textprops={'fontsize': 8})
        
        # Change the color of the text
        for text in texts:
            text.set_color('black')
        for autotext in autotexts:
            autotext.set_color('white')
        
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

        # Display the legend below the pie chart
        st.subheader("Legend")
        for crime_type, percentage in main_crimes.items():
            if crime_type == 'Others':
                continue
            description = crime_descriptions.get(crime_type, "No description available.")
            st.write(f"**{crime_type}**: {description} - **{percentage:.2f}%**")
        
        # Display the breakdown of the "Others" category
        if 'Others' in main_crimes:
            st.subheader("Others Category Breakdown")
            other_types = crime_type_percent[crime_type_percent < 4]
            for crime_type, percentage in other_types.items():
                description = crime_descriptions.get(crime_type, "No description available.")
                st.write(f"**{crime_type}**: {description} - **{percentage:.2f}%**")

elif section == "Crime Over Time":
    with st.expander("Crime Over Time", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        st.subheader("Crime Over Time")
        crime_over_time = filtered_data.groupby('date').size()
        st.line_chart(crime_over_time)

elif section == "Crime Locations":
    with st.expander("Crime Locations", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        st.subheader("Crime Locations")
        if not filtered_data.empty:
            filtered_data['latitude'] = filtered_data['latitude'].astype(float)
            filtered_data['longitude'] = filtered_data['longitude'].astype(float)
            filtered_data['date_str'] = filtered_data.apply(
                lambda row: f"{row['year']}-{row['month']:02d}-{row['day']:02d} {row['hour']:02d}:00:00", axis=1
            )  # Correct date formatting
            view_state = pdk.ViewState(
                latitude=filtered_data['latitude'].mean(),
                longitude=filtered_data['longitude'].mean(),
                zoom=10,
                pitch=0
            )
            layer = pdk.Layer(
                'ScatterplotLayer',
                data=filtered_data,
                get_position='[longitude, latitude]',
                get_radius=100,
                get_color=[0, 0, 0],  # Change color to black
                pickable=True
            )
            tool_tip = {
                "html": "<b>Date:</b> {date_str}<br/><b>Type:</b> {primary_type}<br/><b>Description:</b> {description}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
            crime_map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', initial_view_state=view_state, layers=[layer], tooltip=tool_tip)
            st.pydeck_chart(crime_map, use_container_width=True)

elif section == "Crime Heatmap":
    with st.expander("Crime Heatmap", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        if st.button("Show Heatmap"):
            st.subheader("Crime Heatmap")
            crime_counts = filtered_data.groupby(['community_area', 'primary_type']).size().unstack().fillna(0)
            plt.figure(figsize=(15, 8))  # Make heatmap bigger
            sns.heatmap(crime_counts, cmap="YlGnBu", linewidths=.5)
            st.pyplot(plt)

elif section == "Crime by Day of Week":
    with st.expander("Crime by Day of Week", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        st.subheader("Crime by Day of Week")
        day_of_week_counts = filtered_data['day_of_week'].value_counts()
        st.bar_chart(day_of_week_counts)

elif section == "Crime by Hour":
    with st.expander("Crime by Hour", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        st.subheader("Crime by Hour")
        hour_counts = filtered_data['hour'].value_counts().sort_index()
        st.bar_chart(hour_counts)

elif section == "Crime Trends":
    with st.expander("Crime Trends", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        st.subheader("Crime Trends")
        trend_yearly = filtered_data.groupby('year').size()
        trend_monthly = filtered_data.groupby('month').size()
        trend_daily = filtered_data.groupby('day').size()
        st.line_chart(trend_yearly, use_container_width=True)
        st.line_chart(trend_monthly, use_container_width=True)
        st.line_chart(trend_daily, use_container_width=True)

elif section == "Arrest Analysis":
    with st.expander("Arrest Analysis", expanded=True):
        st.write(f"### Showing {len(filtered_data)} records")
        st.subheader("Arrest Analysis")
        arrest_counts = filtered_data['arrest'].value_counts()
        st.bar_chart(arrest_counts)



