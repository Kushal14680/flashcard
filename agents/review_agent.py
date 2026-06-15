import logging
import os
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agents.flashcard_agent import FlashcardSchema, FlashcardListSchema, _call_llm_with_retry

logger = logging.getLogger(__name__)

class ReviewAgent:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini", temperature: float = 0.1):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError("OpenAI API Key is missing. Please set it in Settings or your .env file.")

    def review_cards(self, cards: List[Dict[str, Any]], enable_llm_review: bool = True, log_callback=None) -> List[Dict[str, Any]]:
        """
        Runs quality control over generated cards.
        1. Exact duplicate removal (rule-based).
        2. Format verification (rules).
        3. LLM-based batch clean and refinement.
        """
        if not cards:
            return []

        if log_callback:
            log_callback(f"Starting quality review on {len(cards)} cards...")

        # 1. Rule-based Deduplication & Basic Formats
        unique_cards = []
        seen_fronts = set()
        
        for card in cards:
            front = card.get("front", "").strip()
            back = card.get("back", "").strip()
            card_type = card.get("type", "Basic").strip()
            difficulty = card.get("difficulty", "Intermediate").strip()
            
            if not front or not back:
                continue # Skip empty cards
                
            # Check for exact duplicate front
            normalized_front = front.lower()
            if normalized_front in seen_fronts:
                continue
            seen_fronts.add(normalized_front)
            
            # Cloze structural check: If type is Cloze but has no brackets, try to convert it or fix it.
            if card_type == "Cloze" and "{{" not in front:
                # If there's no cloze deletion but it was flagged as Cloze, let's treat it as Basic
                card_type = "Basic"
                
            unique_cards.append({
                "front": front,
                "back": back,
                "type": card_type,
                "difficulty": difficulty
            })

        if log_callback:
            log_callback(f"Rule-based check reduced cards from {len(cards)} to {len(unique_cards)} (removed duplicates/blanks).")

        if not unique_cards:
            return []

        if not enable_llm_review:
            if log_callback:
                log_callback(f"LLM Quality Review is disabled. Instantly returning {len(unique_cards)} deduplicated cards.")
            return unique_cards

        # 2. LLM-based Refinement in batches (e.g. batch size of 20)
        llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            temperature=self.temperature
        )
        structured_llm = llm.with_structured_output(FlashcardListSchema)
        
        system_prompt = (
            "You are a meticulous copyeditor and exam prep reviewer.\n"
            "Review the list of educational flashcards and return a refined list. "
            "Your tasks:\n"
            "1. Correct spelling, punctuation, and grammatical mistakes.\n"
            "2. Make questions/fronts clearer, more concise, and academically sound.\n"
            "3. Ensure Cloze cards are correctly formatted with double curly braces like: The capital of France is {{c1::Paris}}.\n"
            "4. Eliminate any cards that have trivial questions, or cards that are repetitive/semantic duplicates of other cards in the batch.\n"
            "5. Maintain card properties (type and difficulty) unless they are incorrect.\n\n"
            "Output your reviewed list matching the requested JSON schema."
        )
        
        user_template = (
            "Review the following flashcards:\n"
            "-----------------\n"
            "{cards_json}\n"
            "-----------------\n"
        )
        
        prompt_tmpl = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_template)
        ])
        
        refined_cards = []
        batch_size = 20
        
        for i in range(0, len(unique_cards), batch_size):
            batch = unique_cards[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(unique_cards) + batch_size - 1) // batch_size
            
            if log_callback:
                log_callback(f"Reviewing batch {batch_num}/{total_batches}...")

            # Format cards as basic dictionary representations for LLM
            batch_input = [{"index": idx, "front": c["front"], "back": c["back"], "type": c["type"], "difficulty": c["difficulty"]} for idx, c in enumerate(batch)]
            
            prompt_value = prompt_tmpl.format_messages(cards_json=str(batch_input))
            
            try:
                # Delay to mitigate rate limits
                if i > 0:
                    time.sleep(1.0)
                    
                result = _call_llm_with_retry(structured_llm, prompt_value)
                
                for card in result.cards:
                    refined_cards.append({
                        "front": card.front,
                        "back": card.back,
                        "type": card.type,
                        "difficulty": card.difficulty
                    })
            except Exception as e:
                logger.error(f"Error reviewing batch {batch_num}: {e}")
                if log_callback:
                    log_callback(f"⚠️ Error reviewing batch {batch_num}: {e}. Keeping raw cards from this batch.")
                # Fallback: keep raw cards if review failed
                refined_cards.extend(batch)
                
        if log_callback:
            log_callback(f"Review completed. Final count: {len(refined_cards)} premium flashcards ready.")

        return refined_cards
