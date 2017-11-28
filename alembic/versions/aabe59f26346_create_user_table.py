"""create user table

Revision ID: aabe59f26346
Revises:
Create Date: 2017-12-01 00:05:54.560472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aabe59f26346'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(1024), nullable=False, unique=True)
    )


def downgrade():
    op.drop_table('user')
