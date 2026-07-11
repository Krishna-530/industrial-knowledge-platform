import asyncio
import os
import sys
from getpass import getpass

# Ensure we can import from our project root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.engine import async_session_factory
from database.repositories.user import UserRepository
from database.repositories.role import RoleRepository
from core.security import get_password_hash
from core.exceptions import DuplicateEntityError
from core.settings import Settings

async def bootstrap():
    settings = Settings()
    
    # Check for credentials in environment variables
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_name = os.getenv("ADMIN_NAME", "System Administrator")

    if not admin_email:
        print("ADMIN_EMAIL not set in environment.")
        admin_email = input("Enter Administrator Email: ")
    
    if not admin_password:
        print("ADMIN_PASSWORD not set in environment.")
        admin_password = getpass("Enter Administrator Password: ")
        confirm_password = getpass("Confirm Password: ")
        if admin_password != confirm_password:
            print("Error: Passwords do not match.")
            sys.exit(1)

    print(f"Bootstrapping administrator account for {admin_email}...")

    async with async_session_factory() as db_session:
        role_repo = RoleRepository(db_session)
        user_repo = UserRepository(db_session)
        
        # Ensure admin role exists
        admin_role = await role_repo.get_by_name("admin")
        if not admin_role:
            print("Error: 'admin' role not found in database. Have you run Alembic migrations?")
            sys.exit(1)
            
        # Check if user already exists
        existing_user = await user_repo.get_by_email(admin_email)
        if existing_user:
            print(f"Administrator {admin_email} already exists. Skipping creation.")
            return

        try:
            password_hash = get_password_hash(admin_password)
            user = await user_repo.create(
                name=admin_name,
                email=admin_email,
                password_hash=password_hash,
                role_id=admin_role.id
            )
            # Service layer now owns transaction boundaries
            await db_session.commit()
            print(f"Success: Administrator {admin_email} created successfully.")
        except DuplicateEntityError:
            await db_session.rollback()
            print(f"Error: A user with email {admin_email} already exists.")
        except Exception as e:
            await db_session.rollback()
            print(f"Error occurred during bootstrap: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(bootstrap())
