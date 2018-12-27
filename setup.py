import io
from setuptools import find_packages, setup

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='strivial',
    version='0.0.1',
    license='Apache',
    description='Does some strava stuff',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'alembic',
        'Click',
        'Flask',
        'Flask-Migrate',
        'Flask-Script',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'itsdangerous',
        'Jinja2',
        'Mako',
        'MarkupSafe',
        'psycopg2',
        'python-dateutil',
        'python-dotenv',
        'python-editor',
        'six',
        'SQLAlchemy',
        'Werkzeug',
        'WTForms',
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ]
    }
)