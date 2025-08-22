from prisma import Prisma
from app.config import settings
import asyncio

# Global database instance
db = Prisma()

async def connect_db():
    """Connect to the database"""
    try:
        await db.connect()
        print("✅ Connected to PostgreSQL database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {str(e)}")
        raise

async def disconnect_db():
    """Disconnect from the database"""
    try:
        await db.disconnect()
        print("✅ Disconnected from database")
    except Exception as e:
        print(f"❌ Error disconnecting from database: {str(e)}")

async def get_db():
    """Get database instance for dependency injection"""
    return db

# Database health check
async def check_db_health():
    """Check if database connection is healthy"""
    try:
        # Simple query to test connection
        result = await db.query_raw("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Initialize database tables (run migrations)
async def init_db():
    """Initialize database with migrations"""
    try:
        # This will be used later when we have migrations
        print("🔄 Initializing database...")
        # await db.execute_raw("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        raise