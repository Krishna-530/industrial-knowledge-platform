"""rename_embedded_status

Revision ID: 6bb8b359dca1
Revises: b8141a08489c
Create Date: 2026-07-16 09:57:14.260689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bb8b359dca1'
down_revision: Union[str, Sequence[str], None] = 'b8141a08489c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE chunkstatus RENAME VALUE 'EMBEDDED' TO 'VECTOR_PENDING'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE chunkstatus RENAME VALUE 'VECTOR_PENDING' TO 'EMBEDDED'")
