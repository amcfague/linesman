import os

from linesman.backends.sqlite import SqliteBackend
from linesman.tests import (create_mock_session, get_temporary_filename, \
                            SPECIFIC_DATE_EPOCH)
from linesman.tests.backends import TestBackend


class TestBackendSqlite(TestBackend):

    def setUp(self):
        self.filename = get_temporary_filename()
        self.backend = SqliteBackend(self.filename)
        self.backend.setup()

    def tearDown(self):
        os.remove(self.filename)

    def test_setup(self):
        """ Test that setup() creates a new table with the correct columns. """
        expected_columns = [
            (u"uuid",       u"",        1),
            (u"timestamp",  u"FLOAT",    0),
            (u"session",    u"PICKLE",   0)
        ]

        # Verify that setup created the correct tables
        c = self.backend.conn.cursor()
        c.execute("PRAGMA table_info(sessions);")
        actual_columns = [
            (name, type, pk)
            for (cid, name, type, notnull, dflt_value, pk) in c.fetchall()]

        self.assertEqual(expected_columns, actual_columns)

    def test_duplicate_setup(self):
        """ Test that running setup() twice (duplicate tables) won't fail. """
        self.backend.setup()

    def test_add_session(self):
        """ Test that adding a session inserts it into the database. """
        mock_session = create_mock_session()
        self.backend.add(mock_session)

        query = "SELECT uuid, timestamp, session FROM sessions WHERE uuid = ?;"
        params = (mock_session.uuid,)

        c = self.backend.conn.cursor()
        c.execute(query, params)
        actual_uuid, actual_timestamp, actual_session = c.fetchone()

        # Assure the meta columns are equal
        self.assertEquals(mock_session.uuid, actual_uuid)
        self.assertEquals(SPECIFIC_DATE_EPOCH, actual_timestamp)

        # Also insure that the session we put in is intact!
        self.assertSessionsEqual(mock_session, actual_session)

    def test_delete(self):
        """ Test that removing an added session removes it from the DB. """
        mock_session = create_mock_session()
        self.backend.add(mock_session)
        self.backend.delete(mock_session.uuid)

        query = "SELECT * FROM sessions WHERE uuid = ?;"
        params = (mock_session.uuid,)

        # Verify that no rows are matched
        c = self.backend.conn.cursor()
        c.execute(query, params)
        self.assertEquals(c.fetchone(), None)

    def test_delete_many(self):
        """ Test that delete_many removes the correct sessions. """
        sessions = []
        for i in range(10):
            mock_session = create_mock_session()
            self.backend.add(mock_session)
            sessions.append(mock_session.uuid)

        delete_count = self.backend.delete_many(sessions[0:5])
        self.assertEquals(delete_count, 5)

        c = self.backend.conn.cursor()
        c.execute("SELECT COUNT(*) FROM sessions;")
        self.assertEquals(c.fetchone(), (5,))

    def test_delete_all(self):
        """ Test that deleting all session removes them all from the DB """
        # Add a few new session profiles
        for i in range(1, 5):
            self.backend.add(create_mock_session())

        # TODO Check to make sure rows were added?

        # Then delete them all.
        self.backend.delete_all()

        query = "SELECT * FROM sessions;"

        # Verify that no rows are matched
        c = self.backend.conn.cursor()
        c.execute(query)
        self.assertEquals(c.fetchone(), None)

    def test_get(self):
        """ Test that a session can be received using get(). """
        mock_session = create_mock_session()
        self.backend.add(mock_session)

        actual_session = self.backend.get(mock_session.uuid)
        self.assertSessionsEqual(mock_session, actual_session)

    def test_get_no_results(self):
        """ Test that when no sessions are available, get returns None """
        actual_session = self.backend.get("not a real uuid")
        self.assertEqual(None, actual_session)

    def test_get_all(self):
        """ Test that all sessions are retrieved when using get_all() """
        expected_sessions = {}
        for i in range(1, 5):
            mock_session = create_mock_session()
            self.backend.add(mock_session)
            expected_sessions[mock_session.uuid] = mock_session

        actual_sessions = self.backend.get_all()
        for (actual_uuid, actual_session) in actual_sessions.items():
            expected_session = expected_sessions.get(actual_uuid)
            self.assertTrue(expected_session != None,
                            "UUID `%s' not found in results." % actual_uuid)
            self.assertSessionsEqual(actual_session, expected_session)

    def test_get_all_no_results(self):
        """ Test that an empty dict is returned when no sessions exist. """
        actual_sessions = self.backend.get_all()
        self.assertFalse(len(actual_sessions))
