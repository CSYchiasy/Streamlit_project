"""
SteadyDayEveryday - Environmental Information Bot for Singapore
A Streamlit app that provides real-time weather, air quality, UV index, and dengue alert information
using RAG (Retrieval-Augmented Generation) with LangChain and OpenAI.
"""

import streamlit as st
from logics import load_rag_components, run_rag_query

# ====================================================================================
# PAGE CONFIGURATION
# ====================================================================================

st.set_page_config(
    page_title="SteadyDayEveryday",
    page_icon="🌍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ====================================================================================
# CUSTOM CSS
# ====================================================================================

st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# ====================================================================================
# APP TITLE
# ====================================================================================

st.title("🌍 SteadyDayEveryday")
st.markdown("""
    Your personal environmental information assistant for Singapore.
    Get real-time weather, air quality, UV index, and dengue alerts with actionable health advice.
""")

# ====================================================================================
# INITIALIZE RAG COMPONENTS (Only once via Streamlit caching)
# ====================================================================================

@st.cache_resource
def initialize_rag():
    """Load RAG components once at app startup."""
    with st.spinner("⏳ Initializing AI components (this may take a minute on first load)..."):
        return load_rag_components()

rag_components = initialize_rag()
llm = rag_components["llm"]
retriever = rag_components["retriever"]
historical_psi_df = rag_components["historical_psi_df"]
historical_uv_df = rag_components["historical_uv_df"]

# ====================================================================================
# MAIN UI
# ====================================================================================

st.markdown("---")

# Input section
st.subheader("📝 Ask a Question")
user_input = st.text_area(
    label="What would you like to know about the environment in Singapore?",
    placeholder="e.g., 'What's the weather like in the west region?', 'Is it safe to go out in the sun tomorrow?'",
    height=100,
    label_visibility="collapsed"
)

# Submit button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    submit_button = st.button("🔍 Get Information", use_container_width=True)

# ====================================================================================
# PROCESS QUERY AND DISPLAY RESULTS
# ====================================================================================

if submit_button:
    if not user_input.strip():
        st.warning("⚠️ Please enter a question!")
    else:
        st.markdown("---")
        
        with st.spinner("🤔 Processing your question..."):
            # Run RAG query
            result = run_rag_query(
                user_query=user_input,
                retriever=retriever,
                historical_psi_df=historical_psi_df,
                historical_uv_df=historical_uv_df,
                llm=llm
            )
        
        # Display response
        st.markdown("### Response")
        st.markdown(result["response"])
        
        # Display API status indicators
        st.markdown("---")
        st.markdown("### Data Source Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            weather_status = "✅ OK" if result["weather_status"] else "❌ Failed"
            st.metric("Weather", weather_status)
        
        with col2:
            psi_status = "✅ OK" if result["psi_status"] else "❌ Failed"
            st.metric("PSI", psi_status)
        
        with col3:
            uv_status = "✅ OK" if result["uv_status"] else "❌ Failed"
            st.metric("UV Index", uv_status)
        
        with col4:
            dengue_status = "✅ OK" if result["dengue_status"] else "❌ Failed"
            st.metric("Dengue", dengue_status)

# ====================================================================================
# SIDEBAR INFORMATION
# ====================================================================================

with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    **SteadyDayEveryday** helps you stay informed about environmental conditions in Singapore.
    
    **Features:**
    - Real-time weather forecasts
    - Air quality (PSI) readings
    - UV index information
    - Dengue alert levels
    - Personalized health advice
    
    **Data Sources:**
    - NEA (National Environment Agency)
    - Weather APIs
    - Historical climate data
    
    **Tips:**
    - Mention a region (Central, East, West, North, South)
    - Ask about specific times or dates
    - Ask for health advice based on conditions
    """)
    
    st.markdown("---")
    st.markdown("### 📍 Example Queries")
    st.markdown("""
    - "How's the weather in the west?"
    - "What's the PSI like today?"
    - "Should I go jogging tomorrow afternoon in Bedok?"
    - "Are there any dengue alerts?"
    - "What's the UV index now?"
    """)

# ====================================================================================
# FOOTER
# ====================================================================================

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    🌍 SteadyDayEveryday | Environmental Information Bot for Singapore
    </div>
    """, unsafe_allow_html=True)