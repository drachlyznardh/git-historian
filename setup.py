
from setuptools import setup, find_packages

with open('VERSION', 'r') as ifd:
    version = ifd.read().strip()

setup(
	name='githistorian',
	version=version,
	url='https://github.com/drachlyznardh/githistorian',
	author='Ivan Simonini',
	author_email='drachlyznardh@gmail.com',
	package_dir={'':'src'},
	packages=find_packages(where='src'),
	package_data={'': ['VERSION']},
	install_requires=['bintrees'],
	entry_points = { 'console_scripts': ['githistorian=githistorian.githistorian:tell_the_story'] },
)
