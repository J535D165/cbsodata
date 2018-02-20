from setuptools import setup

from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

# Use readme as long description
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Extract version from cbsodata.py
for line in open('cbsodata.py'):
    if line.startswith('__version__'):
        exec(line)
        break

setup(
    name='cbsodata',
    version=__version__,  # noqa
    description='Statistics Netherlands opendata API client for Python',
    long_description=long_description,
    url='https://github.com/J535D165/cbsodata',
    author='Jonathan de Bruin',
    author_email='jonathandebruinos@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='cbs statistics odata netherlands dutch',
    install_requires=['requests'],
    py_modules=['cbsodata'],
    tests_require=[
        'nose',
        'nose-parameterized'
    ],
)
