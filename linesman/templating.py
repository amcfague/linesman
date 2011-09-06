from linesman import template_lookup


def render(template_name, **kwargs):
    template = template_lookup(template_name)
    return template.render_unicode(**kwargs)
