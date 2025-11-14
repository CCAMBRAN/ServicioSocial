from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# Constantes de configuración
MONGODB_URL = "mongodb://localhost:27017/"
DATABASE_NAME = "seguros_db"

class Database:
    client: Optional[AsyncIOMotorClient] = None

db = Database()

async def get_db() -> AsyncIOMotorClient:
    return db.client[DATABASE_NAME]

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(MONGODB_URL)
    
async def close_mongo_connection():
    if db.client is not None:
        db.client.close()