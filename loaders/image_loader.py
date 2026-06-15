import base64
import logging
from typing import Dict, Any, List
from utils.ocr import ocr_image, is_easyocr_available
from openai import OpenAI

logger = logging.getLogger(__name__)

class ImageLoader:
    @staticmethod
    def extract_text(
        image_bytes: bytes,
        image_type: str = "image/png",
        use_vision: bool = False,
        openai_api_key: str = None,
        model_name: str = "gpt-4o-mini"
    ) -> Dict[str, Any]:
        """
        Extracts text/structural content from image bytes.
        If use_vision is True and an OpenAI key is provided, uses OpenAI's Vision model.
        Otherwise, falls back to local EasyOCR.
        """
        if use_vision:
            if not openai_api_key:
                return {
                    "success": False,
                    "message": "OpenAI API Key is required for Vision extraction.",
                    "text": ""
                }
            
            try:
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
                
                client = OpenAI(api_key=openai_api_key)
                
                # Setup vision prompt
                prompt = (
                    "You are a high-fidelity information extraction assistant. "
                    "Analyze the attached image. It may contain text, handwritten notes, tables, "
                    "diagrams, flowcharts, or formulas. "
                    "Extract and describe ALL structural information: "
                    "1. Translate any flowcharts or diagrams into descriptive text steps/relationships.\n"
                    "2. Format tables into Markdown tables.\n"
                    "3. Transcribe all text, keeping headings and formatting.\n"
                    "4. Output formulas in standard mathematical or LaTeX notation if applicable.\n"
                    "Provide a clean, comprehensive markdown representation of the image content."
                )
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{image_type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=2048,
                    temperature=0.2
                )
                
                extracted_text = response.choices[0].message.content
                return {
                    "success": True,
                    "message": "Successfully extracted content using OpenAI Vision model.",
                    "text": extracted_text
                }
                
            except Exception as e:
                logger.error(f"OpenAI Vision extraction failed: {e}. Falling back to EasyOCR.")
                # We can either fail or let it try EasyOCR. Let's log and fall back to EasyOCR if available.
                if is_easyocr_available():
                    try:
                        text = ocr_image(image_bytes)
                        return {
                            "success": True,
                            "message": f"OpenAI Vision failed ({e}). Successfully fell back to EasyOCR.",
                            "text": text
                        }
                    except Exception as ocr_err:
                        return {
                            "success": False,
                            "message": f"OpenAI Vision failed ({e}) and EasyOCR fallback failed: {ocr_err}",
                            "text": ""
                        }
                else:
                    return {
                        "success": False,
                        "message": f"OpenAI Vision failed: {e}. EasyOCR is not available.",
                        "text": ""
                    }
        else:
            # Direct EasyOCR path
            if not is_easyocr_available():
                return {
                    "success": False,
                    "message": "EasyOCR is not available. Check installation or try OpenAI Vision.",
                    "text": ""
                }
            try:
                text = ocr_image(image_bytes)
                return {
                    "success": True,
                    "message": "Successfully extracted text using EasyOCR.",
                    "text": text
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"EasyOCR extraction failed: {str(e)}",
                    "text": ""
                }
