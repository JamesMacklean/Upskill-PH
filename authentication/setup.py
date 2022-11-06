import os
from setuptools import setup, find_packages

# Main ##############################################################

setup(
    name='authentication',
    version='1.0',
    description='Scholar Profiles',
    packages=find_packages(exclude=['test']),
    install_requires=[
        'Django',
    ],
)