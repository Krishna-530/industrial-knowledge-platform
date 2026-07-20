import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from core.security import verify_password
async def check_user():
    engine = create_async_engine('postgresql+asyncpg://postgres:Krishna509@localhost:5432/industrial_knowledge_platform')
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT id, email, is_active, password_hash FROM users WHERE email='admin@example.com'"))
            user = result.first()
            if not user:
                print('User does not exist')
            else:
                print(f'is_active: {user.is_active}')
                print(f'Hash: {user.password_hash}')
                matches = verify_password('admin', user.password_hash)
                print(f'Password matches admin: {matches}')
    except Exception as e:
        print(f'Query failed: {e}')
asyncio.run(check_user())
