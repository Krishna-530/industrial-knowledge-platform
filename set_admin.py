import asyncio, os, sys
sys.path.insert(0, os.getcwd())
from database.engine import async_session_factory
from app.services.user_service import UserService
from database.repositories.role import RoleRepository
from core.security import get_password_hash
from database.models.user import User

async def run():
    async with async_session_factory() as db:
        svc = UserService(db)
        user = await svc.user_repo.get_by_email('admin@example.com')
        if not user:
            role_repo = RoleRepository(db)
            role = await role_repo.get_by_name("admin")
            if not role:
                print("Role 'admin' not found.")
                return
            new_user = User(
                name="Admin",
                email="admin@example.com",
                password_hash=get_password_hash('admin'),
                role_id=role.id
            )
            db.add(new_user)
            await db.commit()
            print('Admin user created with admin!')
        else:
            user.password_hash = get_password_hash('admin')
            await db.commit()
            print('Password updated')
            
if __name__ == "__main__":
    asyncio.run(run())
