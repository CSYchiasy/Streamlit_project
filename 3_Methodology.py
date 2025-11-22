import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="SteadyDayEveryday Methodology",
    layout="wide",
)

# --- CSS INJECTION FOR CENTERING TITLE ---
# This CSS will center the main title of the page.
st.markdown("""
<style>
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# --- 2. PAGE CONTENT ---

# 1. Page Title (centered via CSS above)
st.title("⚙️ SteadyDayEveryday Methodology Workflow")
st.markdown("---") # A nice separator

# 2. Image Block: Centering the Flowchart
# Use columns to center the image effectively.
# [1, 2, 1] means the image will be in the middle 50% width of the page.
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    # Display your flowchart image.
    # 'use_column_width="always"' makes it fill the central column,
    # ensuring it's a good size and maintains sharpness if the source is high-res.
    st.image("Methodology.png", use_column_width="always")

st.markdown("---") # Another separator

# --- 3. FOOTER ---
st.markdown("© 2025 SteadyDayEveryday Project")