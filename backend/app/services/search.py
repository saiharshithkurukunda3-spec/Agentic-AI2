import asyncio
from typing import List, Dict, Any
from functools import wraps
import httpx

from app.utils.config import settings
from app.utils.http_client import get_http_client
from app.utils.logging_config import logger

# Exponential Backoff Decorator for Async Operations (exported for backward compatibility)
def async_retry(tries: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (Exception,)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            m_tries, m_delay = tries, delay
            while m_tries > 1:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(
                        f"Retrying {func.__name__} due to failure",
                        error=str(e),
                        delay=m_delay,
                        retries_left=m_tries - 1
                    )
                    await asyncio.sleep(m_delay)
                    m_tries -= 1
                    m_delay *= backoff
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    logger.info("Searching Tavily API", query=query, max_results=max_results)
    
    if len(query) > 250:
        query = query[:250]
        logger.warning("Query truncated to 250 characters for search", query=query)

    url = "https://api.tavily.com/search"
    
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False
    }
    
    client = get_http_client()
    
    try:
        response = await client.post(url, json=payload, timeout=10.0)
        
        if response.status_code != 200:
            logger.error(
                "Tavily Search API returned non-200 response",
                status_code=response.status_code,
                response_text=response.text
            )
            return []
            
        data = response.json()
        results_list = data.get("results", []) if isinstance(data, dict) else []
        
        results = []
        if isinstance(results_list, list):
            for item in results_list:
                if isinstance(item, dict):
                    results.append({
                        "title": str(item.get("title", "")),
                        "url": str(item.get("url", "")),
                        "snippet": str(item.get("content", ""))
                    })
                    
        logger.info("Search completed", results_count=len(results))
        return results
        
    except httpx.TimeoutException as e:
        logger.error("Tavily Search API request timed out", error=str(e))
        return []
    except httpx.HTTPError as e:
        logger.error("Tavily Search API HTTP connection error", error=str(e))
        return []
    except ValueError as e:
        logger.error("Tavily Search API returned invalid JSON response", error=str(e))
        return []
    except Exception as e:
        logger.error("Unexpected error during Tavily Search API query", error=str(e))
        return []
