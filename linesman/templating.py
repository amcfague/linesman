from linesman import url, template_lookup


def render(template_name, **kwargs):
    template = template_lookup.get_template(template_name)
    return template.render_unicode(url=url, **kwargs)
