import os
from setuptools import setup, find_packages

setup(
    name='authentication',
    version='1.0',
    description='for authenticating users',
    packages=find_packages(),
    install_requires=[
        'Django',
    ],
)