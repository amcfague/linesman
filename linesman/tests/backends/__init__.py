import tempfile
import unittest


class TestBackend(unittest.TestCase):
    """
    Base test class for testing backends.  This adds a few helpful functions,
    such as asserting that two sessions are equivalent.
    """

    def assertSessionsEqual(self, session1, session2):
        """
        Verifies that session1 and session2 are equal.
        """
        return all((
            session1.duration == session2.duration,
            session1.path == session2.path,
            session1.timestamp == session2.timestamp,
            session1.uuid == session2.uuid,
            session1._graph == session2._graph,
            session1._uuid == session2._uuid,
        ))
