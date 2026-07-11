import pytest
from alembic.config import Config
from alembic import command

def test_migrations_round_trip(postgres_container):
    """Verify that migrations can upgrade to head and downgrade to base without errors."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_container)
    
    # We are already at head due to autouse fixture, so let's downgrade
    command.downgrade(alembic_cfg, "base")
    
    # And upgrade back to head
    command.upgrade(alembic_cfg, "head")
