import os
from cPickle import HIGHEST_PROTOCOL
from nose.tools import raises
from mock import MagicMock, Mock, patch
from tempfile import TemporaryFile

import linesman.backends.pickle
from linesman.tests import get_temporary_filename
from linesman.tests.backends import TestBackend

MOCK_SESSION_UUID = "abcd1234"


class TestBackendPickle(TestBackend):

    def setUp(self):
        self.filename = get_temporary_filename()
        self.backend = linesman.backends.pickle.PickleBackend(self.filename)

    def tearDown(self):
        os.remove(self.filename)

    @patch("cPickle.dump")
    def test_flush(self, mock_dump):
        """ Test that the file is opened by cPickle. """
        test_fd = TemporaryFile()
        with patch("__builtin__.open", Mock(side_effect=IOError())):
            self.backend.setup()

        with patch("__builtin__.open") as mock_open:
            mock_open.return_value = test_fd
            self.backend._flush()
            mock_open.assert_called_once_with(
                self.backend.filename, "w+b")

        mock_dump.assert_called_once_with(
            self.backend._session_history,
            test_fd,
            HIGHEST_PROTOCOL)

    @patch("__builtin__.open")
    @patch("cPickle.load")
    def test_setup(self, mock_load, mock_open):
        """ Test that setup will load pickled data. """
        mock_open.return_value = MagicMock(spec=file)
        self.backend.setup()
        mock_open.assert_called_once_with(self.filename, "rb")
        mock_load.assert_called_once()

    @patch("__builtin__.open")
    @patch("linesman.backends.pickle.OrderedDict")
    def test_setup_ioerror(self, mock_ordered_dict, mock_open):
        """ Test that setup will create a new ordered dict if no file exists
        """
        mock_open.side_effect = IOError()
        self.backend.setup()
        mock_ordered_dict.assert_called_once_with()

    @raises(ValueError)
    @patch("__builtin__.open")
    def test_setup_value_error(self, mock_open):
        """ Test that bad pickled data raises a ValueError. """
        mock_open.side_effect = ValueError("Could not unpickle!")
        self.backend.setup()

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("linesman.backends.pickle.PickleBackend._flush")
    def test_add(self, mock_flush):
        """ Test that add creates a new entry in the session. """
        mock_session = MagicMock()
        mock_session.uuid = MOCK_SESSION_UUID

        self.backend.setup()
        self.backend.add(mock_session)

        self.assertTrue(mock_session.uuid in self.backend._session_history)
        mock_flush.assert_called_once()

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("linesman.backends.pickle.PickleBackend._flush")
    def test_delete(self, mock_flush):
        """ Test that deleting an existing UUID returns 0. """
        mock_session = MagicMock()
        mock_session.uuid = MOCK_SESSION_UUID

        self.backend.setup()
        self.backend.add(mock_session)
        self.assertEquals(self.backend.delete(mock_session.uuid), 1)
        mock_flush.assert_called_once()

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("linesman.backends.pickle.PickleBackend._flush")
    def test_delete_non_existent_uuid(self, mock_flush):
        """ Test that deleting a non-existing UUID returns 0. """
        mock_session = MagicMock()
        mock_session.uuid = MOCK_SESSION_UUID

        self.backend.setup()
        self.backend.add(mock_session)
        self.assertEquals(self.backend.delete("basb3144"), 0)
        mock_flush.assert_called_once()

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("linesman.backends.pickle.PickleBackend._flush")
    def test_delete_all(self, mock_flush):
        """ Test that deleting a non-existing UUID returns 0. """
        mock_session1 = MagicMock()
        mock_session1.uuid = MOCK_SESSION_UUID

        mock_session2 = MagicMock()
        mock_session2.uuid = "something else"

        self.backend.setup()
        self.backend.add(mock_session1)
        self.backend.add(mock_session2)
        self.assertEquals(self.backend.delete_all(), 2)
        self.assertEquals(len(self.backend._session_history), 0)
        mock_flush.assert_called_once()

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("linesman.backends.pickle.PickleBackend._flush")
    def test_delete_all_empty(self, mock_flush):
        """ Test that callign delete all on an empty dict returns 0. """
        self.backend.setup()
        self.assertEquals(self.backend.delete_all(), 0)
        mock_flush.assert_called_once()

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("linesman.backends.pickle.PickleBackend._flush", Mock())
    def test_get(self):
        """ Test that retrieving an existing UUID succeeds. """
        mock_session = MagicMock()
        mock_session.uuid = MOCK_SESSION_UUID

        self.backend.setup()
        self.backend.add(mock_session)
        self.assertEquals(self.backend.get(MOCK_SESSION_UUID), mock_session)

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    def test_get_non_existent_uuid(self):
        """ Test that retrieving an non-existent UUID returns None. """
        self.backend.setup()
        self.assertEquals(self.backend.get(MOCK_SESSION_UUID), None)

    @patch("__builtin__.open", Mock(side_effect=IOError()))
    @patch("linesman.backends.pickle.PickleBackend._flush", Mock())
    def test_get_all(self):
        """ Test that getting all results returns a copy. """
        mock_session = MagicMock()
        mock_session.uuid = MOCK_SESSION_UUID

        self.backend.setup()
        self.backend.add(mock_session)
        session_history_copy = self.backend.get_all()
        assert self.backend._session_history is not session_history_copy
