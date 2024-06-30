# main.py
import streamlit as st
from pages import data_analysis
from pages import map

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Map", "Crime Data Analysis"])

# Load the selected page
if page == "Home":
    st.write("# Welcome to the Chicago Safety Guide!")
    st.write("Use the sidebar to navigate to different sections of the app.")
    st.markdown(
    """
    Explore the city's crime rates with us as we navigate through maps and provide insightful data. 

    Stay informed, stay safe, and let's work together to make Chicago a brighter place!
    """
)
elif page == "Map":
    map.run()
elif page == "Crime Data Analysis":
    data_analysis.run()
