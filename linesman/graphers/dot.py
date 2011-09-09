from cStringIO import StringIO


def render_dot(session):
    sio = StringIO()

    sio.write("digraph G {\n")

    # Write out each individual node
    for node in session.nodes:
        sio.write('    "%s";\n' % node)

    # Write out the edges
    for source, destinations in session.edges.items():
        for destination in destinations:
            sio.write('    "%s" -> "%s";\n' % (source, destination))

    sio.write("}\n")

    return sio.getvalue()
