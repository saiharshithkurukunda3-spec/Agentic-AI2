import httpx
from typing import Optional
from app.utils.logging_config import logger

class HTTPClientProvider:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            logger.warning("HTTPX Client requested before initialization. Initializing now.")
            cls.initialize()
        return cls._client

    @classmethod
    def initialize(cls):
        if cls._client is None:
            # Set up connection pool and timeouts
            limits = httpx.Limits(
                max_connections=50,
                max_keepalive_connections=10,
                keepalive_expiry=30.0
            )
            timeout = httpx.Timeout(10.0, connect=5.0)
            cls._client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                follow_redirects=True
            )
            logger.info("Shared HTTPX AsyncClient initialized with connection pooling.")

    @classmethod
    async def close(cls):
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
            logger.info("Shared HTTPX AsyncClient closed successfully.")

def get_http_client() -> httpx.AsyncClient:
    return HTTPClientProvider.get_client()
