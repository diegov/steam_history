"""create history_entry table

Revision ID: 783bf1a57f4d
Revises: aabe59f26346
Create Date: 2017-12-01 00:06:28.004467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '783bf1a57f4d'
down_revision = 'aabe59f26346'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'history_entry',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False, index=True),
        sa.Column('app_id', sa.Integer, nullable=False, index=True),
        sa.Column('name', sa.String(1024), nullable=False),
        sa.Column('last_played', sa.DateTime, nullable=True, index=True),
        sa.Column('total_hours', sa.Float, nullable=False)
    )

    # op.create_index('idx_history_entry_user_app_id', 'history_entry', ['user_id', 'app_id'])

    # op.create_foreign_key(
    #     "fk_history_entry_user", "history_entry", "user",
    #     ["user_id"], ["id"], ondelete="CASCADE")


def downgrade():
    op.drop_table('history_entry')
