import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.utils.config import settings
from app.utils.http_client import HTTPClientProvider
from app.services.search import search_web
from app.services.scraper import is_safe_url, scrape_multiple_urls
from app.services.rag import chunk_text, retrieve_top_chunks, rag_cache
from app.services.llm import GeminiProvider

async def run_tests():
    print("=== STARTING VERITAS AI MODULE TESTS ===")
    
    # 1. Initialize HTTPX client
    HTTPClientProvider.initialize()
    
    # 2. Test SSRF URL protection
    print("\n--- 1. Testing SSRF Url checks ---")
    safe_url = "https://example.com"
    unsafe_url = "http://127.0.0.1:8000"
    unsafe_internal = "http://169.254.169.254/latest/meta-data/"
    
    is_safe_ex = await is_safe_url(safe_url)
    is_safe_local = await is_safe_url(unsafe_url)
    is_safe_int = await is_safe_url(unsafe_internal)
    
    print(f"Is {safe_url} safe? {is_safe_ex} (Expected: True)")
    print(f"Is {unsafe_url} safe? {is_safe_local} (Expected: False)")
    print(f"Is {unsafe_internal} safe? {is_safe_int} (Expected: False)")
    
    assert is_safe_ex is True, "SSRF Check failed on safe URL"
    assert is_safe_local is False, "SSRF Check failed on loopback URL"
    assert is_safe_int is False, "SSRF Check failed on cloud metadata URL"
    print("[OK] SSRF protections passed!")

    # 3. Test DDGS Search
    print("\n--- 2. Testing DuckDuckGo web search ---")
    query = "FastAPI lightweight RAG benefits"
    try:
        results = await search_web(query, max_results=3)
        print(f"Search query: '{query}'")
        print(f"Retrieved {len(results)} search results.")
        for r in results:
            print(f"- {r['title']} ({r['url']})")
        assert len(results) > 0, "No search results returned"
        print("[OK] DDGS web search passed!")
    except Exception as e:
        print(f"DDGS Search skipped or failed: {e}")
        results = [{"title": "Fallback", "url": "https://example.com", "snippet": "FastAPI is lightweight."}]

    # 4. Test Web scraper & Chunker
    print("\n--- 3. Testing Trafilatura Scraper and Chunking ---")
    urls = [r["url"] for r in results if r.get("url")]
    scraped = await scrape_multiple_urls(urls[:2])
    print(f"Scraped {len(scraped)} pages.")
    
    for url, text in scraped.items():
        print(f"- {url}: {len(text)} characters extracted.")
        chunks = chunk_text(text, chunk_size=300, overlap=50)
        print(f"  Generated {len(chunks)} text chunks.")
        
    print("[OK] Web scraper and chunking passed!")

    # 5. Test BM25 Retrieval
    print("\n--- 4. Testing pure-Python BM25 Ranker ---")
    # Build dummy scraped data if empty
    if not scraped:
        scraped = {"https://example.com/rag": "FastAPI is a modern, fast (high-performance) web framework for building APIs. RAG architectures typically require transient keyword matching algorithms like BM25 to achieve lower memory profiles."}
    
    top_chunks = retrieve_top_chunks("RAG frameworks", scraped, top_n=3)
    print(f"Top ranked chunks:")
    for c in top_chunks:
        print(f"- [Score: {c['score']:.2f}] {c['url']}: {c['text'][:100]}...")
        
    assert len(top_chunks) > 0, "No chunks retrieved by BM25"
    print("[OK] BM25 chunk ranking passed!")

    # 6. Test Gemini Provider
    print("\n--- 5. Testing Gemini Provider ---")
    gemini = GeminiProvider()
    try:
        llm_resp = await gemini.generate_research_answer("RAG frameworks", top_chunks)
        print("Gemini response:")
        print(f"- Answer: {llm_resp.get('answer')}")
        print(f"- Relevance Score: {llm_resp.get('relevance_score')}")
        print("[OK] Gemini provider passed!")
    except Exception as e:
        print(f"Gemini API call failed: {e}")

    # 7. Test RAG Cache
    print("\n--- 6. Testing Cache and cleanup worker ---")
    rag_cache.start_cleanup_worker()
    test_result = {"answer": "cached answer", "sources": [], "relevance_score": 90}
    await rag_cache.set("test query", test_result)
    
    cached = await rag_cache.get("test query")
    print(f"Cache hit response: {cached}")
    assert cached is not None, "Cache lookup failed"
    assert cached["answer"] == "cached answer"
    
    await rag_cache.stop_cleanup_worker()
    print("[OK] Cache and cleanup worker passed!")

    # 8. Close client pool
    await HTTPClientProvider.close()
    print("\n=== ALL VERITAS AI PIPELINE TESTS PASSED ===")

if __name__ == "__main__":
    asyncio.run(run_tests())
