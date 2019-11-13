from setuptools import setup

# List of dependencies installed via `pip install -e .`
# by virtue of the Setuptools `install_requires` value below.
requires = [
    'pyramid',
    'waitress',
    'SQLAlchemy'
]

# List of dependencies installed via `pip install -e ".[dev]"`
# by virtue of the Setuptools `extras_require` value in the Python
# dictionary below.
dev_requires = [
    'pyramid_debugtoolbar',
]

setup(
    name='recipes',
    install_requires=requires,
    extras_require={
        'dev': dev_requires,
    },
    entry_points={
        'paste.app_factory': [
            'main = recipes:main'
        ],
    },
)
