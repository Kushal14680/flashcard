import re

def clean_text(text: str) -> str:
    """
    Cleans raw extracted text by:
    1. Normalizing whitespace (tabs, newlines, spaces)
    2. Deduplicating consecutive identical blocks or lines
    3. Filtering out obvious OCR garbage characters/patterns
    4. Keeping headings/Markdown structures intact
    """
    if not text:
        return ""

    # Replace multiple spaces with a single space
    # but keep newlines for paragraph separation
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Strip trailing/leading spaces
        trimmed = line.strip()
        
        # Remove lines that look like OCR noise (e.g. random punctuation clusters, single letters)
        if len(trimmed) > 0:
            # Check if line is mostly punctuation/gibberish
            non_space_chars = len(trimmed)
            special_chars = len(re.sub(r'[a-zA-Z0-9\s]', '', trimmed))
            if special_chars / non_space_chars > 0.5 and len(trimmed) < 10:
                continue # Skip noise line
                
            # Normalize whitespace within the line
            normalized_line = re.sub(r'\s+', ' ', trimmed)
            cleaned_lines.append(normalized_line)
        else:
            cleaned_lines.append("")

    # Join lines back
    text = '\n'.join(cleaned_lines)
    
    # Remove consecutive duplicate lines
    lines = text.split('\n')
    deduped_lines = []
    for line in lines:
        if not deduped_lines or line != deduped_lines[-1] or line == "":
            deduped_lines.append(line)
            
    text = '\n'.join(deduped_lines)
    
    # Clean multiple consecutive empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
