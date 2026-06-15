import genanki
import hashlib
import os
import tempfile
from typing import List, Dict, Any

# Custom CSS for gorgeous rendering inside Anki
CARD_CSS = """
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 19px;
  text-align: left;
  color: #2D3748;
  background-color: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 12px;
  padding: 24px;
  max-width: 600px;
  margin: 20px auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 11px;
  border-bottom: 1px solid #EDF2F7;
  padding-bottom: 8px;
}
.badge {
  background-color: #EDF2F7;
  color: #4A5568;
  padding: 4px 10px;
  border-radius: 9999px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.difficulty-Beginner {
  background-color: #C6F6D5;
  color: #22543D;
}
.difficulty-Intermediate {
  background-color: #FEFCBF;
  color: #744210;
}
.difficulty-Advanced {
  background-color: #FED7D7;
  color: #742A2A;
}
.card-content {
  line-height: 1.6;
  word-wrap: break-word;
}
.front-content {
  font-weight: 600;
  font-size: 21px;
  color: #1A202C;
}
.back-content {
  font-size: 18px;
  color: #2D3748;
  margin-top: 10px;
}
#answer {
  border: 0;
  height: 1px;
  background: #E2E8F0;
  margin: 16px 0;
}
.cloze {
  color: #3182CE;
  font-weight: bold;
  background-color: #EBF8FF;
  padding: 0 4px;
  border-radius: 4px;
}
"""

# HTML templates for Basic Cards
BASIC_FRONT_HTML = """
<div class="card basic-card">
  <div class="card-header">
    <span class="badge">{{Type}}</span>
    <span class="badge difficulty-{{Difficulty}}">{{Difficulty}}</span>
  </div>
  <div class="card-content front-content">{{Front}}</div>
</div>
"""

BASIC_BACK_HTML = """
<div class="card basic-card">
  <div class="card-header">
    <span class="badge">{{Type}}</span>
    <span class="badge difficulty-{{Difficulty}}">{{Difficulty}}</span>
  </div>
  <div class="card-content front-content">{{Front}}</div>
  <hr id="answer">
  <div class="card-content back-content">{{Back}}</div>
</div>
"""

# HTML templates for Cloze Cards
CLOZE_FRONT_HTML = """
<div class="card cloze-card">
  <div class="card-header">
    <span class="badge">{{Type}}</span>
    <span class="badge difficulty-{{Difficulty}}">{{Difficulty}}</span>
  </div>
  <div class="card-content front-content">{{cloze:Text}}</div>
</div>
"""

CLOZE_BACK_HTML = """
<div class="card cloze-card">
  <div class="card-header">
    <span class="badge">{{Type}}</span>
    <span class="badge difficulty-{{Difficulty}}">{{Difficulty}}</span>
  </div>
  <div class="card-content front-content">{{cloze:Text}}</div>
  <hr id="answer">
  <div class="card-content back-content">{{Extra}}</div>
</div>
"""

# Define unique Model IDs
BASIC_MODEL_ID = 1607392319
CLOZE_MODEL_ID = 1607392320

# Create Models
BASIC_MODEL = genanki.Model(
    BASIC_MODEL_ID,
    'Flashcard Agent Basic Model',
    fields=[
        {'name': 'Front'},
        {'name': 'Back'},
        {'name': 'Type'},
        {'name': 'Difficulty'},
    ],
    templates=[
        {
            'name': 'Basic Card Template',
            'qfmt': BASIC_FRONT_HTML,
            'afmt': BASIC_BACK_HTML,
        },
    ],
    css=CARD_CSS
)

CLOZE_MODEL = genanki.Model(
    CLOZE_MODEL_ID,
    'Flashcard Agent Cloze Model',
    fields=[
        {'name': 'Text'},
        {'name': 'Extra'},
        {'name': 'Type'},
        {'name': 'Difficulty'},
    ],
    templates=[
        {
            'name': 'Cloze Card Template',
            'qfmt': CLOZE_FRONT_HTML,
            'afmt': CLOZE_BACK_HTML,
        },
    ],
    css=CARD_CSS,
    model_type=genanki.Model.CLOZE
)

class AnkiExporter:
    @staticmethod
    def generate_deck_id(deck_name: str) -> int:
        """Generates a stable integer ID based on the deck name."""
        h = hashlib.md5(deck_name.encode('utf-8')).hexdigest()
        # Take first 8 chars and parse as base-16 integer
        return int(h[:8], 16)

    @staticmethod
    def export_to_apkg(cards: List[Dict[str, Any]], deck_name: str) -> bytes:
        """
        Creates an Anki deck from the flashcard list and packages it.
        Returns the deck file content in bytes.
        """
        if not cards:
            return b""
            
        deck_id = AnkiExporter.generate_deck_id(deck_name)
        deck = genanki.Deck(deck_id, deck_name)
        
        for card in cards:
            front = card.get("front", "").strip()
            back = card.get("back", "").strip()
            card_type = card.get("type", "Basic")
            difficulty = card.get("difficulty", "Intermediate")
            
            # Map types
            if card_type in ["Basic", "Concept"]:
                note = genanki.Note(
                    model=BASIC_MODEL,
                    fields=[front, back, card_type, difficulty]
                )
                deck.add_note(note)
            elif card_type == "Cloze":
                # For Cloze, front needs to contain the cloze syntax, e.g., {{c1::Paris}}
                # Back acts as Extra info
                note = genanki.Note(
                    model=CLOZE_MODEL,
                    fields=[front, back, card_type, difficulty]
                )
                deck.add_note(note)
                
        # Package deck to file
        package = genanki.Package(deck)
        
        # Save to temporary file and read bytes
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, f"{deck_id}.apkg")
        
        try:
            package.write_to_file(temp_file_path)
            with open(temp_file_path, "rb") as f:
                apkg_bytes = f.read()
            return apkg_bytes
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
        return b""
