from distutils.core import setup
__version__ = open('src/githistorian/VERSION').read().strip()
setup(
	name='githistorian',
	version=__version__,
	url='https://github.com/drachlyznardh/githistorian',
	author='Ivan Simonini',
	author_email='drachlyznardh@gmail.com',
	package_dir={'githistorian':'src/githistorian'},
	packages=['githistorian']
)
