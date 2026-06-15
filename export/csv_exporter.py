import pandas as pd
from typing import List, Dict, Any

class CSVExporter:
    @staticmethod
    def export_to_csv(cards: List[Dict[str, Any]]) -> str:
        """
        Exports a list of flashcards to a CSV string.
        For Basic/Concept: Front, Back
        For Cloze: Front is used as Text, Back is used as Extra.
        """
        if not cards:
            return ""
            
        data = []
        for card in cards:
            front = card.get("front", "").strip()
            back = card.get("back", "").strip()
            
            # Anki CSV import formats can map:
            # Field 1 -> Front / Cloze Text
            # Field 2 -> Back / Extra
            # Field 3 -> Card Type
            # Field 4 -> Difficulty
            data.append({
                "Front/Text": front,
                "Back/Extra": back,
                "Type": card.get("type", "Basic"),
                "Difficulty": card.get("difficulty", "Intermediate")
            })
            
        df = pd.DataFrame(data)
        # Use index=False, line_terminator='\n' (or lineterminator for modern pandas)
        return df.to_csv(index=False, encoding='utf-8')
