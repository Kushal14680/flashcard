import os
import time
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import openai

logger = logging.getLogger(__name__)

# Pydantic schemas for structured output
class FlashcardSchema(BaseModel):
    front: str = Field(description="The front side content of the flashcard. E.g. 'What is X?', 'Explain Y.', or a cloze sentence like 'The capital of France is {{c1::Paris}}'")
    back: str = Field(description="The back side content of the flashcard. E.g. the definition, answer, formula, or extra explanation. For Cloze cards, this can be extra background details.")
    type: str = Field(description="Type of the card. Must be exactly 'Basic', 'Cloze', or 'Concept'")
    difficulty: str = Field(description="Difficulty level of the card. Must be exactly 'Beginner', 'Intermediate', or 'Advanced'")

class FlashcardListSchema(BaseModel):
    cards: List[FlashcardSchema]

# Setup tenacity retry strategy for handling OpenAI Rate Limits
def is_rate_limit_error(exception):
    return isinstance(exception, openai.RateLimitError)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    retry=retry_if_exception_type(openai.RateLimitError),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Rate limit hit. Retrying in {retry_state.next_action.sleep} seconds..."
    )
)
def _call_llm_with_retry(llm, prompt_value):
    """
    Wrapper to call ChatOpenAI with retry logic.
    """
    return llm.invoke(prompt_value)

class FlashcardAgent:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini", temperature: float = 0.3):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError("OpenAI API Key is missing. Please set it in Settings or your .env file.")

    def generate_flashcards(
        self,
        chunks: List[str],
        card_type: str = "Mixed",
        difficulty: str = "Mixed",
        num_cards_target: str = "Auto",
        include_references: bool = False,
        source_name: str = "Document",
        log_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Generates flashcards from a list of text chunks.
        Controls rates, chunks inputs, and aggregates the results.
        """
        if not chunks:
            return []
            
        # Parse target number of cards
        if num_cards_target == "Auto":
            # Roughly 3-5 cards per 2000 character chunk
            cards_per_chunk = 4
        else:
            try:
                total_target = int(num_cards_target)
                cards_per_chunk = max(1, round(total_target / len(chunks)))
            except ValueError:
                cards_per_chunk = 4

        # Set up ChatOpenAI with structured output
        llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model_name,
            temperature=self.temperature
        )
        
        # We bind the Pydantic schema to the model
        structured_llm = llm.with_structured_output(FlashcardListSchema)
        
        # System instructions
        system_prompt = (
            "You are an expert educational designer and flashcard generator.\n"
            "Your task is to analyze the provided text chunk and extract high-quality, exam-worthy flashcards.\n\n"
            "Focus on identifying:\n"
            "- Key concepts and their definitions\n"
            "- Important formulas or technical equations\n"
            "- Critical facts, dates, and names\n"
            "- Cause-and-effect relationships\n"
            "- Real-world examples or applications\n\n"
            "Card Type Guidance:\n"
            "- Basic Cards: Front has a concise question, Back has a direct answer. (e.g. Front: 'What is RAG?', Back: 'Retrieval Augmented Generation...')\n"
            "- Cloze Cards: Front is a sentence containing one or more cloze deletions formatted as {{c1::hidden text}}. E.g. 'The capital of France is {{c1::Paris}}'. Use {{c1::text}} syntax carefully. The back can contain extra detail/explanation.\n"
            "- Concept Cards: Front is a prompt to explain/describe a key term. E.g. Front: 'Explain overfitting.', Back: 'Overfitting happens when a model learns noise in training data...' \n\n"
            "Difficulty Guidelines:\n"
            "- Beginner: Simple recognition, direct vocabulary terms, basic factual recall.\n"
            "- Intermediate: Application of principles, multi-step explanations, relationship linking.\n"
            "- Advanced: Nuanced edge cases, complex system analysis, mathematical implications.\n\n"
            "Format your response strictly as a JSON object matching the requested schema."
        )

        user_template = (
            "Text source chunk:\n"
            "-----------------\n"
            "{text_chunk}\n"
            "-----------------\n\n"
            "Generate exactly {cards_count} flashcards from this text.\n"
            "Target Card Type: {card_type}\n"
            "Target Difficulty: {difficulty}\n"
        )
        
        prompt_tmpl = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_template)
        ])
        
        all_generated_cards = []
        
        for idx, chunk in enumerate(chunks):
            if log_callback:
                log_callback(f"Processing chunk {idx + 1}/{len(chunks)}...")
                
            prompt_value = prompt_tmpl.format_messages(
                text_chunk=chunk,
                cards_count=cards_per_chunk,
                card_type=card_type,
                difficulty=difficulty
            )
            
            try:
                # Add delay between calls to mitigate rate limiting if there are many chunks
                if idx > 0:
                    time.sleep(1.0)
                    
                # Invoke model with retry logic
                result = _call_llm_with_retry(structured_llm, prompt_value)
                
                # Extract and format cards
                for card in result.cards:
                    card_dict = {
                        "front": card.front,
                        "back": card.back,
                        "type": card.type,
                        "difficulty": card.difficulty
                    }
                    
                    # Ensure valid values
                    if card_dict["type"] not in ["Basic", "Cloze", "Concept"]:
                        card_dict["type"] = "Basic"
                    if card_dict["difficulty"] not in ["Beginner", "Intermediate", "Advanced"]:
                        card_dict["difficulty"] = "Intermediate"
                        
                    if include_references:
                        # Append source reference to the back of the card
                        ref_suffix = f"<br><br><small><i>Source: {source_name} (Chunk {idx + 1})</i></small>"
                        card_dict["back"] = card_dict["back"] + ref_suffix
                        
                    all_generated_cards.append(card_dict)
                    
            except Exception as e:
                logger.error(f"Error generating cards for chunk {idx + 1}: {e}")
                if log_callback:
                    log_callback(f"⚠️ Error generating cards for chunk {idx + 1}: {e}")
                    
        if log_callback:
            log_callback(f"Generation completed! Extracted {len(all_generated_cards)} raw cards in total.")
            
        return all_generated_cards
