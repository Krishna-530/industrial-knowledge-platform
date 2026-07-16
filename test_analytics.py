import asyncio
import uuid
from datetime import datetime
from database.engine import async_session_factory
from database.models.user import User
from app.services.enterprise_analytics_service import EnterpriseAnalyticsService

async def main():
    async with async_session_factory() as session:
        service = EnterpriseAnalyticsService(session)
        result = await service.get_enterprise_analytics()
        print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
