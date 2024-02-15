from setuptools import setup, find_packages

setup(
    name='code-meower',
    version='1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[],
    entry_points='''
        [console_scripts]
        meow=main:main
    ''',
)
