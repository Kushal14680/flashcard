import streamlit as st
import pandas as pd
import json
import datetime
import os
from utils.ui_styles import inject_custom_css, init_session_state, render_sidebar
from loaders.pdf_loader import PDFLoader
from loaders.url_loader import URLLoader
from loaders.image_loader import ImageLoader
from utils.chunker import RecursiveTextChunker
from utils.cleaner import clean_text
from agents.flashcard_agent import FlashcardAgent
from agents.review_agent import ReviewAgent
from export.csv_exporter import CSVExporter
from export.anki_exporter import AnkiExporter

# Set page config first
st.set_page_config(
    page_title="AI Flashcard Generator Agent",
    page_icon="⚡",
    layout="wide"
)

# Initialize states and global styling
init_session_state()
inject_custom_css()

# Custom clean sidebar navigation
render_sidebar()

# Hero Section
st.markdown(
    '<div class="hero-section">'
    '<h1 class="hero-title">Flashcard Generator Agent</h1>'
    '<p class="hero-subtitle">Convert PDFs, URLs, and Images into study-ready Anki decks using AI</p>'
    '</div>',
    unsafe_allow_html=True
)

# Active state variables for extraction
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "logs" not in st.session_state:
    st.session_state.logs = []

def add_log(msg: str):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {msg}")
    st.toast(msg)

def save_deck_to_history(deck_name: str, cards_list: list):
    os.makedirs("exports", exist_ok=True)
    slug = "".join([c if c.isalnum() else "_" for c in deck_name]).strip("_")
    timestamp = int(datetime.datetime.now().timestamp())
    filename = f"exports/deck_{slug}_{timestamp}.json"
    
    data = {
        "deck_name": deck_name,
        "created_at": datetime.datetime.now().isoformat(),
        "cards": cards_list
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    add_log(f"Saved deck '{deck_name}' to local history.")

# ----------------- STEP 1: Input Source -----------------
st.markdown("### 📥 Step 1: Input Sources")
source_tabs = st.tabs(["📄 Upload PDFs", "🔗 Enter URL", "🖼️ Upload Images"])

# PDF tab
with source_tabs[0]:
    uploaded_pdfs = st.file_uploader(
        "Choose one or multiple PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_uploader"
    )
    if uploaded_pdfs:
        st.info(f"Loaded {len(uploaded_pdfs)} PDF files.")
        if st.button("Extract PDF Text", key="btn_pdf_extract"):
            combined_text = []
            st.session_state.logs = []
            add_log("Starting text extraction from PDF(s)...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for file_idx, pdf_file in enumerate(uploaded_pdfs):
                pdf_bytes = pdf_file.read()
                loader = PDFLoader.extract_text(pdf_bytes)
                
                for step in loader:
                    if step["status"] == "processing":
                        status_text.text(f"File {file_idx + 1}/{len(uploaded_pdfs)}: {step['message']}")
                        progress_bar.progress((step["current_page"] / step["total_pages"]))
                    elif step["status"] == "completed" and step["text"]:
                        combined_text.append(step["text"])
                        add_log(f"Extracted {pdf_file.name} successfully.")
                    elif step["status"] == "error":
                        st.error(step["message"])
                        add_log(f"Error extracting {pdf_file.name}: {step['message']}")
                        
            if combined_text:
                st.session_state.extracted_text = "\n\n".join(combined_text)
                st.success(f"Successfully extracted text from all PDFs! Count: {len(st.session_state.extracted_text)} chars.")
                add_log("PDF Extraction Complete.")
            progress_bar.empty()
            status_text.empty()

# URL tab
with source_tabs[1]:
    url_input = st.text_input(
        "Paste article, documentation page, or blog URL",
        placeholder="https://example.com/article-to-study"
    )
    if url_input:
        if st.button("Extract Webpage Content", key="btn_url_extract"):
            st.session_state.logs = []
            add_log(f"Fetching URL: {url_input}")
            with st.spinner("Parsing web page content (removing ads/nav/scripts)..."):
                result = URLLoader.extract_text(url_input)
                if result["success"]:
                    st.session_state.extracted_text = result["text"]
                    st.success("Webpage text extracted successfully!")
                    add_log(result["message"])
                else:
                    st.error(result["message"])
                    add_log(f"URL extraction failed: {result['message']}")

# Images tab
with source_tabs[2]:
    uploaded_images = st.file_uploader(
        "Choose image files",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key="image_uploader"
    )
    use_vision = st.checkbox(
        "Use AI Vision Understanding (Recommended for diagrams, flowcharts, mathematical formulas, and tables)",
        value=True,
        help="If checked, uses OpenAI's Vision model to understand visual/structured data. If unchecked, uses local OCR (EasyOCR)."
    )
    
    if uploaded_images:
        st.image(uploaded_images, width=200, caption=[img.name for img in uploaded_images])
        
        if st.button("Extract Image Content", key="btn_image_extract"):
            st.session_state.logs = []
            add_log("Starting image text extraction...")
            combined_texts = []
            
            with st.spinner("Extracting content from image files..."):
                for img_file in uploaded_images:
                    img_bytes = img_file.read()
                    
                    # Determine MIME type
                    mime_type = "image/png"
                    if img_file.name.lower().endswith((".jpg", ".jpeg")):
                        mime_type = "image/jpeg"
                    elif img_file.name.lower().endswith(".webp"):
                        mime_type = "image/webp"
                        
                    res = ImageLoader.extract_text(
                        image_bytes=img_bytes,
                        image_type=mime_type,
                        use_vision=use_vision,
                        openai_api_key=st.session_state.openai_api_key,
                        model_name=st.session_state.vision_model_name
                    )
                    
                    if res["success"]:
                        combined_texts.append(res["text"])
                        add_log(f"Extracted content from {img_file.name}")
                    else:
                        st.error(f"Failed extracting {img_file.name}: {res['message']}")
                        add_log(f"Extraction failed: {res['message']}")
                        
            if combined_texts:
                st.session_state.extracted_text = "\n\n".join(combined_texts)
                st.success("Successfully processed images!")
                add_log("Image Extraction Complete.")

# Preview Extracted Text
if st.session_state.extracted_text:
    with st.expander("📝 View Extracted Text Preview", expanded=False):
        st.text_area("Extracted Context", value=st.session_state.extracted_text, height=250, disabled=True)

# Chat with document feature (Bonus)
if st.session_state.extracted_text:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("💬 Chat with Document")
    st.write("Ask questions about the uploaded content before generating flashcards:")
    
    chat_question = st.text_input("Ask a question:", placeholder="What are the main findings in this document?")
    if chat_question:
        if not st.session_state.openai_api_key:
            st.warning("⚠️ OpenAI API Key is missing. Configure it in Settings to use the chat feature.")
        else:
            with st.spinner("Thinking..."):
                try:
                    from langchain_openai import ChatOpenAI
                    from langchain_core.prompts import ChatPromptTemplate
                    
                    llm = ChatOpenAI(
                        api_key=st.session_state.openai_api_key,
                        model=st.session_state.model_name
                    )
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", "You are a helpful study assistant. Answer questions strictly based on the provided context.\n\nContext:\n{context}"),
                        ("user", "{question}")
                    ])
                    chain = prompt | llm
                    ans = chain.invoke({
                        "context": st.session_state.extracted_text[:6000], # limit context size
                        "question": chat_question
                    })
                    st.markdown(f"**Answer**: {ans.content}")
                except Exception as e:
                    st.error(f"Error chatting with document: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- STEP 2: Customization -----------------
st.markdown("### 🎛️ Step 2: Customization")
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

cust_col1, cust_col2, cust_col3, cust_col4 = st.columns(4)

with cust_col1:
    card_type = st.selectbox(
        "Card Type",
        options=["Mixed", "Basic", "Cloze"],
        help="Basic cards use Question/Answer. Cloze cards hide words using {{c1::...}} syntax."
    )

with cust_col2:
    num_cards = st.selectbox(
        "Number of Cards",
        options=["Auto", "10", "20", "50", "100"],
        help="Choose target deck size. Auto scales based on text length."
    )

with cust_col3:
    difficulty = st.selectbox(
        "Difficulty Level",
        options=["Mixed", "Beginner", "Intermediate", "Advanced"],
        help="Controls vocabulary complexity and depth of facts asked."
    )

with cust_col4:
    include_refs = st.checkbox(
        "Include Source References",
        value=True,
        help="Append the source identifier to the back of each flashcard."
    )
    enable_review = st.checkbox(
        "Enable AI Quality Review",
        value=False,
        help="Runs a second LLM pass to review cards for grammar and repetition. Turn off for maximum speed and token savings."
    )

# Selected Subject template display
st.markdown(
    f"📚 **Active Prompt Template Profile**: `{st.session_state.subject_template}` "
    f"*(Adjust this on the [Subject Templates](pages/templates.py) page)*"
)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- STEP 3: Generation -----------------
st.markdown("### ⚡ Step 3: Flashcard Generation")

if st.button("🚀 Generate Flashcards", key="btn_generate_cards"):
    if not st.session_state.extracted_text.strip():
        st.error("⚠️ Please load and extract some text source content first!")
    elif not st.session_state.openai_api_key:
        st.error("⚠️ OpenAI API Key is missing. Please set it in Settings page or your `.env` file first.")
    else:
        st.session_state.logs = []
        add_log("Initiating Flashcard Generation pipeline...")
        
        try:
            # 1. Clean extracted text
            with st.spinner("Cleaning text and filtering OCR noise..."):
                cleaned = clean_text(st.session_state.extracted_text)
                add_log("Text cleaned successfully.")
                
            # 2. Chunk text
            with st.spinner("Recursively chunking content..."):
                chunker = RecursiveTextChunker(
                    chunk_size=st.session_state.chunk_size,
                    overlap=st.session_state.chunk_overlap
                )
                chunks = chunker.split_text(cleaned)
                add_log(f"Text divided into {len(chunks)} chunks.")
                
            # 3. Generate raw cards
            raw_cards = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            agent = FlashcardAgent(
                api_key=st.session_state.openai_api_key,
                model_name=st.session_state.model_name
            )
            
            # Custom logging callback for agent
            def log_callback(msg):
                add_log(msg)
                status_text.text(msg)
                
            # Loop chunks
            raw_cards = agent.generate_flashcards(
                chunks=chunks,
                card_type=card_type,
                difficulty=difficulty,
                num_cards_target=num_cards,
                include_references=include_refs,
                source_name=st.session_state.active_deck_name,
                log_callback=log_callback
            )
            
            # 4. Review Agent Quality Check
            if raw_cards:
                status_text.text("Running Quality Review Agent...")
                reviewer = ReviewAgent(
                    api_key=st.session_state.openai_api_key,
                    model_name=st.session_state.model_name
                )
                import inspect
                sig = inspect.signature(reviewer.review_cards)
                if "enable_llm_review" in sig.parameters:
                    final_cards = reviewer.review_cards(raw_cards, enable_llm_review=enable_review, log_callback=log_callback)
                else:
                    final_cards = reviewer.review_cards(raw_cards, log_callback=log_callback)
                
                if final_cards:
                    st.session_state.generated_cards = final_cards
                    st.success(f"🎉 Generated {len(final_cards)} premium flashcards!")
                    
                    # Auto-save to history
                    save_deck_to_history(st.session_state.active_deck_name, final_cards)
                else:
                    st.warning("Quality reviewer filtered out all generated cards. Try refining settings.")
            else:
                st.warning("No cards were generated. Check your content or API key limits.")
                
            progress_bar.empty()
            status_text.empty()
            
        except Exception as err:
            st.error(f"Generation Pipeline halted with error: {err}")
            add_log(f"Critical error: {err}")

# Show Console Logs
if st.session_state.logs:
    with st.expander("🖥️ Live Logs & Status Console", expanded=True):
        st.markdown(
            f'<div class="log-console">{"<br>".join(st.session_state.logs)}</div>',
            unsafe_allow_html=True
        )

# ----------------- STEP 4: Review, Preview & Export -----------------
if st.session_state.generated_cards:
    st.markdown("---")
    st.markdown("### 📝 Step 4: Preview, Review & Export")
    
    # Deck renaming
    deck_name_input = st.text_input(
        "Set Deck Name",
        value=st.session_state.active_deck_name,
        help="This name will be saved in history and used inside Anki."
    )
    if deck_name_input != st.session_state.active_deck_name:
        st.session_state.active_deck_name = deck_name_input
        
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("💡 You can edit, delete, or add cards directly in the table below. Search and filter using the controls:")
    
    cards_df = pd.DataFrame(st.session_state.generated_cards)
    
    # Filter controls
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        search_query = st.text_input("Search Front/Back content:", placeholder="Type to search...")
    with col_f2:
        filter_type = st.selectbox("Filter Type:", options=["All", "Basic", "Cloze", "Concept"])
    with col_f3:
        filter_diff = st.selectbox("Filter Difficulty:", options=["All", "Beginner", "Intermediate", "Advanced"])
        
    # Apply filters
    filtered_df = cards_df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["front"].str.contains(search_query, case=False) |
            filtered_df["back"].str.contains(search_query, case=False)
        ]
    if filter_type != "All":
        filtered_df = filtered_df[filtered_df["type"] == filter_type]
    if filter_diff != "All":
        filtered_df = filtered_df[filtered_df["difficulty"] == filter_diff]
        
    # Interactive Grid
    edited_df = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        column_config={
            "front": st.column_config.TextColumn("Front (Question / Cloze phrase)", width="large", required=True),
            "back": st.column_config.TextColumn("Back (Answer / Extra)", width="large", required=True),
            "type": st.column_config.SelectboxColumn("Type", options=["Basic", "Cloze", "Concept"], required=True),
            "difficulty": st.column_config.SelectboxColumn("Difficulty", options=["Beginner", "Intermediate", "Advanced"], required=True)
        },
        use_container_width=True,
        key="card_editor"
    )
    
    # Save edits back to session state
    if st.button("Save Grid Edges"):
        # We merge back the edited rows
        # If rows were added or deleted, we sync the global state
        new_cards = edited_df.to_dict("records")
        st.session_state.generated_cards = new_cards
        st.success("Edits saved to active session!")
        # Resave historical file
        save_deck_to_history(st.session_state.active_deck_name, new_cards)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export options
    st.markdown("#### 📤 Export Formats")
    col_exp1, col_exp2 = st.columns(2)
    
    # Prepare exports
    final_cards_list = st.session_state.generated_cards
    
    with col_exp1:
        st.markdown('<div class="download-btn-wrapper">', unsafe_allow_html=True)
        csv_str = CSVExporter.export_to_csv(final_cards_list)
        st.download_button(
            label="📥 Download CSV Format",
            data=csv_str,
            file_name=f"{st.session_state.active_deck_name.replace(' ', '_')}.csv",
            mime="text/csv"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Standard comma-separated file format importable directly into Anki.")
        
    with col_exp2:
        st.markdown('<div class="download-btn-wrapper">', unsafe_allow_html=True)
        apkg_bytes = AnkiExporter.export_to_apkg(final_cards_list, st.session_state.active_deck_name)
        st.download_button(
            label="📥 Download APKG Package",
            data=apkg_bytes,
            file_name=f"{st.session_state.active_deck_name.replace(' ', '_')}.apkg",
            mime="application/octet-stream"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Pre-compiled Anki Deck package complete with custom visual layouts.")
