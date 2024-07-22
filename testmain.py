# testmain.py
import streamlit as st

st.set_page_config(page_title="Chicago Safety Guide", page_icon="🛡️", layout="wide")

from pages import data_analysis
from pages import map
import base64

# Function to load image as base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Home", "Map", "Crime Data Analysis"])

if page == "Home":
    # Replace with the correct path to your image
    background_image_path = r"C:\Users\Bayar\Desktop\Bigdata_project\Bigdata_project\chi2.jpg"
    background_image = get_base64_image(background_image_path)

    # Add custom CSS for styling
    st.markdown(
        f"""
        <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden; /* Disable scrolling */
        }}
        .main {{
            background: url("data:image/jpeg;base64,{background_image}") no-repeat center center fixed;
            background-size: cover;
            width: 100vw;
            position: relative;
        }}
        .content-wrapper {{
            position: absolute;
            top: 5px;  /* Position content 5px from the top */
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 800px;
            text-align: center;
        }}
        .title {{
            color: #ffffff;
            font-size: 48px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.3);
            padding: 5px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .text {{
            color: #ffffff;
            font-size: 18px;
            background: rgba(0, 0, 0, 0.3);
            padding: 5px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .footer {{
            color: #ffffff;
            font-size: 18px;
            background: rgba(0, 0, 0, 0.3);
            padding: 5px;
            border-radius: 10px;
            margin-top: 5px;
            text-align: center;
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
            """, unsafe_allow_html=True)
        st.markdown('<div class="footer">Use the sidebar to navigate to different sections of the app</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
elif page == "Map":
    map.run()
elif page == "Crime Data Analysis":
    data_analysis.run()
