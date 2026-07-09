from ddgs import DDGS
import asyncio
from typing import List, Dict
from app.utils.logging_config import logger

async def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    logger.info("Searching web with DDGS", query=query)

    def _search():
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))

    raw_results = await asyncio.to_thread(_search)

    results = []
    for item in raw_results:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("href", ""),
            "snippet": item.get("body", "")
        })

    logger.info("Search completed", results_count=len(results))
    return results