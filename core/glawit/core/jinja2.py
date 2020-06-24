import importlib.resources

import jinja2

data_package = 'glawit.core.data.jinja2'

loader = jinja2.FunctionLoader(
    load_template,
)


def load_template(name):
    exists = importlib.resources.is_resource(
        name=name,
        package=data_package,
    )

    assert exists

    content = importlib.resources.read_text(
        encoding='utf-8',
        package=data_package,
        resource=name,
    )

    return content
