import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import numpy as np
import pydeck as pdk
from datetime import datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap
import time
# Function to load data from the Chicago Data Portal
@st.cache_data
def load_data():
    url = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"
    data = requests.get(url, params={"$limit": 10000}).json()  # Fetching 10,000 record
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['primary_type'] = df['primary_type'].str.title()  # Convert crime types to title case
    return df

def run():
    # Load the data
    df = load_data()

    # Community area names mapping
    community_area_names = {
        1: "Rogers Park", 2: "West Ridge", 3: "Uptown", 4: "Lincoln Square", 5: "North Center",
        6: "Lake View", 7: "Lincoln Park", 8: "Near North Side", 9: "Edison Park", 10: "Norwood Park",
        11: "Jefferson Park", 12: "Forest Glen", 13: "North Park", 14: "Albany Park", 15: "Portage Park",
        16: "Irving Park", 17: "Dunning", 18: "Montclare", 19: "Belmont Cragin", 20: "Hermosa",
        21: "Avondale", 22: "Logan Square", 23: "Humboldt Park", 24: "West Town", 25: "Austin",
        26: "West Garfield Park", 27: "East Garfield Park", 28: "Near West Side", 29: "North Lawndale",
        30: "South Lawndale", 31: "Lower West Side", 32: "(The) Loop", 33: "Near South Side",
        34: "Armour Square", 35: "Douglas", 36: "Oakland", 37: "Fuller Park", 38: "Grand Boulevard",
        39: "Kenwood", 40: "Washington Park", 41: "Hyde Park", 42: "Woodlawn", 43: "South Shore",
        44: "Chatham", 45: "Avalon Park", 46: "South Chicago", 47: "Burnside", 48: "Calumet Heights",
        49: "Roseland", 50: "Pullman", 51: "South Deering", 52: "East Side", 53: "West Pullman",
        54: "Riverdale", 55: "Hegewisch", 56: "Garfield Ridge", 57: "Archer Heights", 58: "Brighton Park",
        59: "McKinley Park", 60: "Bridgeport", 61: "New City", 62: "West Elsdon", 63: "Gage Park",
        64: "Clearing", 65: "West Lawn", 66: "Chicago Lawn", 67: "West Englewood", 68: "Englewood",
        69: "Greater Grand Crossing", 70: "Ashburn", 71: "Auburn Gresham", 72: "Beverly",
        73: "Washington Heights", 74: "Mount Greenwood", 75: "Morgan Park", 76: "O'Hare", 77: "Edgewater"
    }

    # Example descriptions for crime types (you can replace these with actual descriptions)
    crime_descriptions = {
        "Theft": "Taking property without permission",
        "Battery": "Physical attack or threat",
        "Criminal Damage": "Damaging property intentionally",
        "Assault": "Threatening physical harm",
        "Other Offense": "Other criminal activities",
        "Narcotics": "Drug-related offenses",
        "Burglary": "Illegal entry with intent to commit a crime",
        "Motor Vehicle Theft": "Theft of a motor vehicle",
        "Robbery": "Taking property by force",
        "Deceptive Practice": "Fraud or deceitful actions",
        "Criminal Trespass": "Entering property without permission",
        "Weapons Violation": "Illegal possession or use of weapons",
        "Prostitution": "Engaging in or promoting sexual activities for money",
        "Sex Offense": "Sexual crimes excluding rape",
        "Gambling": "Illegal betting or gaming",
        "Liquor Law Violation": "Breaking laws related to alcohol",
        "Arson": "Setting fire to property intentionally",
        "Homicide": "Killing of one person by another",
        "Kidnapping": "Unlawful seizure and detention of a person",
        "Intimidation": "Threatening someone to cause fear",
        "Stalking": "Repeated, unwanted attention and contact"
    }

    # Set up the Streamlit app
    st.title("Chicago Crime Data Analysis")

    # Sidebar for filters and navigation
    st.sidebar.header("Filters")

    # Date range filter
    min_date = datetime(2022, 1, 1)  # Set the minimum date to January 1, 2022
    max_date = df['date'].max().to_pydatetime()  # Convert to datetime for comparison

    # Get the current date and calculate the start of the current week
    current_date = datetime.now()
    default_end_date = min(current_date, max_date)
    start_of_week = default_end_date - timedelta(days=default_end_date.weekday())
    # Date input for date range
    date_range = st.sidebar.date_input('Date range', [start_of_week, default_end_date], min_value=min_date, max_value=max_date)

    # Ensure date_range always has two dates
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = start_of_week
        end_date = default_end_date

    # Crime type filter
    crime_types = df['primary_type'].unique()
    select_all = st.sidebar.checkbox("Select All Crime Types", value=True)
    if select_all:
        selected_crime_types = st.sidebar.multiselect("Select Crime Type", crime_types, default=crime_types)
    else:
        selected_crime_types = st.sidebar.multiselect("Select Crime Type", crime_types)

    # Search function
    search_term = st.sidebar.text_input("Search Crime Description, Case Number, etc.")

    # Filter the data based on the selected options and search term
    filtered_data = df[
                    (df['primary_type'].isin(selected_crime_types)) & 
                    (df['date'] >= np.datetime64(start_date)) & 
                    (df['date'] <= np.datetime64(end_date))]

    if search_term:
        filtered_data = filtered_data[filtered_data.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]

    # Sidebar for navigation
    st.sidebar.subheader("Sections")
    section = st.sidebar.radio("Go to", [
        "Crime Types Distribution", 
        "Crime Over Time", 
        "Crime by Day of Week",
        "Crime by Hour",
        "Crime Trends",
        "Arrest Analysis",
        "Crime by Location Description",
        "Distribution per Community Area"
    ])

    # Expanders for each section based on navigation
    if section == "Crime Types Distribution":
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
            fig, ax = plt.subplots(figsize=(3, 3))  # Smaller figure size
            wedges, texts, autotexts = ax.pie(main_crimes, labels=main_crimes.index, autopct='%1.1f%%', startangle=90, colors=colors(np.linspace(0, 1, len(main_crimes))), textprops={'fontsize': 5})
            
            # Change the color of the text
            for text in texts:
                text.set_color('black')
            for autotext in autotexts:
                autotext.set_color('white')
            
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)

            # Display the legend below the pie chart in two tables
            st.subheader("Legend")
            
            crime_legend = []
            others_legend = []
            for crime_type, percentage in main_crimes.items():
                description = crime_descriptions.get(crime_type, "No description available.")
                if crime_type == 'Others':
                    other_types = crime_type_percent[crime_type_percent < 4]
                    for other_crime_type, other_percentage in other_types.items():
                        other_description = crime_descriptions.get(other_crime_type, "No description available.")
                        others_legend.append([other_crime_type, other_description, f"{other_percentage:.2f}%"])
                else:
                    crime_legend.append([crime_type, description, f"{percentage:.2f}%"])
            
            legend_df1 = pd.DataFrame(crime_legend, columns=["Crime Type", "Description", "Percentage"])
            legend_df2 = pd.DataFrame(others_legend, columns=["Crime Type", "Description", "Percentage"])
            
            st.table(legend_df1)
            st.subheader("Others Category Breakdown")
            st.table(legend_df2)

    elif section == "Crime Over Time":
            st.subheader("Crime Over Time")
            crime_over_time = filtered_data.groupby('date').size()
            st.line_chart(crime_over_time)

    elif section == "Distribution per Community Area":
            st.subheader("Amount of Crime Type per Community Area")
            
            # Replace community area numbers with names
            filtered_data['community_area'] = filtered_data['community_area'].astype(int).map(community_area_names)
            
            # Group data by community_area and primary_type before dropping the column
            crime_counts = filtered_data.groupby(['community_area', 'primary_type']).size().unstack().fillna(0)
            plt.figure(figsize=(10, 5))  # Smaller figure size
            sns.heatmap(crime_counts, cmap="YlGnBu", linewidths=.5)
            st.pyplot(plt)

    elif section == "Crime by Day of Week":
            st.subheader("Crime by Day of Week")
            day_of_week_counts = filtered_data['day_of_week'].value_counts()
            st.bar_chart(day_of_week_counts)

    elif section == "Crime by Hour":
            st.subheader("Crime by Hour")
            hour_counts = filtered_data['hour'].value_counts().sort_index()
            st.bar_chart(hour_counts)

    elif section == "Crime Trends":
            st.subheader("Crime Trends")
            
            # Determine the most recent date in the dataset
            most_recent_date = df['date'].max()
            
            # Monthly trend: last 12 months each from beginning of month until end of month and the current month from beginning until current date
            last_12_months = df[(df['date'] >= (most_recent_date - pd.DateOffset(months=12)).replace(day=1)) & (df['date'] < most_recent_date)]
            monthly_trend = last_12_months.groupby(last_12_months['date'].dt.to_period("M")).size()
            current_month = df[df['date'] >= most_recent_date.replace(day=1)]
            monthly_trend = pd.concat([monthly_trend, pd.Series({most_recent_date.to_period("M"): len(current_month)})])
            
            # Weekly trend: last 4 weeks each from beginning of week until end of week and the current week from beginning until current date
            current_week = df[(df['date'] >= most_recent_date - timedelta(days=most_recent_date.weekday())) & (df['date'] <= most_recent_date)]
            last_4_weeks = df[(df['date'] >= (most_recent_date - pd.DateOffset(weeks=4))) & (df['date'] < most_recent_date - timedelta(days=most_recent_date.weekday()))]
            weekly_trend = last_4_weeks.groupby(last_4_weeks['date'].dt.to_period("W-SUN")).size()
            weekly_trend = pd.concat([weekly_trend, pd.Series({most_recent_date.to_period("W-SUN"): len(current_week)})])
            
            # Daily trend: from 12am to 12am for each hour the number of crimes in the last 24 hours
            last_24_hours = df[(df['date'] >= (most_recent_date - timedelta(days=1))) & (df['date'] <= most_recent_date)]
            daily_trend = last_24_hours.groupby(last_24_hours['date'].dt.hour).size()
            
            fig, axs = plt.subplots(3, 1, figsize=(10, 15))
            
            # Monthly trend plot
            axs[0].plot(monthly_trend.index.astype(str), monthly_trend.values, marker='o', color='blue', linestyle='-', linewidth=2)
            axs[0].set_title("Monthly Crime Trend (Last 12 Months + Current Month)", fontsize=14)
            axs[0].set_xlabel("Month", fontsize=12)
            axs[0].set_ylabel("Number of Crimes", fontsize=12)
            axs[0].grid(True, linestyle='--', alpha=0.6)
            axs[0].tick_params(axis='x', rotation=45)

            # Weekly trend plot
            axs[1].plot(weekly_trend.index.astype(str), weekly_trend.values, marker='o', color='green', linestyle='-', linewidth=2)
            axs[1].set_title("Weekly Crime Trend (Last 4 Weeks + Current Week)", fontsize=14)
            axs[1].set_xlabel("Week", fontsize=12)
            axs[1].set_ylabel("Number of Crimes", fontsize=12)
            axs[1].grid(True, linestyle='--', alpha=0.6)

            # Daily trend plot
            axs[2].plot(daily_trend.index, daily_trend.values, marker='o', color='red', linestyle='-', linewidth=2)
            axs[2].set_title("Hourly Crime Trend (Last 24 Hours)", fontsize=14)
            axs[2].set_xlabel("Hour of the Day", fontsize=12)
            axs[2].set_ylabel("Number of Crimes", fontsize=12)
            axs[2].grid(True, linestyle='--', alpha=0.6)

            plt.tight_layout(pad=3.0)
            st.pyplot(fig)

    elif section == "Arrest Analysis":
            st.subheader("Arrest Analysis")
            arrest_counts = filtered_data['arrest'].value_counts()
            st.bar_chart(arrest_counts)

    elif section == "Crime by Location Description":
            st.subheader("Crime by Location Description")
            
            # Filter the data for the selected date range
            selected_date = st.slider("Select Date for Weekly View", min_value=min_date.date(), max_value=max_date.date(), value=max_date.date())
            start_week = selected_date - timedelta(days=7)
            end_week = selected_date

            filtered_data_last_7_days = df[(df['date'] >= pd.to_datetime(start_week)) & (df['date'] <= pd.to_datetime(end_week))]

            # Calculate the percentage of each location description
            location_counts = filtered_data_last_7_days['location_description'].value_counts()
            top_locations = location_counts[:10]
            other_locations = location_counts[10:].sum()
            
            top_locations['Other'] = other_locations
            location_percent = (top_locations / location_counts.sum()) * 100
            
            # Horizontal bar chart for location description distribution
            fig, ax = plt.subplots(figsize=(10, 8))  # Adjust the size as needed
            sns.barplot(x=location_percent.values, y=location_percent.index, ax=ax, palette="Blues_d")
            ax.set_xlabel("Percentage of Crimes")
            ax.set_ylabel("Location Description")
            ax.set_title(f"Crime by Location Description for the Week of {start_week} to {end_week}")
            
            # Add annotations
            for i, (value, name) in enumerate(zip(location_percent.values, location_percent.index)):
                ax.text(value, i, f'{value:.1f}%', ha='left', va='center', fontsize=9, color='black')
            
            st.pyplot(fig)
