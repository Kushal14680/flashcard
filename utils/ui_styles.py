import streamlit as st

def inject_custom_css():
    """
    Injects global, SaaS-grade styling overrides into the Streamlit app.
    Features dark glassmorphism, responsive components, custom typography,
    and elegant animations.
    """
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        
        <style>
        /* Base page styling overrides */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Custom Main Dashboard Header Gradient */
        .hero-section {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #311042 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
        }
        
        .hero-title {
            font-size: 3rem !important;
            font-weight: 700 !important;
            background: linear-gradient(90deg, #38BDF8 0%, #A855F7 50%, #F43F5E 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            letter-spacing: -0.025em;
        }
        
        .hero-subtitle {
            font-size: 1.15rem;
            color: #94A3B8;
            font-weight: 400;
        }

        /* Glassmorphic card panels */
        .glass-card {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }

        /* Custom buttons styling */
        div.stButton > button {
            background: linear-gradient(90deg, #6366F1 0%, #4F46E5 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4) !important;
            transition: all 0.25s ease-in-out !important;
            width: 100%;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
            background: linear-gradient(90deg, #4F46E5 0%, #4338CA 100%) !important;
        }

        div.stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* Secondary action button (Download style) */
        .download-btn-wrapper div.stButton > button {
            background: linear-gradient(90deg, #10B981 0%, #059669 100%) !important;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4) !important;
        }
        .download-btn-wrapper div.stButton > button:hover {
            background: linear-gradient(90deg, #059669 0%, #047857 100%) !important;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6) !important;
        }

        /* Flashcard Study Mode CSS */
        .flashcard-container {
            perspective: 1000px;
            width: 100%;
            max-width: 500px;
            height: 300px;
            margin: 20px auto;
            cursor: pointer;
        }
        
        .flashcard-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            border-radius: 16px;
        }
        
        .flashcard-inner.is-flipped {
            transform: rotateY(180deg);
        }
        
        .flashcard-side {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 16px;
            padding: 30px;
            box-sizing: border-box;
            border: 1px solid rgba(255,255,255,0.08);
        }
        
        .flashcard-front {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F8FAFC;
        }
        
        .flashcard-back {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            color: #F8FAFC;
            transform: rotateY(180deg);
        }
        
        .flashcard-text {
            font-size: 1.5rem;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .flashcard-hint {
            font-size: 0.85rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            position: absolute;
            bottom: 20px;
        }

        .flashcard-badge {
            position: absolute;
            top: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            background: rgba(255,255,255,0.08);
            padding: 4px 10px;
            border-radius: 9999px;
            color: #38BDF8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Logging area */
        .log-console {
            background-color: #020617 !important;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #38BDF8;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def init_session_state():
    """
    Initializes global session states with environment variables or safe defaults.
    Ensures single page and multi-page configurations remain in sync.
    """
    import os
    from dotenv import load_dotenv
    
    # Load dotenv from workspace root
    load_dotenv()
    
    # Retrieve key from st.secrets or os.environ fallback
    openai_key = ""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            openai_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
        
    if not openai_key:
        openai_key = os.getenv("OPENAI_API_KEY", "")
        
    defaults = {
        "openai_api_key": openai_key,
        "model_name": "gpt-4o-mini",
        "vision_model_name": "gpt-4o-mini",
        "chunk_size": 6000,
        "chunk_overlap": 500,
        "rate_limit_sleep": 1.0,
        "generated_cards": [],      # List of currently active generated cards
        "history": [],              # List of generated flashcard decks in history
        "active_deck_name": "My AI Flashcards",
        "study_index": 0,           # Flashcard index for study mode
        "study_flipped": False,     # Flip state of flashcard in study mode
        "quiz_score": 0,            # MCQ Quiz score tracker
        "quiz_questions": [],       # MCQs list
        "quiz_user_answers": {},    # Selected answers
        "subject_template": "General Study",
        "custom_subject_instructions": "Focus on key definitions, core concepts, critical facts, cause-and-effect relationships, and exam-worthy topics. Ensure clarity and academic rigor."
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def render_sidebar():
    """
    Renders custom sidebar navigation across all pages of the application.
    Removes the duplicate label emoji since we specify it via the 'icon' parameter.
    """
    st.sidebar.markdown("### 🧭 Flashcard Agent")
    st.sidebar.page_link("app.py", label="Home / Dashboard", icon="🏠")
    st.sidebar.page_link("pages/my_flashcards.py", label="Study Arena", icon="🧠")
    st.sidebar.page_link("pages/history.py", label="Deck History", icon="📅")
    st.sidebar.page_link("pages/templates.py", label="Subject Templates", icon="📚")
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.sidebar.page_link("pages/about.py", label="About Agent", icon="ℹ️")


