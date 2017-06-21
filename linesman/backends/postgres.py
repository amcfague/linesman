import cPickle
import logging
import psycopg2
import time
import StringIO

from linesman.backends.base import Backend

try:
    # Python 2.7+
    from collections import OrderedDict
except ImportError:
    # Python 2.4+
    from ordereddict import OrderedDict

log = logging.getLogger(__name__)


class PostgresBackend(Backend):
    """
    Stores sessions in a PostgreSQL database.
    """

    def __init__(self, dbname='linesman', user='user', password='password'):
        """
        Opens up a connection to a PostgreSQL database.
        There is no "connection close" method at
        linesman.backends.base.Backend...
        """

        self.conn = psycopg2.connect(
            dbname=dbname, user=user, password=password)

    def setup(self):
        """
        Creates table for Linesman, if it doesn't already exist.
        """

        query = """
            CREATE TABLE sessions (
                uuid uuid PRIMARY KEY,
                timestamp FLOAT,
                session BYTEA
            );
        """
        cur = self.conn.cursor()
        try:
            cur.execute(query)
            self.conn.commit()
        except psycopg2.ProgrammingError:
            log.debug("Table already exists.")
            self.conn.rollback()
        finally:
            cur.close()

    def add(self, session):
        """
        Insert a new session into the database.
        """
        uuid = session.uuid
        if session.timestamp:
            timestamp = time.mktime(session.timestamp.timetuple())
        else:
            timestamp = None

        pickled_session = psycopg2.Binary(cPickle.dumps(session, -1))

        query = "INSERT INTO sessions VALUES ('{}', {}, {});".format(
            uuid, timestamp, pickled_session
        )
        cur = self.conn.cursor()
        try:
            cur.execute(query)
            self.conn.commit()
        except:
            self.conn.rollback()
        finally:
            cur.close()

    def delete(self, session_uuid):
        """
        Remove the session.
        """
        query = "DELETE FROM sessions WHERE uuid = '{}';".format(session_uuid)

        cur = self.conn.cursor()
        try:
            cur.execute(query)
            self.conn.commit()
        except:
            self.conn.rollback()
        finally:
            cur.close()

    def delete_many(self, session_uuids):
        """
        Remove the sessions.
        """
        query = "DELETE FROM sessions WHERE uuid IN ('{}');".format(
            "', '".join(session_uuids))
        cur = self.conn.cursor()
        deleted_rows = 0
        try:
            cur.execute(query)
            self.conn.commit()
            deleted_rows = cur.rowcount
        except:
            self.conn.rollback()
        finally:
            cur.close()
        return deleted_rows

    def delete_all(self):
        """
        Truncate the database.
        """
        query = "DELETE FROM sessions;"

        cur = self.conn.cursor()
        try:
            cur.execute(query)
            self.conn.commit()
        except:
            self.conn.rollback()
        finally:
            cur.close()

    def get(self, session_uuid):
        """
        Retrieves the session from the database.
        """
        query = "SELECT session FROM sessions WHERE uuid = '{}';".format(
            session_uuid)

        cur = self.conn.cursor()
        result = None
        try:
            cur.execute(query)
            self.conn.commit()
            session = cur.fetchone()
            result = cPickle.load(StringIO.StringIO(session[0]))
        except:
            self.conn.rollback()
        finally:
            cur.close()

        return result if result else None

    def get_all(self):
        """
        Generates a dictionary of the data based on the contents of the DB.
        """
        query = "SELECT uuid, session FROM sessions ORDER BY timestamp;"

        cur = self.conn.cursor()
        result = []
        try:
            cur.execute(query)
            self.conn.commit()
            result = cur.fetchall()
        except:
            self.conn.rollback()
        finally:
            cur.close()

        unpickled_result = []

        for (uuid, session) in result:
            unpickled_session = cPickle.load(StringIO.StringIO(session))
            unpickled_result.append((uuid, unpickled_session))

        return OrderedDict(unpickled_result)
