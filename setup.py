from io import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='fmsquared',
	version='1.0.0',
	description='A tool to create collage images using data from Last FM',
	author='Shoot',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Shoot/FMSquared',
	packages=find_packages(),
	install_requires=[
		'numpy',
		'scipy',
		'Pillow',
		'requests',
	],
	entry_points={
		'console_scripts': [
			'fmsquared = fmsquared.__main__:main'
		]
	}
)