"""add indexing_checked_at to files

Revision ID: 42b23aba7562
Revises: 33612bfde906
Create Date: 2025-12-21 14:32:57.414049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42b23aba7562'
down_revision: Union[str, Sequence[str], None] = '33612bfde906'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "files",
        sa.Column(
            "indexing_checked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_files_indexing_checked_at",
        "files",
        ["indexing_checked_at"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_files_indexing_checked_at", table_name="files")
    op.drop_column("files", "indexing_checked_at")

