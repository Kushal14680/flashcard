import streamlit as st
from utils.ui_styles import inject_custom_css, init_session_state, render_sidebar

# Page config
st.set_page_config(
    page_title="Settings - Flashcard Generator Agent",
    page_icon="⚙️",
    layout="wide"
)

# Initialize and inject UI styling
init_session_state()
inject_custom_css()

render_sidebar()

# Header
st.markdown('<div class="hero-section"><h1 class="hero-title">Configuration & Settings</h1><p class="hero-subtitle">Adjust generation parameters, model parameters, and API configurations</p></div>', unsafe_allow_html=True)

# Main Grid Layout
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔑 API & Provider Configurations")
    
    # API key binding
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password",
        help="Paste your OpenAI API Key here. If already set in .env, it will load automatically."
    )
    if api_key_input != st.session_state.openai_api_key:
        st.session_state.openai_api_key = api_key_input
        st.success("API Key updated in session state!")
        
    st.markdown("---")
    
    # Model Selector
    model_choice = st.selectbox(
        "Default LLM Model",
        options=["gpt-4o-mini", "gpt-4o"],
        index=0 if st.session_state.model_name == "gpt-4o-mini" else 1,
        help="Select the OpenAI ChatCompletion model to generate the flashcards."
    )
    if model_choice != st.session_state.model_name:
        st.session_state.model_name = model_choice
        
    # Vision Model Selector
    vision_choice = st.selectbox(
        "AI Vision Model",
        options=["gpt-4o-mini", "gpt-4o"],
        index=0 if st.session_state.vision_model_name == "gpt-4o-mini" else 1,
        help="Select the Vision model to use for diagram/image parsing."
    )
    if vision_choice != st.session_state.vision_model_name:
        st.session_state.vision_model_name = vision_choice

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Processing & Chunking Parameters")
    
    # Chunk size
    chunk_size_input = st.number_input(
        "Text Chunk Size (characters)",
        min_value=500,
        max_value=10000,
        value=st.session_state.chunk_size,
        step=100,
        help="The max character count per text section passed to the LLM agent."
    )
    if chunk_size_input != st.session_state.chunk_size:
        st.session_state.chunk_size = chunk_size_input
        
    # Chunk overlap
    chunk_overlap_input = st.number_input(
        "Text Chunk Overlap (characters)",
        min_value=0,
        max_value=2000,
        value=st.session_state.chunk_overlap,
        step=50,
        help="The amount of overlapping text between successive chunks to maintain context."
    )
    if chunk_overlap_input != st.session_state.chunk_overlap:
        st.session_state.chunk_overlap = chunk_overlap_input

    st.markdown("---")
    
    # Rate Limiting parameters
    rate_sleep_input = st.slider(
        "Request Delay / Sleep (seconds)",
        min_value=0.0,
        max_value=10.0,
        value=st.session_state.rate_limit_sleep,
        step=0.5,
        help="Time to sleep between sequential LLM calls to prevent API rate limiting (RateLimitError)."
    )
    if rate_sleep_input != st.session_state.rate_limit_sleep:
        st.session_state.rate_limit_sleep = rate_sleep_input
        
    st.markdown('</div>', unsafe_allow_html=True)

# Footer actions
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("🧹 System Maintenance")
if st.button("Reset Session State & Clear Cache"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
