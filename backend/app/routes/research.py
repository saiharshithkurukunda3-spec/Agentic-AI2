import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from app.auth.utils import get_current_user
from app.database.mongodb import get_db
from app.services.search import search_web
from app.services.scraper import scrape_multiple_urls
from app.services.rag import retrieve_top_chunks, rag_cache
from app.services.llm import GeminiProvider
from app.utils.logging_config import logger

router = APIRouter()
gemini_provider = GeminiProvider()

class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=250)

class SourceResponse(BaseModel):
    title: str
    url: str
    relevance_score: float

class ResearchResponse(BaseModel):
    answer: str
    sources: List[SourceResponse]
    relevance_score: int

@router.post("/", response_model=ResearchResponse)
async def perform_research(request_data: ResearchRequest, current_user: dict = Depends(get_current_user)):
    query = request_data.query.strip()
    user_id = current_user["_id"]

    logger.info("New research request received", query=query, user_id=user_id)

    # 1. Check in-memory cache
    cached_response = await rag_cache.get(query)
    if cached_response:
        logger.info("Returning cached research result", query=query)
        # If cache hits, we still log history? History is typically unique per search.
        # But if they searched it before, it's already in history. We can just return it.
        return cached_response

    # 2. Search the web using DuckDuckGo
    try:
        search_results = await search_web(query, max_results=5)
    except Exception as e:
        logger.error("Web search failed", error=str(e))
        search_results = []

    if not search_results:
        # Graceful degradation if search fails
        logger.warning("No search results found for query", query=query)
        result = {
            "answer": "I was unable to retrieve search results for this query. Please check your network connection or query context.",
            "sources": [],
            "relevance_score": 0
        }
        return result

    # 3. Extract web URLs and download content concurrently
    urls = [res["url"] for res in search_results if res.get("url")]
    scraped_data = {}
    if urls:
        try:
            scraped_data = await scrape_multiple_urls(urls)
        except Exception as e:
            logger.error("Web scraping failed", error=str(e))
            scraped_data = {}

    # If scraping failed for all but we have snippet search results, use snippets as context
    if not scraped_data:
        logger.warning("Web scraping retrieved no page content, falling back to DDGS search snippets")
        scraped_data = {
            res["url"]: res["snippet"]
            for res in search_results
            if res.get("url") and res.get("snippet")
        }

    # 4. Chunk text and rank chunks via BM25 keyword scoring
    top_chunks = retrieve_top_chunks(query, scraped_data, top_n=6)

    # 5. Synthesize grounded answer using Gemini Provider
    try:
        llm_response = await gemini_provider.generate_research_answer(query, top_chunks)
        answer = llm_response.get("answer", "No answer generated.")
        relevance_score = llm_response.get("relevance_score", 0)
    except Exception as e:
        logger.error("Failed to generate answer via LLM", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error generating answer from AI provider."
        )

    # Map sources and their respective BM25 scores
    # We consolidate chunks back to distinct sources to avoid showing duplicates
    unique_sources = {}
    for chunk in top_chunks:
        url = chunk["url"]
        score = chunk["score"]
        # Find match title from original search results
        title = next((res["title"] for res in search_results if res["url"] == url), "Source Link")
        
        if url not in unique_sources or score > unique_sources[url]["relevance_score"]:
            unique_sources[url] = {
                "title": title,
                "url": url,
                "relevance_score": round(score, 2)
            }

    sources_list = list(unique_sources.values())

    # Build final response payload
    research_result = {
        "answer": answer,
        "sources": sources_list,
        "relevance_score": relevance_score
    }

    # 6. Save in cache
    await rag_cache.set(query, research_result)

    # 7. Log and Save to MongoDB user history
    db = get_db()
    if db is not None:
        try:
            history_doc = {
                "user_id": user_id,
                "query": query,
                "response": answer,
                "sources": [
                    {
                        "title": s["title"],
                        "url": s["url"],
                        "relevance_score": s["relevance_score"]
                    }
                    for s in sources_list
                ],
                "timestamp": datetime.datetime.utcnow()
            }
            await db["history"].insert_one(history_doc)
            logger.info("Saved search query to user history", user_id=user_id)
        except Exception as e:
            logger.error("Failed to save query to MongoDB search history", error=str(e))
    else:
        logger.warning("Database unavailable, query not saved to search history")

    return research_result
