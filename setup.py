import io
import os.path
from setuptools import find_packages, setup

version = '0.0.1-alpha'

def parse_requirements(filename):
    ''' load requirements from a pip requirements file'''
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith('#')]

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'))

setup(
    name='strivial',
    version=version,
    author='Sean Watson',
    url='https://github.com/watsosc/strivial',
    license='Apache',
    description='Does some strava stuff',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=reqs,
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ]
    }
)