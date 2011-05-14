import datetime
import tempfile

from mock import Mock, patch

import linesman


__all__ = ['SPECIFIC_DATE_DATETIME', 'SPECIFIC_DATE_EPOCH',
           'create_mock_session', 'get_temporary_filename']

SPECIFIC_DATE_DATETIME = datetime.datetime(2011, 1, 1, 0, 0, 0, 0)
SPECIFIC_DATE_EPOCH = 1293858000.0


@patch.object(linesman, "create_graph", Mock(return_value=["abc"]))
def create_mock_session(timestamp=SPECIFIC_DATE_DATETIME):
    class Stat(object):
        totaltime = 0
    return linesman.ProfilingSession([Stat()], timestamp=timestamp)


def get_temporary_filename():
    with tempfile.NamedTemporaryFile(delete=False) as fd:
        return fd.name
