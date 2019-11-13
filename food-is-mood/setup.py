from setuptools import setup

requires = [
    'pyramid',
    'waitress',
    'SQLAlchemy'
]

setup(
    name='recipes',
    install_requires=requires
)
