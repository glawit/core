import setuptools


packages = setuptools.find_namespace_packages(
    include=[
        'glawit.*',
    ],
)

setuptools.setup(
    install_requires=[
        'gql == 2.0.0',
    ],
    name='glawit_core',
    package_data={
        'glawit.core.data.graphql': [
            '*.graphql',
        ],
    },
    packages=packages,
    python_requires='>= 3.7',
    version='0.1',
    zip_safe=False, # due to namespace package
)
