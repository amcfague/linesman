class Backend(object):
    """
    Base class for all backends.  Methods that raise a NotImplemented exception
    are required to be overriden by children, while functions that pass are
    optional.
    """

    def __init__(self, *args, **kwargs):
        pass

    def setup(self):
        """
        Responsible for initializing the backend; this should create tables,
        create files, etc..
        """
        raise NotImplemented()

    def add(self, session):
        """
        Called when adding a new session
        """
        raise NotImplemented()

    def clear(self):
        """
        When called, this should remove all results from the backend.
        """
        raise NotImplemented()

    def get(self, session_uuid):
        """
        Returns the data associated with ``session_uuid``.  Should return
        `None` if no session can be found with the specified uuid.
        """
        raise NotImplemented()

    def get_all(self):
        """
        Return a dictionary of ALL sessions, where the key is the uuid.
        """
        raise NotImplemented()
