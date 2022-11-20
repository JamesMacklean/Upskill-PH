# -*- coding: utf-8 -*-
#
# Imports ###########################################################

import os
from setuptools import setup, find_packages

# Main ##############################################################

setup(
    name='authentication',
    version='1.0',
    description='for authenticating users',
    packages=find_packages(),
    install_requires=[
        'Django',
    ],
)