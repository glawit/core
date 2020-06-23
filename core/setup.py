import setuptools


packages = setuptools.find_namespace_packages(
    include=[
        'glawit.*',
    ],
)

setuptools.setup(
    install_requires=[
        'gql == 2.0.0',
        'Jinja2 == 2.11.2',
    ],
    name='glawit_core',
    package_data={
        'glawit': [
            'data/*',
        ],
    },
    packages=packages,
    python_requires='>= 3.7',
    version='0.1',
    zip_safe=False, # due to namespace package
)
