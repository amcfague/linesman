from paste.registry import StackedObjectProxy


backend = StackedObjectProxy(name="backend")
request = StackedObjectProxy(name="request")
response = StackedObjectProxy(name="response")
template_lookup = StackedObjectProxy(name="template_lookup")
