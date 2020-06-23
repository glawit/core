import importlib.resources

import jinja2

loader = jinja2.PackageLoader(
    'glawit.core.data',
    package_path='data/jinja2',
)

package = 'glawit.core.data.jinja2'


def load_template(name):
    exists = importlib.resources.is_resource(
        name=name,
        package=package,
    )

    assert exists

    content = importlib.resources.read_text(
        encoding='utf-8',
        package=package,
        resource=name,
    )

    return content
