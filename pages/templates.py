import streamlit as st
from utils.ui_styles import inject_custom_css, init_session_state, render_sidebar

# Page Config
st.set_page_config(
    page_title="Subject Templates - Flashcard Generator Agent",
    page_icon="📚",
    layout="wide"
)

init_session_state()
inject_custom_css()

# Subject Templates Dictionary
SUBJECT_TEMPLATES = {
    "General Study": (
        "Focus on key definitions, core concepts, critical facts, cause-and-effect relationships, "
        "and exam-worthy topics. Ensure clarity and academic rigor."
    ),
    "Medical & Biology": (
        "Focus on pathophysiology, diseases, symptoms, clinical diagnosis criteria, treatment protocols, "
        "drug mechanisms of action, side effects, and anatomical relationships. Use precise medical terminology."
    ),
    "Law & Legal Studies": (
        "Focus on constitutional provisions, statutes, key judicial cases, legal tests (e.g., intermediate scrutiny), "
        "rules of evidence, legal principles, and rulings. Link cases to legal concepts."
    ),
    "Software & Computer Science": (
        "Focus on algorithm time/space complexity, syntax constructs, design patterns, system architecture principles, "
        "data structures, performance trade-offs, and debugging paradigms. Format code snippets cleanly."
    ),
    "Language Learning & Linguistics": (
        "Focus on vocabulary, verb conjugations, grammar structures, idiomatic phrases, phonetics, "
        "and translations. Provide usage example sentences where helpful."
    ),
    "Mathematical & Physics Formulas": (
        "Focus on formula definitions, variables definitions, mathematical constraints, physical constants, "
        "proof concepts, and direct calculations. Format formulas using clear LaTeX or plain-text notation."
    )
}

# Ensure subject templates is in session state
if "subject_template" not in st.session_state:
    st.session_state.subject_template = "General Study"
if "custom_subject_instructions" not in st.session_state:
    st.session_state.custom_subject_instructions = SUBJECT_TEMPLATES["General Study"]

render_sidebar()

# Header
st.markdown('<div class="hero-section"><h1 class="hero-title">Subject-Specific Templates</h1><p class="hero-subtitle">Optimize the agent\'s generation criteria based on your study subject</p></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Select Subject")
    
    selected_template = st.radio(
        "Choose a template profile:",
        options=list(SUBJECT_TEMPLATES.keys()),
        index=list(SUBJECT_TEMPLATES.keys()).index(st.session_state.subject_template)
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📝 Target System Guidelines")
    
    # Text area showing current prompts
    if selected_template != st.session_state.subject_template:
        st.session_state.subject_template = selected_template
        st.session_state.custom_subject_instructions = SUBJECT_TEMPLATES[selected_template]
        st.rerun()
        
    custom_instrs = st.text_area(
        "Direct instructions injected into the Generation Agent's prompt:",
        value=st.session_state.custom_subject_instructions,
        height=200,
        help="You can customize these instructions to guide the agent to focus on specific elements."
    )
    if custom_instrs != st.session_state.custom_subject_instructions:
        st.session_state.custom_subject_instructions = custom_instrs
        
    st.info("💡 The selected template instructions will be appended to the LLM agent's prompts to guide card discovery.")
    st.markdown('</div>', unsafe_allow_html=True)
