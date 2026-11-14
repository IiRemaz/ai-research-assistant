"""Add saved papers feature.

Revision ID: b7e1a4d21c90
Revises: 0baaad0b3c33
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b7e1a4d21c90'
down_revision: Union[str, Sequence[str], None] = '0baaad0b3c33'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('saved_papers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('paper_id', sa.Integer(), sa.ForeignKey('papers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('paper_id', name='uq_saved_paper'))

def downgrade() -> None:
    op.drop_table('saved_papers')
