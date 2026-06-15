import os
import logging

logger = logging.getLogger(__name__)

_READER_INSTANCE = None
_EASYOCR_AVAILABLE = None

def get_easyocr_reader(languages=['en']):
    """
    Returns a shared instance of EasyOCR Reader.
    If EasyOCR is not installed or errors occur, returns None.
    """
    global _READER_INSTANCE, _EASYOCR_AVAILABLE
    
    if _EASYOCR_AVAILABLE is False:
        return None
        
    if _READER_INSTANCE is not None:
        return _READER_INSTANCE

    try:
        import easyocr
        logger.info("Initializing EasyOCR reader (this may download model files on first run)...")
        # Initialize reader (CPU mode by default unless GPU is available, easyocr handles this automatically)
        _READER_INSTANCE = easyocr.Reader(languages, gpu=False)
        _EASYOCR_AVAILABLE = True
        return _READER_INSTANCE
    except Exception as e:
        logger.warning(f"EasyOCR initialization failed: {e}. Falling back to non-OCR modes or OpenAI Vision.")
        _EASYOCR_AVAILABLE = False
        _READER_INSTANCE = None
        return None

def is_easyocr_available() -> bool:
    global _EASYOCR_AVAILABLE
    if _EASYOCR_AVAILABLE is None:
        # Trigger initialization check
        get_easyocr_reader()
    return bool(_EASYOCR_AVAILABLE)

def ocr_image(image_path_or_bytes) -> str:
    """
    Performs OCR on an image and returns the combined text.
    """
    reader = get_easyocr_reader()
    if not reader:
        raise ImportError(
            "EasyOCR is not initialized or failed to load. "
            "Please configure OpenAI Vision in Settings or verify your local PyTorch installation."
        )
    
    try:
        # EasyOCR can accept filepath, bytes or numpy array
        results = reader.readtext(image_path_or_bytes)
        # Combine text segments
        texts = [res[1] for res in results]
        return "\n".join(texts)
    except Exception as e:
        logger.error(f"Error during OCR execution: {e}")
        raise RuntimeError(f"OCR failed: {e}")
