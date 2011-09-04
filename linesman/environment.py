from paste.registry import StackedObjectProxy
from linesman.middleware import ProfilingMiddleware, RegistryManager

globals = StackedObjectProxy()
app = RegistryManager(ProfilingMiddleware)
