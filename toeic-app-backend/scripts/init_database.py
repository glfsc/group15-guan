import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.init_db import init_database, test_connection
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting database initialization...")
    
    is_connected = await test_connection()
    if not is_connected:
        logger.error("Failed to connect to database. Please check your database configuration.")
        sys.exit(1)
    
    logger.info("Connection successful. Creating tables...")
    await init_database()
    
    logger.info("Database initialization completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
