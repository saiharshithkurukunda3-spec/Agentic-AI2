import asyncio
import ipaddress
import socket
import urllib.parse
from typing import List, Dict, Any, Optional
import httpx
import trafilatura
from app.utils.http_client import get_http_client
from app.utils.logging_config import logger
from app.services.search import async_retry

def is_safe_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        return not (
            ip.is_private or
            ip.is_loopback or
            ip.is_link_local or
            ip.is_multicast or
            ip.is_reserved or
            ip.is_unspecified
        )
    except ValueError:
        return False

async def is_safe_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            logger.warning("SSRF Check: Blocked non-http/https URL", url=url)
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False

        # Check if the hostname itself is a raw IP address
        try:
            # If it resolves directly as an IP, check it
            ipaddress.ip_address(hostname)
            if not is_safe_ip(hostname):
                logger.warning("SSRF Check: Blocked raw private IP URL", url=url)
                return False
            return True
        except ValueError:
            pass

        # Resolve hostname to IPs asynchronously
        loop = asyncio.get_event_loop()
        addr_info = await loop.getaddrinfo(hostname, None)
        
        for info in addr_info:
            ip = info[4][0]
            if not is_safe_ip(ip):
                logger.warning("SSRF Check: Host resolved to unsafe IP, blocking URL", url=url, ip=ip)
                return False
                
        return True
    except Exception as e:
        logger.error("SSRF Check: Error resolving URL", url=url, error=str(e))
        return False

@async_retry(tries=2, delay=0.5, backoff=2.0, exceptions=(httpx.HTTPError,))
async def fetch_page_content(client: httpx.AsyncClient, url: str) -> str:
    # Set a short timeout for scraping
    response = await client.get(url, timeout=6.0)
    response.raise_for_status()
    return response.text

async def scrape_url(url: str, client: Optional[httpx.AsyncClient] = None) -> Optional[str]:
    # Check SSRF safety
    if not await is_safe_url(url):
        return None

    if client is None:
        client = get_http_client()

    try:
        logger.info("Scraping webpage", url=url)
        html_content = await fetch_page_content(client, url)
        
        # Extract plain text using trafilatura
        extracted_text = trafilatura.extract(html_content, no_fallback=False)
        if not extracted_text:
            # Fallback to bare trafilatura parsing
            extracted_text = trafilatura.baseline(html_content)[1]
            
        if extracted_text:
            # Enforce max content limits per page (15000 characters)
            if len(extracted_text) > 15000:
                extracted_text = extracted_text[:15000]
                logger.warning("Content limit exceeded, truncated page text to 15,000 characters", url=url)
            return extracted_text.strip()
            
        logger.warning("No extractable content found", url=url)
        return None
    except Exception as e:
        logger.warning("Failed to scrape webpage", url=url, error=str(e))
        return None

async def scrape_multiple_urls(urls: List[str]) -> Dict[str, str]:
    # Cache duplicate URLs during a request
    unique_urls = list(set(urls))
    client = get_http_client()
    
    # Limit concurrent downloads to max 5 concurrent requests using a Semaphore
    semaphore = asyncio.Semaphore(5)
    
    async def sem_scrape(url: str):
        async with semaphore:
            content = await scrape_url(url, client)
            return url, content

    tasks = [sem_scrape(url) for url in unique_urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    scraped_data = {}
    for res in results:
        if isinstance(res, tuple):
            url, content = res
            if content:
                scraped_data[url] = content
                
    return scraped_data
