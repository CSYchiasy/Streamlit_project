import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="#SteadyDayEveryday with Jagabot",
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
    st.title("💡 SteadyDayEveryday with Jagabot")

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
    st.header("Your Environmental Assistant")
    
    # The Core Paragraph 
    about_paragraph = """
    **#SteadyDayEveryday** with Jagabot who is your intelligent environmental assistant, designed to simplify daily planning and enhance safety for individuals in Singapore. 
    We tackle the challenge of fragmented information—where users currently have to check multiple sources like the NEA app and various government websites for crucial details 
    on weather, air quality, UV index, and dengue hotspots. 
    Our solution consolidates this data by tapping into **NEA's live APIs** for real-time readings, and historical records for forecast estimates which is then supplemented with a knowledge base of 
    government advisories, tips and guidelines using **Hybrid Retrieval-Augmented Generation (RAG)**. 
    This powerful combination ensures you receive a comprehensive, timely, and personalized information, allowing you to proactively plan your activities and make contingency plans with confidence.
    """
    st.markdown(about_paragraph)

# --- 3. FOOTER ---
st.markdown("---")
st.markdown("© 2025 SteadyDayEveryday Project")