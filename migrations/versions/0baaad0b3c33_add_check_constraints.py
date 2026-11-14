
"""add check constraints

Revision ID: 0baaad0b3c33
Revises: ee7f5eb2064a
Create Date: 2026-11-12 03:36:03.390290
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0baaad0b3c33'
down_revision: Union[str, Sequence[str], None] = 'ee7f5eb2064a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add check constraints."""

    with op.batch_alter_table("messages") as batch_op:
        batch_op.create_check_constraint(
            "ck_messages_role_valid",
            "role IN ('user', 'assistant')"
        )

    with op.batch_alter_table("paper_chunks") as batch_op:
        batch_op.create_check_constraint(
            "ck_paper_chunks_chunk_index_nonnegative",
            "chunk_index >= 0"
        )


def downgrade() -> None:
    """Remove check constraints."""

    with op.batch_alter_table("paper_chunks") as batch_op:
        batch_op.drop_constraint(
            "ck_paper_chunks_chunk_index_nonnegative",
            type_="check"
        )

    with op.batch_alter_table("messages") as batch_op:
        batch_op.drop_constraint(
            "ck_messages_role_valid",
            type_="check"
        )
