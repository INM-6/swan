from setuptools import setup
from sys import version_info


def readme():
    with open("README.rst") as f:
        return f.read()


if version_info < (3, 3):
    raise RuntimeError("Required: Python version > 3.3")


with open("swan/version.py") as fp:
    d = {}
    exec(fp.read(), d)
    swan_version = d['version']

install_requirements = ['numpy',
                        'quantities',
                        'PyQt5',
                        'pyqtgraph',
                        'odml',
                        'elephant',
                        'pyopengl',
                        'matplotlib',
                        'scikit-learn',
                        'psutil',
                        'neo']

setup(
    name='swan',
    version=swan_version,
    packages=['swan',
              'swan.gui',
              'swan.res',
              'swan.src',
              'swan.stg',
              'swan.tools.vumv.gui',
              'swan.tools.vumv.src',
              'tests',
              'doc'],
    url='https://github.com/INM-6/swan',
    download_url='https://github.com/INM-6/swan',
    license='BSD-3-Clause',
    author='SWAN authors and contributors',
    author_email='s.sridhar@fz-juelich.de',
    install_requires=install_requirements,
    dependency_links=['https://github.com/INM-6/python-neo'],
    description='Python based tool for tracking single units from spike sorted data across several '
                'electrophysiological recording sessions.',
    long_description=readme(),
    scripts=['scripts/swan'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering']
)
