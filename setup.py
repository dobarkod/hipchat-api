#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='hipchat-api',
    version='0.0.2',
    author='Senko Rasic',
    author_email='senko.rasic@goodcode.io',
    description='A Pythonic wrapper for the HipChat API',
    license='MIT',
    url='http://goodcode.io/',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    install_requires=[],
)
