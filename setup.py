# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in delivery_integration/__init__.py
from delivery_integration import __version__ as version

setup(
	name='delivery_integration',
	version=version,
	description='App for Manage Third Party of Delivery Method',
	author='DAS',
	author_email='digitalasiasolusindo.developer@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
