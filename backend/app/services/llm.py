import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import httpx
from app.utils.config import settings
from app.utils.logging_config import logger
from app.utils.http_client import get_http_client
from app.services.search import async_retry

class LLMProvider(ABC):
    @abstractmethod
    async def generate_research_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Accepts a research query and context chunks and returns a dictionary:
        {
          "answer": "...",
          "relevance_score": int
        }
        """
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        self.api_key = settings.GEMINI_API_KEY

    @async_retry(tries=3, delay=1.5, backoff=2.0, exceptions=(httpx.HTTPError, json.JSONDecodeError))
    async def generate_research_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.api_key or self.api_key == "mock_key_for_testing":
            logger.warning("Gemini API key is not configured or in testing mode. Returning mock response.")
            return {
                "answer": f"[MOCK ANSWER] This is a mock response because the Gemini API key is not configured. Your query was: '{query}'",
                "relevance_score": 50
            }

        client = get_http_client()

        # Build context prompt
        context_str = ""
        for i, chunk in enumerate(context_chunks):
            context_str += f"Source [{i+1}]: {chunk['url']}\nContent: {chunk['text']}\n\n"

        system_instruction = (
            "You are VERITAS AI, a premium and objective research assistant.\n"
            "Analyze the search context provided below and synthesize a thorough, production-ready, grounded answer to the query.\n"
            "You must rely ONLY on the provided sources. Do not make up facts. If the sources do not contain the answer, state that.\n"
            "Assess the overall relevance of the sources to the query and provide a score between 0 and 100.\n"
            "Format your output strictly as a JSON object with keys 'answer' and 'relevance_score' (an integer).\n"
            "Do NOT include markdown syntax (like ```json) in the JSON payload itself, return plain JSON."
        )

        user_prompt = f"Query: {query}\n\nSearch Context Sources:\n{context_str}"

        # Setup Gemini payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }

        url = f"{self.api_url}?key={self.api_key}"
        logger.info("Sending prompt to Gemini API", query=query)
        
        response = await client.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30.0)
        response.raise_for_status()

        resp_json = response.json()
        
        # Parse output text from Gemini structure
        try:
            candidates = resp_json.get("candidates", [])
            if not candidates:
                logger.error("Gemini API returned no candidates", response=resp_json)
                raise ValueError("Empty response from LLM")
                
            text_response = candidates[0]["content"]["parts"][0]["text"]
            logger.info("Received raw response from Gemini", raw_text=text_response)
            
            parsed_response = json.loads(text_response)
            
            # Basic validation of keys
            if "answer" not in parsed_response or "relevance_score" not in parsed_response:
                raise KeyError("Missing required response keys 'answer' or 'relevance_score'")
                
            return {
                "answer": str(parsed_response["answer"]),
                "relevance_score": int(parsed_response["relevance_score"])
            }
        except (KeyError, IndexError, ValueError, json.JSONDecodeError) as e:
            logger.error("Failed to parse structured response from Gemini", error=str(e), response=resp_json)
            # Try to return fallback
            return {
                "answer": "Error: Received unparsable output from research model. Please try again.",
                "relevance_score": 0
            }
