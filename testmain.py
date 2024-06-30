# main.py
import streamlit as st
from pages import data_analysis
from pages import map
import base64

# Set the page configuration with a title and an icon
st.set_page_config(page_title="Chicago Safety Guide", page_icon="🛡️", layout="wide")

# Function to load image as base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Map", "Crime Data Analysis"])

if page == "Home":
    # Replace with the correct path to your image
    background_image_path = r"C:\Users\Bayar\Desktop\Bigdata_project-main\chi2.jpg"
    background_image = get_base64_image(background_image_path)

    # Add custom CSS for styling
    st.markdown(
        f"""
        <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        .main {{
            background: url("data:image/jpeg;base64,{background_image}") no-repeat center center fixed;
            background-size: cover;
            height: 100vh;
            display: flex;
            justify-content: flex-start; /* Align content to the top */
            align-items: center;
            padding: 20px;
            text-align: center;
        }}
        .content-wrapper {{
            width: 100%;
            max-width: 800px;
        }}
        .title {{
            color: #ffffff;
            font-size: 48px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .text {{
            color: #ffffff;
            font-size: 18px;
            background: rgba(0, 0, 0, 0.7);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .footer {{
            color: #ffffff;
            font-size: 18px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-top: 20px;
        }}
        </style>
        """, unsafe_allow_html=True
    )

    # Add the background image div if the image is loaded successfully
    if background_image:
        st.markdown('<div class="main">', unsafe_allow_html=True)
        st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="title">Welcome to the Chicago Safety Guide</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="text">
            Your comprehensive resource for staying safe and informed in the Windy City. Our platform offers a range of tools, including interactive charts and dashboards, and an intuitive map to help you navigate Chicago confidently. Whether you're a resident or a visitor, our guide provides up-to-date safety information, empowering you to make well-informed decisions and explore the city with peace of mind.
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown('<div class="footer">Use the sidebar to navigate to different sections of the app</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
elif page == "Map":
    map.run()
elif page == "Crime Data Analysis":
    data_analysis.run()
