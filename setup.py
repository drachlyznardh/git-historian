
from setuptools import setup, find_packages

with open('VERSION', 'r') as ifd:
    version = ifd.read().strip()

with open('README.md', 'r') as ifd:
	readme = ifd.read()

setup(
	name='githistorian',
	version=version,
	url='https://github.com/drachlyznardh/githistorian',
	author='Ivan Simonini',
	author_email='drachlyznardh@gmail.com',
	description='Graph visualizer for git history',
	long_description=readme,
	long_description_content_type='text/markdown',
	package_dir={'':'src'},
	packages=find_packages(where='src'),
	install_requires=['bintrees'],
	entry_points = { 'console_scripts': ['githistorian=githistorian.githistorian:tell_the_story'] },
	package_data={'': ['VERSION']},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
