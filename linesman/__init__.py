from paste.registry import StackedObjectProxy


backend = StackedObjectProxy(name="backend")
profiling_status = StackedObjectProxy(name="profiling_status")
request = StackedObjectProxy(name="request")
response = StackedObjectProxy(name="response")
template_lookup = StackedObjectProxy(name="template_lookup")
url = StackedObjectProxy(name="url")
