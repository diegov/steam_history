from sqlalchemy import create_engine, func
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData
from sqlalchemy.sql import select
import functools

metadata = MetaData()

user = Table('user', metadata,
             Column('id', Integer, primary_key=True),
             Column('username', String(1024), nullable=False)
)

update_session = Table('update_session', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('run_at', DateTime, nullable=False, index=True)
)

history_entry = Table('history_entry', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('user_id', Integer, nullable=False),
                      Column('app_id', Integer, nullable=False),
                      Column('name', String(1024), nullable=False),
                      Column('last_played', DateTime, nullable=True),
                      Column('total_hours', Float, nullable=False),
                      Column('session_id', Integer, nullable=False)
)

class Storage(object):
    def __init__(self, conn_string):
        self.conn_string = conn_string
        self._init_engine()

    def _init_engine(self):        
        self.engine = create_engine(self.conn_string, echo=False)

    def save(self, table, values=None, key=None):
        if key is None and values and 'id' in values:
            key = {'id': values['id']}

        conn = self.engine.connect()
        try:
            if key is not None:
                existing = self.get(table, key=key)
            else:
                existing = None

            all_values = {k: v for k, v in values.items()} if values is not None else {}
            if key is not None:
                all_values.update(key)

            if existing is None:
                cmd = table.insert().values(**all_values)
            else:
                cmd = table.update().\
                      where(self._get_key_conditions(table, key)).\
                      values(**all_values)
            return conn.execute(cmd)
        finally:
            conn.close()

    def get_max_id(self, table):
        conn = self.engine.connect()
        try:
            s = select([func.max(table.c.id)])
            result = conn.execute(s).fetchone()
            if result:
                return result[0]
            else:
                return None
        finally:
            conn.close()

    def get(self, table, key):
        conn = self.engine.connect()
        try:
            s = select([table]).where(self._get_key_conditions(table, key))
            result = conn.execute(s)
            try:
                row = result.fetchone()
                if row == None:
                    return None
                else:
                    return {k: row[k] for k in result.keys()}
            finally:
                result.close()
        finally:
            conn.close()

    def _get_key_conditions(self, table, key):
        conditions = (getattr(table.c, col) == val for col, val in key.items())
        return functools.reduce(lambda x, y: x & y, conditions)

