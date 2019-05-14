
from setuptools import setup, find_packages
from setuptools.extension import Extension
from distutils.command.build_py import build_py
from distutils.command.install_lib import install_lib

with open('VERSION', 'r') as ifd:
    version = ifd.read().strip()

class MyBuildPy(build_py):

	def addCustomVersion(self):
		import os
		from distutils.file_util import copy_file
		_, srcdir, destdir, _ = self.data_files[0]
		copy_file('VERSION', os.path.join(destdir, 'VERSION'))
		# copy_file(os.path.join(srcdir, 'VERSION'), os.path.join(destdir, 'VERSION'))

	def run(self):
		build_py.run(self)
		if not self.dry_run: self.addCustomVersion()

class MyInstallLib(install_lib):

	def addCustomVersion(self):
		print(self)
		for e in self.__dict__: print(e)
		print(self.distribution)
		print('From {} to {}'.format(self.build_dir, self.install_dir))
		return
		import os
		from distutils.file_util import copy_file
		_, srcdir, destdir, _ = self.data_files[0]
		# copy_file('VERSION', os.path.join(destdir, 'VERSION'))
		# copy_file(os.path.join(srcdir, 'VERSION'), os.path.join(destdir, 'VERSION'))
		print(self.data_files)

	def run(self):
		install_lib.run(self)
		if not self.dry_run: self.addCustomVersion()

setup(
	name='githistorian',
	version=version,
	url='https://github.com/drachlyznardh/githistorian',
	author='Ivan Simonini',
	author_email='drachlyznardh@gmail.com',
	package_dir={'':'src'},
	packages=find_packages(where='src'),
	install_requires=['bintrees'],
	entry_points = { 'console_scripts': ['githistorian=githistorian.githistorian:tell_the_story'] },
	cmdclass = { 'build_py': MyBuildPy, 'install_lib': MyInstallLib }
)
