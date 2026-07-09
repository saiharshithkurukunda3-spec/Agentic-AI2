import asyncio
import urllib.parse
from typing import List, Dict, Any
from functools import wraps
from lxml import html
import httpx

from app.utils.http_client import get_http_client
from app.utils.logging_config import logger

# Exponential Backoff Decorator for Async Operations
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

def clean_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    if '/l/?' in raw_url:
        parsed = urllib.parse.urlparse(raw_url)
        queries = urllib.parse.parse_qs(parsed.query)
        uddg_url = queries.get('uddg', [])
        if uddg_url:
            return uddg_url[0]
    if raw_url.startswith('//'):
        return 'https:' + raw_url
    return raw_url

@async_retry(tries=3, delay=1.0, backoff=2.0, exceptions=(Exception,))
async def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    logger.info("Executing DuckDuckGo web search via custom scraper", query=query, max_results=max_results)
    
    # Enforce maximum query length inside the search logic
    if len(query) > 250:
        query = query[:250]
        logger.warning("Query truncated to 250 characters", query=query)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    # Ensure query is properly url-encoded
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    # Reuse the central, connection-pooled client
    client = get_http_client()
    
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        tree = html.fromstring(response.text)
        results = []
        
        # Iterate over results divs in DuckDuckGo HTML layout
        for result in tree.xpath('//div[contains(@class, "result")]'):
            title_nodes = result.xpath('.//a[contains(@class, "result__a")]')
            snippet_nodes = result.xpath('.//a[contains(@class, "result__snippet")]')
            
            if title_nodes:
                title_node = title_nodes[0]
                title = title_node.text_content().strip()
                raw_url = title_node.get('href', '')
                
                # Extract clean target link from redirect parameters
                clean_link = clean_url(raw_url)
                
                snippet = snippet_nodes[0].text_content().strip() if snippet_nodes else ""
                
                results.append({
                    "title": title,
                    "url": clean_link,
                    "snippet": snippet
                })
                
        logger.info("Web search completed successfully", results_count=len(results))
        return results[:max_results]
        
    except Exception as e:
        logger.error("DuckDuckGo custom search scraper encountered an error", error=str(e))
        raise e
