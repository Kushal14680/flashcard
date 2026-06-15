import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any

class URLLoader:
    @staticmethod
    def extract_text(url: str) -> Dict[str, Any]:
        """
        Crawls a URL, removes navigation, scripts, styles, advertisements,
        and extracts clean article text.
        """
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            return {
                "success": False,
                "message": f"HTTP request failed: {str(e)}",
                "text": ""
            }
            
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts, styles, and iframe elements
            for element in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav", "aside"]):
                element.decompose()
                
            # Remove ads or class structures commonly associated with widgets/social-sharing/promotions
            for tag in soup.find_all(class_=re.compile(r"ad-|promo|sidebar|menu|nav|share|widget|footer|header", re.I)):
                tag.decompose()
            for tag in soup.find_all(id=re.compile(r"ad-|promo|sidebar|menu|nav|share|widget|footer|header", re.I)):
                tag.decompose()
                
            # Attempt to find main content areas
            main_content = None
            for selector in ["article", "[role='main']", "main", "#content", ".post", ".entry-content"]:
                found = soup.select_one(selector)
                if found:
                    main_content = found
                    break
                    
            if not main_content:
                main_content = soup.body if soup.body else soup
                
            # Extract paragraphs and headings
            extracted_blocks = []
            for element in main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
                # Retain markdown-like structural indicators for headers
                text_content = element.get_text().strip()
                if not text_content:
                    continue
                    
                tag_name = element.name
                if tag_name.startswith("h"):
                    level = int(tag_name[1])
                    extracted_blocks.append(f"{'#' * level} {text_content}")
                else:
                    extracted_blocks.append(text_content)
                    
            cleaned_text = "\n\n".join(extracted_blocks)
            
            if len(cleaned_text.strip()) < 50:
                # If extraction was too aggressive, fall back to simple text extraction from body
                body_text = soup.body.get_text() if soup.body else soup.get_text()
                cleaned_text = re.sub(r'\n+', '\n', body_text)
                
            return {
                "success": True,
                "message": f"Successfully parsed page. Length: {len(cleaned_text)} characters.",
                "text": cleaned_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to parse content: {str(e)}",
                "text": ""
            }
