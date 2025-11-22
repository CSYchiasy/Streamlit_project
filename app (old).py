import streamlit as st
import time # Used for the success message delay

# --- CONFIGURATION ---
CORRECT_PASSWORD = "steady123!" 
AUTH_KEY = "authenticated"

# --- Configure Page Settings ---
st.set_page_config(
    page_title="#SteadyDayEveryday - Your Environmental RAG Assistant",
    page_icon="🤖",
    layout="centered"
)

# --- 1. INITIALIZE SESSION STATE ---
# Initialize the authentication state if it doesn't exist
if AUTH_KEY not in st.session_state:
    st.session_state[AUTH_KEY] = False

# --- 2. LOGIN FORM FUNCTION ---
def login_form():
    """Displays the login form and handles authentication."""
    st.title("Environmental RAG Login")
    st.info("Please enter the password to access the Environmental Assistant.")

    # Create a form container to handle the input and submission cleanly
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

        if submitted:
            if password == CORRECT_PASSWORD:
                st.session_state[AUTH_KEY] = True
                st.success("Login successful! Redirecting...")
                # Optional: Add a brief delay before rerunning the app
                time.sleep(0.5) 
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

# --- 3. MAIN APP LOGIC ---

if not st.session_state[AUTH_KEY]:
    # Display the login form if not authenticated
    login_form()
else:
    # Display the main content if authenticated
    st.title("Welcome to the Environmental Assistant")
    st.caption("Access granted. Use the sidebar to navigate to the Chatbot.")
    st.markdown("Navigate to the **Chatbot RAG** page in the sidebar to begin using the service.")

    # Optional: You can add a logout button
    if st.button("Logout", help="Click to log out and return to the login screen"):
        st.session_state[AUTH_KEY] = False
        st.info("Logged out successfully.")
        st.rerun()

    # Quick Navigation (Only shown after login)
    st.header("Quick Navigation")
    st.page_link("pages/3_Chatbot_RAG.py", label="Start Chatting Now", icon="💬")
    st.page_link("pages/1_About_Us.py", label="About Us", icon="💡")
    st.page_link("pages/2_Methodology.py", label="Methodology", icon="⚙️")