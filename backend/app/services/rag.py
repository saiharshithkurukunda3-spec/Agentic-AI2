import time
import math
import re
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from app.utils.logging_config import logger

# --- IN-MEMORY QUERY CACHE WITH BACKGROUND CLEANER ---
class RAGCache:
    def __init__(self, ttl_seconds: int = 600):
        self._cache: Dict[str, Tuple[Dict[str, Any], float]] = {}  # query -> (data, expires_at)
        self.ttl = ttl_seconds
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def get(self, query: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            # Normalize query to make caching robust
            norm_query = query.strip().lower()
            if norm_query in self._cache:
                data, expires_at = self._cache[norm_query]
                if time.time() < expires_at:
                    logger.info("RAG Cache Hit", query=query)
                    return data
                else:
                    # Stale entry
                    del self._cache[norm_query]
            return None

    async def set(self, query: str, data: Dict[str, Any]):
        async with self._lock:
            norm_query = query.strip().lower()
            expires_at = time.time() + self.ttl
            self._cache[norm_query] = (data, expires_at)
            logger.info("RAG Cache Entry Added", query=query, expires_in=self.ttl)

    async def delete(self, query: str):
        async with self._lock:
            norm_query = query.strip().lower()
            if norm_query in self._cache:
                del self._cache[norm_query]

    async def _clean_loop(self):
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every 60 seconds
                async with self._lock:
                    now = time.time()
                    expired_keys = [k for k, (_, exp) in self._cache.items() if now >= exp]
                    for k in expired_keys:
                        del self._cache[k]
                    if expired_keys:
                        logger.info("RAG Cache periodic cleanup executed", evicted_count=len(expired_keys))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("RAG Cache cleanup worker encountered error", error=str(e))

    def start_cleanup_worker(self):
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._clean_loop())
            logger.info("RAG Cache Background Cleanup Worker started.")

    async def stop_cleanup_worker(self):
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("RAG Cache Background Cleanup Worker stopped.")

# Global cache instance
rag_cache = RAGCache(ttl_seconds=600)  # 10 minutes cache TTL


# --- PURE-PYTHON BM25 RANKER ---
class SimpleBM25:
    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avg_doc_len = sum(len(doc) for doc in corpus) / self.corpus_size if self.corpus_size > 0 else 0
        self.doc_lens = [len(doc) for doc in corpus]
        self.idf: Dict[str, float] = {}
        self._calculate_idf(corpus)

    def _calculate_idf(self, corpus: List[List[str]]):
        nd = {}
        for doc in corpus:
            for word in set(doc):
                nd[word] = nd.get(word, 0) + 1
        for word, freq in nd.items():
            # BM25 IDF variant that prevents negative numbers
            self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1.0)

    def get_scores(self, query: List[str], corpus: List[List[str]]) -> List[float]:
        scores = []
        for i, doc in enumerate(corpus):
            score = 0.0
            doc_len = self.doc_lens[i]
            tf = {}
            for word in doc:
                tf[word] = tf.get(word, 0) + 1
            
            for word in query:
                if word in tf:
                    word_tf = tf[word]
                    numerator = self.idf.get(word, 0.0) * word_tf * (self.k1 + 1)
                    denominator = word_tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += numerator / denominator
            scores.append(score)
        return scores


# --- CHUNKING & RETRIEVAL ENGINE ---
def tokenize(text: str) -> List[str]:
    # Clean text and split into lowercase word tokens
    return re.findall(r'\w+', text.lower())

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    chunks = []
    start = 0
    text_len = len(text)
    
    if text_len <= chunk_size:
        return [text]

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        start += chunk_size - overlap
        
    return chunks

def retrieve_top_chunks(query: str, sources_data: Dict[str, str], top_n: int = 8) -> List[Dict[str, Any]]:
    """
    Ranks chunks using BM25 and returns top_n chunks mapped to their source URL.
    """
    logger.info("Starting chunking and BM25 retrieval", url_count=len(sources_data))
    
    all_chunks_info = []
    corpus_tokens = []
    
    # 1. Chunk documents and tokenise
    for url, text in sources_data.items():
        chunks = chunk_text(text, chunk_size=800, overlap=150)
        for chunk in chunks:
            tokens = tokenize(chunk)
            all_chunks_info.append({
                "url": url,
                "text": chunk,
                "tokens": tokens
            })
            corpus_tokens.append(tokens)

    if not all_chunks_info:
        logger.warning("No text chunks generated for ranking")
        return []

    # 2. Tokenise Query
    query_tokens = tokenize(query)

    # 3. Score Chunks using BM25
    bm25 = SimpleBM25(corpus_tokens)
    scores = bm25.get_scores(query_tokens, corpus_tokens)

    # 4. Attach scores and sort
    for i, score in enumerate(scores):
        all_chunks_info[i]["score"] = score

    # Sort descending by score
    sorted_chunks = sorted(all_chunks_info, key=lambda x: x["score"], reverse=True)

    # 5. Extract top N results
    top_chunks = sorted_chunks[:top_n]
    
    # Exclude raw tokens before returning to save memory
    for c in top_chunks:
        c.pop("tokens", None)

    logger.info("BM25 chunk ranking completed", chunks_evaluated=len(all_chunks_info), retrieved_count=len(top_chunks))
    return top_chunks
