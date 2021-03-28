from setuptools import setup

setup(
    name='auror',
    version='0.0.2',
    packages=['auror'],
    install_requires=[
        'click',
        'pytest',
        'requests',
        'semantic_version',
    ],
    entry_points='''
        [console_scripts]
        auror=auror.__main__:cli
    ''',
)
