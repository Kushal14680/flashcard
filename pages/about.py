import streamlit as st
from utils.ui_styles import inject_custom_css, init_session_state, render_sidebar

st.set_page_config(
    page_title="About - Flashcard Generator Agent",
    page_icon="ℹ️",
    layout="wide"
)

init_session_state()
inject_custom_css()

render_sidebar()

st.markdown('<div class="hero-section"><h1 class="hero-title">About the Agent</h1><p class="hero-subtitle">Learn about the architecture, pipelines, and import instructions</p></div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("📚 The Intelligent Processing Pipeline")
st.markdown(
    """
    The **Flashcard Generator Agent** converts raw, complex document formats into active-recall learning aids.
    Here is a breakdown of what happens behind the scenes:
    
    1. **Extraction**:
       - **PDFs** are parsed page-by-page using PyMuPDF (`fitz`), handling even dense multi-column texts.
       - **URLs** are parsed, cleaning scripts, style headers, nav widgets, and advertisements using `BeautifulSoup`.
       - **Images** undergo local high-speed optical character recognition via `EasyOCR` or are parsed through `OpenAI Vision` (`gpt-4o-mini`) to understand diagrams, math formulas, and tables.
    2. **Cleaning & Preprocessing**:
       - Text normalization strips excess padding, handles duplicate blocks, and cleans scanning glitches.
    3. **Recursive Chunking**:
       - The cleaner text is split into segments based on natural separators (paragraphs, sentences) to fit LLM window sizes without breaking ideas.
    4. **Concept Identification & Agent Generation**:
       - Using a structured **LangChain agent**, key definitions, formulas, rules, and facts are extracted to generate Basic, Cloze, or Concept flashcards.
    5. **Self-Correction (Review Agent)**:
       - The cards are analyzed by a review agent to fix typos, ensure valid Anki markup, deduplicate semantic overlaps, and improve clarity.
    6. **Export**:
       - Creates CSVs or packages decks into `.apkg` files using `genanki`.
    """
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("💡 Anki Import Instructions")
st.markdown(
    """
    To import the generated cards into your **Anki** deck:
    
    ### Using `.apkg` files (Recommended)
    1. Download the generated `.apkg` deck from the Home or History dashboard.
    2. Open your Anki desktop program or AnkiMobile app.
    3. Click **File** > **Import** (or press Ctrl+I / Cmd+I).
    4. Select the `.apkg` file you downloaded.
    5. The deck is automatically created with custom card CSS, badges, and layout templates!
    
    ### Using `.csv` files
    1. Download the generated `.csv` file.
    2. Open Anki, click **Import File**, and choose the `.csv`.
    3. Match the columns:
       - Field 1: Front / Cloze Text
       - Field 2: Back / Extra
       - Field 3: Card Type
       - Field 4: Difficulty
    4. Make sure to check "Allow HTML in fields" to support custom styling and line breaks.
    """
)
st.markdown('</div>', unsafe_allow_html=True)
