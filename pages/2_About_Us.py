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
col_title_left, col_title_center, col_title_right = st.columns([0.4, 1, 0.4])

with col_title_center:
    st.markdown(
        """
        <h1 style='text-align: center;'>Jagabot at your service!</h1>
        """, 
        unsafe_allow_html=True
    )

st.markdown("---")

# --- IMAGE BLOCK ---

# 1. Use columns to center the image block.
col_img_left, col_img_center, col_img_right = st.columns([1, 3, 1]) 

with col_img_center:
    # 2. Use 'use_column_width="always"' for maximum sharpness and automatic sizing within the narrow center column.
    st.image("jagabot.png", use_column_width="always") 


st.markdown("##") # Adds space below the image


# --- TEXT CONTENT---

# Use columns for the main text body to create a centered reading area
col_margin_left, col_text_main, col_margin_right = st.columns([0.5, 3, 0.5])

with col_text_main:
    
    # The Core Paragraph (FIXED: Using <h2> and <h3> with inline styles for larger font)
    about_paragraph = """
    <h2 style='font-size: 2.5em; color: #007bff; margin-bottom: 0px;'>🎯 One Mission: Empowering Your Day</h2>

Jagabot is Singapore’s intelligent environmental assistant, here transforming how you plan your everyday. We solve the common challenge of fragmented information: the public must currently navigate multiple sources—from the NEA app to various government advisories—for crucial details on weather, air quality (PSI), UV index, and dengue hotspots.

<h3 style='font-size: 1.8em; margin-top: 20px;'>Our Solution</h3>

Jagabot delivers context-aware advice by:

📊 Consolidating Data: Tapping into NEA's live APIs for real-time, environmental readings from an official source.

📈 Enhancing Forecasts: Supplementing live data with historical records to generate reliable forecast estimates for the coming days.

📍 Focusing on Context: Crucially, Jagabot automatically analyzes your specific date, time, and target region (e.g., Jurong, East Coast) from your query to ensure location-aware and timely advice.

📜 Integrating Guidance: Combining all environmental factors with official government guidelines and safety tips.

This ensures you receive a highly contextual, timely, and personalized environmental report, enabling you to proactively plan your schedule and confidently make contingency plans!

<h3 style='font-size: 1.8em; margin-top: 20px;'>Data Sources</h3>

ℹ️ Guidelines and advisories from Meteorological Service Singapore (MSS), National Environmental Agency (NEA) and Health Hub Singapore.

🔗 Live and historical data from National Environmental Agency (NEA)

"""
    st.markdown(about_paragraph, unsafe_allow_html=True)

        # --- NEW: DISCLAIMER SECTION ---
    st.markdown("##") # Add spacing before the disclaimer
    disclaimer_section = """
    <div style='border: 1px solid #ffcc00; padding: 15px; border-radius: 8px; background-color: #fffacd;'>
        <h3 style='font-size: 1.5em; color: #b8860b; margin-top: 0px;'>💡 Important Notice</h3>
        <p style='font-size: 0.95em; margin-bottom: 0px;'>
        This web application is a protoype developed for educational purposes only. The environmental and health advice provided by Jagabot 
        is intended for informational and planning purposes only. While we source data from authoritative bodies like the NEA, 
        this tool is not a substitute for official government alerts, professional medical advice, or exercising personal caution. 
        Please be aware that the LLM may also generate inaccurate or incorrect information. 
        </p>
    </div>
    """
    st.markdown(disclaimer_section, unsafe_allow_html=True)

# --- 3. FOOTER ---
st.markdown("---")
st.markdown("© 2025 SteadyDayEveryday Project")