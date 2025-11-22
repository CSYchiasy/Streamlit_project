import streamlit as st
import hmac
# Assuming logics.py contains these functions
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
# CUSTOM CSS (Includes spacing and prompt hint styling)
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
    /* --- CSS FIX: Reduce margins around the horizontal divider (hr) --- */
    hr {
        margin-top: 0.5rem; 
        margin-bottom: 0.5rem; 
    }
    /* Custom style for the prompt hint (Instructions box) */
    .prompt-hint {
        padding: 10px;
        /* FIX: Removed max-width and auto margins to make it full width (same size as input) */
        width: 100%; 
        /* END FIX */
        
        /* REDUCED MARGINS for better fit above chat input */
        margin-top: 10px; 
        margin-bottom: 10px; 
        border-radius: 8px;
        background-color: #f0f2f6; /* Light gray background */
        border-left: 5px solid #007bff; /* Blue accent bar */
        /* FIX: Increased font size for better visibility */
        font-size: 1.1em; 
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
# Placeholder for API status (Defaulting to True until first query)
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

# ====================================================================================
# AUTHENTICATION LOGIC
# ====================================================================================

def logout():
    """Logs out the user and clears session state."""
    st.session_state["authenticated"] = False
    st.session_state["password_correct"] = False
    st.session_state["messages"] = []
    st.rerun()

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        try:
            # Assuming you have a secret named "password" in your secrets.toml file
            secret_password = st.secrets["password"]
        except KeyError:
            # Fallback for environments without secrets.toml
            secret_password = "password123" # Use a fallback if st.secrets is unavailable

        # Check against the secure secret
        if hmac.compare_digest(st.session_state["password"], secret_password):
            st.session_state["password_correct"] = True
            st.session_state["authenticated"] = True
            del st.session_state["password"]  # Don't store the password
            if not st.session_state.messages: # Only greet on first successful login
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
    # Center the login form visually
    col_left, col_center, col_right = st.columns([1, 1, 1])
    
    with col_center:
        st.title("Portal Access")
        st.subheader("Login Required")
        st.text_input(
            "Enter Password", type="password", on_change=password_entered, key="password"
        )
        
        # Display the incorrect password error
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Password incorrect")
        
    return False

# ====================================================================================
# HELPER FUNCTIONS (for sidebar)
# ====================================================================================
def display_api_status(name, status):
    """Displays API status in the sidebar."""
    if status:
        st.sidebar.success(f"🟢 {name}: OK")
    else:
        st.sidebar.error(f"🔴 {name}: FAIL")

# ====================================================================================
# CHATBOT INTERFACE FUNCTION
# ====================================================================================

def chatbot_interface():
    
    # RAG components are loaded here after successful authentication
    rag_components = initialize_rag()
    llm = rag_components["llm"]
    retriever = rag_components["retriever"]
    historical_psi_df = rag_components["historical_psi_df"]
    historical_uv_df = rag_components["historical_uv_df"]
    
    # --- 1. Title Section (Centered and Single Line Fix) ---
    col_title_left, col_title_center, col_title_right = st.columns([0.4, 1, 0.4])

    with col_title_center:
        st.markdown(
            # Using h1 tag with CSS to ensure centering and large font
            """
            <h1 style='text-align: center;'>One Mission: Empowering Your Everyday</h1>
            """, 
            unsafe_allow_html=True
        )

    # st.divider() renders the <hr> tag, which now has reduced margins from the CSS above.
    st.divider()

    # --- 2. Image Section (FIXED: Centering the Image) ---
    # Use three columns with symmetrical side columns to create a centered image area.
    col_spacer_left, col_image_center, col_spacer_right = st.columns([1, 3, 1]) 
    
    with col_image_center:
        # The image will now be centered in the middle column and use its full width 
        st.image("jagabotwmap.png", use_column_width="always") 
        
    # --- 3. Sidebar Enhancements (RE-ADDED) ---
    st.sidebar.button("Logout", on_click=logout)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Live Data Status 🌐")
    
    # Display the status indicators based on the last query
    display_api_status("Weather Forecast", st.session_state.last_statuses["Weather"])
    display_api_status("PSI Index", st.session_state.last_statuses["PSI"])
    display_api_status("UV Index", st.session_state.last_statuses["UV"])
    display_api_status("Dengue Clusters", st.session_state.last_statuses["Dengue"])
    
    # --- 4. Chat History Display (FIXED: Using fixed-height container) ---
    # By placing the chat history inside a fixed-height container, it scrolls, 
    # ensuring the input box and instructions remain visible below it.
    chat_container = st.container(height=550) 
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # --- 5. User Instructions (Full Width and HTML Fix) ---
    st.markdown(
        """
        <div class="prompt-hint">
            <b>💡 How to Query:</b> For the best results, please specify the <b>time, date</b> (if a forecast), <b>region</b>, and intended activity.
            <br>
            <i>Example: "I am planning to <b>have a picnic</b> in <b>Jurong</b> at <b>3 PM tomorrow</b>?"</i>
        </div>
        """,
        unsafe_allow_html=True
    )