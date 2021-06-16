from setuptools import setup
from sys import version_info
from pathlib import Path


def readme():
    with open("README.md") as f:
        return f.read()


if version_info < (3, 9):
    raise RuntimeError("Required: Python version > 3.9")

with open("swan/version.py") as fp:
    d = {}
    exec(fp.read(), d)
    swan_version = d['version']

install_requirements = Path("./requirements.txt").read_text()

setup(
    name='python-swan',
    version=swan_version,
    packages=['swan',
              'swan.app',
              'swan.gui',
              'swan.resources',
              'swan.base',
              'swan.views',
              'swan.widgets',
              'tests',
              'doc'],
    url='https://github.com/INM-6/swan',
    download_url='https://github.com/INM-6/swan',
    license='BSD-3-Clause',
    author='SWAN authors and contributors',
    author_email='shashwat.sridhar.95@gmail.com',
    install_requires=install_requirements,
    dependency_links=['https://github.com/INM-6/python-neo'],
    description='Python based tool for tracking single units from spike sorted data across several '
                'electrophysiological recording sessions.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': ['swan = swan.app.start:launch']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering']
)
