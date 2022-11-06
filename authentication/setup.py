import os
from setuptools import setup

# Main ##############################################################

setup(
    name='authentication',
    version='1.0',
    description='Scholar Profiles',
    packages=['scholarium'],
    install_requires=[
        'Django',
    ],
)