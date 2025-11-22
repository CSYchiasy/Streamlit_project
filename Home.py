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
    
# Placeholder functions for dependencies used in the re-added widget
def logout():
    """Resets authentication state and messages."""
    st.session_state["authenticated"] = False
    st.session_state["messages"] = []
    st.rerun()

def display_api_status(name, status):
    """Displays API status in the sidebar."""
    if status:
        st.sidebar.success(f"🟢 {name}: OK")
    else:
        st.sidebar.error(f"🔴 {name}: FAIL")

def check_password():
    # Placeholder: In a real app, this would handle authentication
    return True 

# ====================================================================================
# CHATBOT INTERFACE FUNCTION
# ====================================================================================

def chatbot_interface():
    
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
    
    # --- 4. Chat History Display ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- 5. User Instructions (FIXED: Converting Markdown to HTML for guaranteed styling) ---
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
    
    # --- 6. Chat Input and Logic ---
    if prompt := st.chat_input("Ask about the weather, PSI, UV, or dengue risk..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display the user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display the "Generating..." spinner
        with st.chat_message("assistant"):
            with st.spinner("Generating detailed environmental report..."):
                # Run the RAG query logic
                try:
                    components = load_rag_components() 
                    retriever = components["retriever"]
                    historical_psi_df = components["historical_psi_df"]
                    historical_uv_df = components["historical_uv_df"]
                    llm = components["llm"]
                    
                    result = run_rag_query(
                        user_query=prompt, 
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
        # Rerun to clear the spinner and finalize the display
        st.rerun()

    # --- 7. Footer ---
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