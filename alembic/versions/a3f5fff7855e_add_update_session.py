"""add_update_session

Revision ID: a3f5fff7855e
Revises: 783bf1a57f4d
Create Date: 2017-12-08 11:35:18.160925

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import select

# revision identifiers, used by Alembic.
revision = 'a3f5fff7855e'
down_revision = '783bf1a57f4d'
branch_labels = None
depends_on = None


def _get_data(select_op):
    connection = op.get_bind()
    return [r for r in connection.execute(select_op)]


def upgrade():
    session_tbl = op.create_table(
        'update_session',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('run_at', sa.DateTime, nullable=True, index=True)
    )

    metadata = sa.MetaData()
    
    history_entry = sa.Table('history_entry', metadata,
                             sa.Column('id', sa.Integer, primary_key=True),
                             sa.Column('user_id', sa.Integer, nullable=False),
                             sa.Column('app_id', sa.Integer, nullable=False),
                             sa.Column('name', sa.String(1024), nullable=False),
                             sa.Column('last_played', sa.DateTime, nullable=True),
                             sa.Column('total_hours', sa.Float, nullable=False),
                             sa.Column('session_id', sa.INTEGER)
    )

    latest_played = _get_data(select([sa.func.max(history_entry.c.last_played)]))

    op.add_column('history_entry',
                  sa.Column('session_id', sa.INTEGER)
    )

    if len(latest_played) > 0 and latest_played[0] is not None:
        op.execute(session_tbl.insert({'run_at': latest_played[0][0]}))
        session_id = _get_data(select([sa.func.max(session_tbl.c.id)]))[0][0]
        op.execute(history_entry.update().values({'session_id': session_id}))


def downgrade():
    op.drop_column('history_entry', 'session_id')
    op.drop_table('update_session')
