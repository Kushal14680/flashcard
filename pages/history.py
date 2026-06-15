import streamlit as st
import os
import json
import datetime
from utils.ui_styles import inject_custom_css, init_session_state, render_sidebar
from export.csv_exporter import CSVExporter
from export.anki_exporter import AnkiExporter

st.set_page_config(
    page_title="History - Flashcard Generator Agent",
    page_icon="📅",
    layout="wide"
)

init_session_state()
inject_custom_css()

render_sidebar()

st.markdown('<div class="hero-section"><h1 class="hero-title">Deck History</h1><p class="hero-subtitle">Access, reload, and manage your saved flashcard collections</p></div>', unsafe_allow_html=True)

exports_dir = "exports"

# Create exports directory if it doesn't exist
if not os.path.exists(exports_dir):
    os.makedirs(exports_dir)

# Read all json files
deck_files = [f for f in os.listdir(exports_dir) if f.endswith(".json")]

if not deck_files:
    st.info("ℹ️ No historical decks found. Create and generate flashcards on the Home dashboard to save them here!")
    st.stop()

# Load deck data
decks = []
for file in deck_files:
    filepath = os.path.join(exports_dir, file)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["filename"] = file
            data["filepath"] = filepath
            # Parse datetime
            created_dt = datetime.datetime.fromisoformat(data["created_at"])
            data["created_formatted"] = created_dt.strftime("%b %d, %Y - %I:%M %p")
            decks.append(data)
    except Exception as e:
        # Ignore malformed files
        pass

# Sort decks by creation time desc
decks.sort(key=lambda x: x.get("created_at", ""), reverse=True)

# Render decks list
for idx, deck in enumerate(decks):
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col_info, col_actions = st.columns([3, 2])
    
    with col_info:
        st.subheader(deck.get("deck_name", "Untitled Deck"))
        st.write(f"📅 **Generated**: {deck.get('created_formatted')}")
        st.write(f"🎴 **Cards count**: {len(deck.get('cards', []))}")
        
    with col_actions:
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            # Load active deck action
            if st.button("📥 Load Deck", key=f"load_{idx}"):
                st.session_state.generated_cards = deck["cards"]
                st.session_state.active_deck_name = deck["deck_name"]
                st.session_state.study_index = 0
                st.session_state.study_flipped = False
                st.session_state.quiz_questions = []
                st.toast(f"Loaded '{deck['deck_name']}' into study arena!", icon="🚀")
                st.success("Deck loaded! Redirecting...")
                
        with btn_col2:
            # Delete action
            if st.button("🗑️ Delete Deck", key=f"delete_{idx}"):
                try:
                    os.remove(deck["filepath"])
                    st.toast("Deck deleted successfully!", icon="🗑️")
                    st.rerun()
                except Exception as err:
                    st.error(f"Error deleting deck: {err}")
                    
        # Exporters directly on history card
        st.write("")
        exp_col1, exp_col2 = st.columns(2)
        
        cards_list = deck.get("cards", [])
        deck_name = deck.get("deck_name", "Anki Deck")
        
        with exp_col1:
            csv_str = CSVExporter.export_to_csv(cards_list)
            st.download_button(
                label="📥 Download CSV",
                data=csv_str,
                file_name=f"{deck_name.replace(' ', '_')}.csv",
                mime="text/csv",
                key=f"csv_dl_{idx}"
            )
            
        with exp_col2:
            apkg_bytes = AnkiExporter.export_to_apkg(cards_list, deck_name)
            st.download_button(
                label="📥 Download APKG",
                data=apkg_bytes,
                file_name=f"{deck_name.replace(' ', '_')}.apkg",
                mime="application/octet-stream",
                key=f"apkg_dl_{idx}"
            )
            
    st.markdown('</div>', unsafe_allow_html=True)
