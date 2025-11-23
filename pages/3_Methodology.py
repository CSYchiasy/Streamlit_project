import streamlit as st
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="SteadyDayEveryday Methodology",
    layout="wide",
)

# --- CSS INJECTION FOR CENTERING TITLE ---
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
st.markdown("---") 

# 2. Image Block: Centering the Flowchart
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    st.image("Methodology.png", use_column_width="always")

st.markdown("---") 

# --- 3. FOOTER ---
st.markdown("© 2025 SteadyDayEveryday Project")