import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="☀️SteadyDayEveryday with Jagabot☀️",
    layout="wide",
)

# --- INLINE CSS FOR TEXT ALIGNMENT ONLY ---
st.markdown("""
<style>
/* Center the secondary header */
h2 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# --- 2. WHO ARE WE ---

# 1. Center the title using columns
col_title_left, col_title_center, col_title_right = st.columns([1, 2, 1])

with col_title_center:
    st.title("One Mission: Empowering Your Everyday")

st.markdown("---")


# --- IMAGE BLOCK: Streamlit Native Centering and Sizing (FINAL FIX) ---

# 1. Use columns to center the image block.
col_img_left, col_img_center, col_img_right = st.columns([1, 1, 1]) 

with col_img_center:
    # 2. Use 'use_column_width="always"' for maximum sharpness and automatic sizing within the narrow center column.
    st.image("jagabot.png", use_column_width="always") 


st.markdown("##") # Adds space below the image


# --- TEXT CONTENT (BELOW THE IMAGE) ---

# Use columns for the main text body to create a centered reading area
col_margin_left, col_text_main, col_margin_right = st.columns([0.5, 3, 0.5])

with col_text_main:
    # This header is centered via the H2 CSS style block
    st.header("Jagabot at your service")
    
    # The Core Paragraph 
    about_paragraph = """
    🎯 One Mission: Empowering Your Day

Jagabot is Singapore’s intelligent environmental assistant, here transforming how you plan your everyday.

We solve the common challenge of fragmented information: the public must currently navigate multiple sources—from the NEA app to various government advisories—for crucial details on weather, air quality (PSI), UV index, and dengue hotspots.

Our Solution

Jagabot delivers context-aware advice through a sophisticated process:

📊 Consolidating Data: Tapping into NEA's live APIs for real-time, environmental readings from an official source.

📈 Enhancing Forecasts: Supplementing live data with historical records to generate reliable forecast estimates for the coming days.

📍 Focusing on Context: Crucially, Jagabot automatically analyzes your specific date, time, and target region (e.g., Jurong, East Coast) from your query to ensure location-aware and timely advice.

📜 Integrating Guidance: Combining all environmental factors with official government guidelines and safety tips.

This ensures you receive a highly contextual, timely, and personalized environmental overview, enabling you to proactively plan your schedule and confidently make contingency plans.
"""
    st.markdown(about_paragraph)

# --- 3. FOOTER ---
st.markdown("---")
st.markdown("© 2025 SteadyDayEveryday Project")