from setuptools import setup

requires = [
    'pyramid',
    'waitress',
    'SQLAlchemy'
]

setup(
    name='recipes',
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = recipes:main'
        ],
    },
)
