import setuptools


packages = setuptools.find_namespace_packages(
    include=[
        'glawit.*',
    ],
)

setuptools.setup(
    install_requires=[
        'Flask == 1.1.2',
    ],
    name='glawit_interface_flask',
    packages=packages,
    python_requires='>= 3.7',
    version='0.1',
    zip_safe=False, # due to namespace package
)
