"""de_duplicate_entries

Revision ID: 6929579f04e5
Revises: a3f5fff7855e
Create Date: 2017-12-13 01:09:05.712131

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import select, delete, not_, and_
from sqlalchemy.sql.expression import exists

# revision identifiers, used by Alembic.
revision = '6929579f04e5'
down_revision = 'a3f5fff7855e'
branch_labels = None
depends_on = None


def upgrade():
    metadata = sa.MetaData()
    
    history_entry = sa.Table('history_entry', metadata,
                             sa.Column('id', sa.Integer, primary_key=True),
                             sa.Column('user_id', sa.Integer, nullable=False),
                             sa.Column('app_id', sa.Integer, nullable=False),
                             sa.Column('name', sa.String(1024), nullable=False),
                             sa.Column('last_played', sa.DateTime, nullable=True),
                             sa.Column('total_hours', sa.Float, nullable=False),
                             sa.Column('session_id', sa.INTEGER))

    connection = op.get_bind()
    to_keep = select([
        history_entry.c.user_id,
        history_entry.c.app_id,
        history_entry.c.last_played,
        history_entry.c.total_hours,
        sa.func.max(history_entry.c.session_id).label('most_recent_session')
    ]).select_from(
        history_entry
    ).group_by(
        history_entry.c.user_id,
        history_entry.c.app_id,
        history_entry.c.last_played,
        history_entry.c.total_hours
    ).alias('to_keep')

    to_delete = history_entry

    full_query = delete(to_delete).\
        where(not_(exists(
            select([to_keep.c.user_id]).select_from(
                to_keep
            ).where(
                and_(
                    to_keep.c.user_id == to_delete.c.user_id,
                    to_keep.c.app_id == to_delete.c.app_id,
                    to_keep.c.last_played == to_delete.c.last_played,
                    to_keep.c.total_hours == to_delete.c.total_hours,
                    to_keep.c.most_recent_session == to_delete.c.session_id
                )
            )
        )))

    connection.execute(full_query)

    # Now clean up some duplicates within each session, from before the update_session table was introduced.

    to_keep = select([
        history_entry.c.user_id,
        history_entry.c.app_id,
        history_entry.c.last_played,
        history_entry.c.total_hours,
        history_entry.c.session_id,
        sa.func.max(history_entry.c.id).label('max_id')
    ]).select_from(
        history_entry
    ).group_by(
        history_entry.c.user_id,
        history_entry.c.app_id,
        history_entry.c.last_played,
        history_entry.c.total_hours,
        history_entry.c.session_id
    ).alias('to_keep')

    full_query = delete(to_delete).\
        where(not_(exists(
            select([to_keep.c.user_id]).select_from(
                to_keep
            ).where(
                and_(
                    to_keep.c.user_id == to_delete.c.user_id,
                    to_keep.c.app_id == to_delete.c.app_id,
                    to_keep.c.last_played == to_delete.c.last_played,
                    to_keep.c.total_hours == to_delete.c.total_hours,
                    to_keep.c.session_id == to_delete.c.session_id,
                    to_keep.c.max_id == to_delete.c.id
                )
            )
        )))

    connection.execute(full_query)


def downgrade():
    pass
