import streamlit as st
# Import both the runner and the new loader function
from main import run_rag_query, load_rag_components 

# --- 1. Page Configuration and Initialization (Revised) ---

st.title("Singapore Environmental RAG Chatbot")
st.caption("Ask about weather, PSI, UV, or Dengue in any region of Singapore.")

# Initialize RAG components using Streamlit's session state
if 'rag_components' not in st.session_state:
    with st.spinner("Initializing RAG components... This happens only once."):
        # ⚠️ CALL THE WRAPPER FUNCTION HERE
        st.session_state.rag_components = load_rag_components()
    st.success("Initialization Complete!")


# Unpack components for easier use in the runner function
llm_model = st.session_state.rag_components['llm']
retriever = st.session_state.rag_components['retriever']
historical_psi_df = st.session_state.rag_components['historical_psi_df']
historical_uv_df = st.session_state.rag_components['historical_uv_df']


# Initialize chat history (remains the same)
if "messages" not in st.session_state:
    # ... (your message initialization code) ...
    ...

# --- 2. Display Chat History (remains the same) ---
# ...

# --- 3. Handle User Input and RAG Execution (Revised Call) ---

if prompt := st.chat_input("Enter your query here..."):
    # ... (user message display code) ...

    # 2. Call the RAG pipeline
    with st.chat_message("assistant"):
        with st.spinner("Generating environmental report..."):
            
            # ⚠️ CALL THE run_rag_query FUNCTION WITH THE UNPACKED COMPONENTS
            response_content = run_rag_query(
                user_query=prompt,
                retriever=retriever,
                historical_psi_df=historical_psi_df,
                historical_uv_df=historical_uv_df,
                llm=llm_model 
            )
            
            # ... (display and store assistant's response code) ...
            ...