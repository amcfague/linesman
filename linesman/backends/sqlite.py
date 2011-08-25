# This file is part of linesman.
#
# linesman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# linesman is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with linesman.  If not, see <http://www.gnu.org/licenses/>.
#
import cPickle
import logging
import sqlite3
import time

from linesman.backends.base import Backend


try:
    # Python 2.7+
    from collections import OrderedDict
except ImportError:
    # Python 2.4+
    from ordereddict import OrderedDict


sqlite3.register_converter("pickle", cPickle.loads)
log = logging.getLogger(__name__)


class SqliteBackend(Backend):
    """
    Stores sessions in a SQLite database.
    """

    def __init__(self, filename="sessions.db"):
        """
        Opens up a connection to a sqlite3 database.

        ``filename``:
            filename of the sqlite database.  If this file does not exist, it
            will be created automatically.

            This can also be set to `:memory:` to store the database in
            memory; however, this will not persist across runs.
        """
        self.filename = filename

    @property
    def conn(self):
        return sqlite3.connect(self.filename, isolation_level=None,
            detect_types=(sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES))

    def setup(self):
        """
        Creates table for Linesman, if it doesn't already exist.
        """
        query = """
            CREATE TABLE sessions (
                uuid PRIMARY KEY,
                timestamp FLOAT,
                session PICKLE
            );
        """
        try:
            c = self.conn.cursor()
            c.execute(query)
        except sqlite3.OperationalError:
            log.debug("Table already exists.")

    def add(self, session):
        """
        Insert a new session into the database.
        """
        uuid = session.uuid
        if session.timestamp:
            timestamp = time.mktime(session.timestamp.timetuple())
        else:
            timestamp = None
        pickled_session = sqlite3.Binary(cPickle.dumps(session, -1))

        query = "INSERT INTO sessions VALUES (?, ?, ?);"
        params = (uuid, timestamp, pickled_session)

        c = self.conn.cursor()
        c.execute(query, params)

    def delete(self, session_uuid):
        """
        Remove the session.
        """
        query = "DELETE FROM sessions WHERE uuid = ?;"
        params = (session_uuid,)

        conn = self.conn
        curs = conn.cursor()
        curs.execute(query, params)

        return conn.total_changes

    def delete_all(self):
        """
        Truncate the database.
        """
        query = "DELETE FROM sessions;"

        conn = self.conn
        curs = conn.cursor()
        curs.execute(query)

        return conn.total_changes

    def get(self, session_uuid):
        """
        Retrieves the session from the database.
        """
        query = "SELECT session FROM sessions WHERE uuid = ?;"
        params = (session_uuid,)

        c = self.conn.cursor()
        c.execute(query, params)
        result = c.fetchone()

        return result[0] if result else None

    def get_all(self):
        """
        Generates a dictionary of the data based on the contents of the DB.
        """
        query = "SELECT uuid, session FROM sessions ORDER BY timestamp;"

        c = self.conn.cursor()
        c.execute(query)

        return OrderedDict(c.fetchall())
