import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.config import settings
from app.utils.logging_config import logger

class Database:
    client: AsyncIOMotorClient = None
    db = None
    connected: bool = False

    @classmethod
    async def connect_db(cls):
        try:
            logger.info("Connecting to MongoDB Atlas...", uri=settings.MONGODB_URI)
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Try to ping the database to verify connectivity
            await cls.client.admin.command('ping')
            # Extract database name from connection string or default to veritas_db
            db_name = settings.MONGODB_URI.split("/")[-1].split("?")[0]
            if not db_name:
                db_name = "veritas_db"
            cls.db = cls.client[db_name]
            cls.connected = True
            logger.info("Successfully connected to MongoDB database.", database_name=db_name)
        except Exception as e:
            cls.connected = False
            cls.db = None
            logger.error(
                "MongoDB connection failed. Continuing in degraded state.",
                error=str(e),
                tip="Make sure MONGODB_URI is correct and IP whitelisting is configured in Atlas."
            )

    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            cls.client.close()
            logger.info("MongoDB client connection closed.")

def get_db():
    if not Database.connected or Database.db is None:
        # In a real environment we might want to retry, but for endpoints we throw if they need the DB.
        # But we don't crash startup.
        pass
    return Database.db
