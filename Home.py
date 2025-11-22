import streamlit as st
import os
import random  
import hmac
from main import load_rag_components, run_rag_query


# ====================================================================
# CONFIGURATION
# ====================================================================

st.set_page_config(
    page_title="SteadyDayEveryday - Environmental Chatbot",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize Session State Variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []
# Placeholder for API status (Defaulting to True until first query)
if "last_statuses" not in st.session_state:
    st.session_state.last_statuses = {
        "Weather": True, "PSI": True, "UV": True, "Dengue": True
    }


# ====================================================================
# PERFORMANCE & INITIALIZATION
# ====================================================================

@st.cache_resource
def initialize_rag_components():
    """
    Loads and caches the heavy RAG components (LLM, Vector Store, DataFrames).
    This function is called only once when the app starts.
    """
    with st.spinner("Loading AI and environmental data..."):
        # This calls the wrapper you defined in main.py
        components = load_rag_components() 
    return components

# Load components immediately, caching the result
rag_components = initialize_rag_components()

# ====================================================================
# AUTHENTICATION LOGIC
# ====================================================================
# This function is triggered when the user clicks the "Login" button (on_click)

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
            st.session_state["authenticated"] = True # Keep your old state
            del st.session_state["password"]  # Don't store the password.
            st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm Jagabot, your environmental assistant. How can I help you today?"})
        else:
            st.session_state["password_correct"] = False
            st.session_state["authenticated"] = False
            
    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
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
    st.session_state["password_correct"] = False # Reset the new state variable
    st.session_state["messages"] = []
    st.rerun()

    # Inject a simple CSS footer for a professional touch
    st.markdown("""
        <style>
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
        <div class="footer">
            Portal access is restricted to authorized users.
        </div>
    """, unsafe_allow_html=True)


# ====================================================================
# CHATBOT INTERFACE (MAIN APPLICATION)
# ====================================================================

# Helper function for dynamic status display (used in chatbot_interface)
def display_api_status(name: str, status: bool):
    """Displays a colored status based on a boolean flag."""
    if status:
        st.markdown(f"**✅ {name}**", help="API connection successful.")
    else:
        st.markdown(f"**❌ {name}**", help="API connection failed. Showing historical data only.")


# --- AMENDED: Jazzed-Up Chatbot Interface (chatbot_interface) ---
def chatbot_interface():
    """Display the RAG chatbot interface with jazzed-up layout."""
    
    # Extract components from the cached dictionary
    llm = rag_components["llm"]
    retriever = rag_components["retriever"]
    historical_psi_df = rag_components["historical_psi_df"]
    historical_uv_df = rag_components["historical_uv_df"]
    
    # --- 1. Top Section Layout (Title and Status) ---
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("☀️ SteadyDayEveryday")
        st.markdown("Jagabot here to jaga your day!")
    
    with col2:
        # Overall Status Light 
        st.markdown("<div style='padding-top: 15px;'>", unsafe_allow_html=True)
        overall_status = all(st.session_state.last_statuses.values())
        if overall_status:
            st.success("STATUS: Live Data OK")
        else:
            st.warning("STATUS: API Error")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("---") # Visual separator

    col_img_left, col_img_center, col_img_right = st.columns([3, 1, 1]) 
    
    with col_img_left:
        # Using a larger width (350px) to prevent the browser from stretching a small image.
        # Make sure your source image is high-resolution (e.g., 500x500 pixels).
        st.image("jagabotwmap.png", width=350) 
        
    st.markdown("---")
    
    # --- 2. Sidebar Enhancements ---
    st.sidebar.button("Logout", on_click=logout)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Data Status 🌐")
    
    # Display the status indicators based on the last query
    display_api_status("Weather Forecast", st.session_state.last_statuses["Weather"])
    display_api_status("PSI Index", st.session_state.last_statuses["PSI"])
    display_api_status("UV Index", st.session_state.last_statuses["UV"])
    display_api_status("Dengue Clusters", st.session_state.last_statuses["Dengue"])
    
    st.sidebar.markdown("---")

    # --- 3. Chat History Container (Main Content Area) ---
    # Use a fixed-height container to make the chat history scrollable
    chat_container = st.container(height=550) 
    
    with chat_container:
        # Display chat messages from history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # --- 4. Handle User Input ---
    # Set default input text for suggestion
    default_prompt = "I am planning to go dragonboating at Kallang tomorrow around 11am. What should I be aware of?"
    if prompt := st.chat_input(default_prompt):
        
        # 1. Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Rerun chat history to show new user message immediately
        st.rerun() 

    # Rerun logic to display the response immediately after input
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        
        # 2. Get AI response using the RAG runner from main.py
        with st.chat_message("assistant"):
            with st.spinner("Generating environmental report..."):
                try:
                    # Call your core RAG function
                    # NOTE: This assumes run_rag_query now returns a dictionary with 'response' and status flags
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

        # 3. Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response_content})
        # Rerun to clear the "Generating..." spinner and finalize the display
        st.rerun()


# ====================================================================
# MAIN APP EXECUTION
# ====================================================================

if not check_password():
    st.stop()
    
chatbot_interface()