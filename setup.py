
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='argupdate',
    version='0.1.0',
    description='Dynamically update a functions arguments before passing them in.',
    python_requires='==3.*,>=3.8.0',
    author='Dustin Wyatt',
    author_email='dustin.wyatt@gmail.com',
    license='MIT',
    classifiers=['Programming Language :: Python :: 3.8', 'License :: OSI Approved :: MIT License', 'Operating System :: OS Independent'],
    packages=['argupdate'],
    package_data={},
    install_requires=[],
)
