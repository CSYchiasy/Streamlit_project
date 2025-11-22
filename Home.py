"""
SteadyDayEveryday - Environmental Information Bot for Singapore
A Streamlit app that provides real-time weather, air quality, UV index, and dengue alert information
using RAG (Retrieval-Augmented Generation) with LangChain and OpenAI.
"""

import streamlit as st
import hmac
from logics import load_rag_components, run_rag_query

# ====================================================================================
# PAGE CONFIGURATION
# ====================================================================================

st.set_page_config(
    page_title="SteadyDayEveryday - Environmental Chatbot",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        color: #808080;
        text-align: center;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

# ====================================================================================
# SESSION STATE INITIALIZATION
# ====================================================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_statuses" not in st.session_state:
    st.session_state.last_statuses = {
        "Weather": True, "PSI": True, "UV": True, "Dengue": True
    }

# ====================================================================================
# INITIALIZE RAG COMPONENTS (Only once via Streamlit caching)
# ====================================================================================

@st.cache_resource
def initialize_rag():
    """Load RAG components once at app startup."""
    with st.spinner("⏳ Loading AI and environmental data..."):
        return load_rag_components()

rag_components = initialize_rag()

# ====================================================================================
# AUTHENTICATION LOGIC
# ====================================================================================

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        try:
            secret_password = st.secrets["password"]
        except KeyError:
            st.error("Configuration Error: 'password' secret not found in secrets.toml.")
            return

        # Check against the secure secret
        if hmac.compare_digest(st.session_state["password"], secret_password):
            st.session_state["password_correct"] = True
            st.session_state["authenticated"] = True
            del st.session_state["password"]  # Don't store the password
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Hello! I'm Jagabot, your environmental assistant. How can I help you today?"
            })
        else:
            st.session_state["password_correct"] = False
            st.session_state["authenticated"] = False
            
    # Return True if the password is validated
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    
    # Display the incorrect password error
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")
        
    return False

def logout():
    """Logs out the user and clears session state."""
    st.session_state["authenticated"] = False
    st.session_state["password_correct"] = False
    st.session_state["messages"] = []
    st.rerun()

# ====================================================================================
# HELPER FUNCTIONS
# ====================================================================================

def display_api_status(name: str, status: bool):
    """Displays a colored status based on a boolean flag."""
    if status:
        st.markdown(f"**✅ {name}**", help="API connection successful.")
    else:
        st.markdown(f"**❌ {name}**", help="API connection failed. Showing historical data only.")

# ====================================================================================
# MAIN CHATBOT INTERFACE
# ====================================================================================

def chatbot_interface():
    """Display the RAG chatbot interface with enhanced layout."""
    
    # Extract components from the cached dictionary
    llm = rag_components["llm"]
    retriever = rag_components["retriever"]
    historical_psi_df = rag_components["historical_psi_df"]
    historical_uv_df = rag_components["historical_uv_df"]
    
    # --- 1. Top Section Layout (Title and Status) ---
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("☀️ SteadyDayEveryday with Jagabot")
        st.markdown("Here to jaga your day!")
    
    with col2:
        # Overall Status Light 
        st.markdown("<div style='padding-top: 15px;'>", unsafe_allow_html=True)
        overall_status = all(st.session_state.last_statuses.values())
        if overall_status:
            st.success("STATUS: Live Data OK")
        else:
            st.warning("STATUS: API Error")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("---")  # Visual separator

    # --- 2. Image Section ---
    col_img_left, col_img_center, col_img_right = st.columns([3, 1, 1]) 
    
    with col_img_left:
        st.image("jagabotwmap.png", use_column_width="always")
        
    st.markdown("---")
    
    # --- 3. Sidebar Enhancements ---
    st.sidebar.button("Logout", on_click=logout)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Data Status 🌐")
    
    # Display the status indicators based on the last query
    display_api_status("Weather Forecast", st.session_state.last_statuses["Weather"])
    display_api_status("PSI Index", st.session_state.last_statuses["PSI"])
    display_api_status("UV Index", st.session_state.last_statuses["UV"])
    display_api_status("Dengue Clusters", st.session_state.last_statuses["Dengue"])
    

    # --- 4. Chat History Container (Main Content Area) ---
    chat_container = st.container(height=550) 
    
    with chat_container:
        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # --- 5. Handle User Input ---
    default_prompt = "I am planning to go dragonboating at Kallang tomorrow around 11am. What should I be aware of?"
    if prompt := st.chat_input(default_prompt):
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Rerun to show new user message immediately
        st.rerun() 

    # Process and display assistant response
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        
        with st.chat_message("assistant"):
            with st.spinner("Generating environmental report..."):
                try:
                    # Call RAG function
                    result = run_rag_query(
                        user_query=st.session_state.messages[-1]["content"], 
                        retriever=retriever, 
                        historical_psi_df=historical_psi_df, 
                        historical_uv_df=historical_uv_df, 
                        llm=llm
                    )
                    
                    response_content = result["response"]
                    
                    # Update status flags for the sidebar display
                    st.session_state.last_statuses["Weather"] = result["weather_status"]
                    st.session_state.last_statuses["PSI"] = result["psi_status"]
                    st.session_state.last_statuses["UV"] = result["uv_status"]
                    st.session_state.last_statuses["Dengue"] = result["dengue_status"]
                    
                    st.markdown(response_content)
                
                except Exception as e:
                    error_message = f"An error occurred while fetching data or generating a response: {e}"
                    st.error(error_message)
                    response_content = error_message 

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        # Rerun to finalize the display
        st.rerun()

    # --- 6. Footer ---
    st.markdown("""
        <div class="footer">
            🌍 SteadyDayEveryday | Portal access is restricted to authorized users.
        </div>
    """, unsafe_allow_html=True)

# ====================================================================================
# MAIN APP EXECUTION
# ====================================================================================

if not check_password():
    st.stop()
    
chatbot_interface()