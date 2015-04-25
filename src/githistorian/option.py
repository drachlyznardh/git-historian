# Option module for Git-Historian
# encoding: utf-8

from __future__ import print_function

import sys
import os
import getopt

class Option:

	def __init__ (self):

		self.verbose = 0
		self.debug = 0
		self.all_debug = 0

		self.all_heads = 0
		self.head = []

		self.pretty = None
		self.size_limit = False
		self.match = False

		version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
		self.version = open(version_file, 'r').read().strip()

	def d (self, value):
		return self.all_debug or self.debug / value % 2

def _print_help ():

	print('Usage: %s [options] heads…' % sys.argv[0])
	print()
	print(' -a, --all, --all-heads : consider all refnames')
	print(' -n, --limit : size limit')
	print(' -p, --pretty : format options')
	print()
	print(' --prefix, --prefix-match   : arguments match refnames by prefix')
	print(' -x, --exact, --exact-match : arguments must match refnames exactly')
	print()
	print(' -f<name>, --file<name> : load preferences from <name> instead of default .githistorian')
	print()
	print(' -D, --all-debug : print(all kinds of debug messages')
	print(' -d N, --debug N : add N to the debug counter')
	print()
	print('debug  1 : show heads')
	print('debug  2 : show data loading')
	print('debug  4 : show bindings')
	print('debug  8 : show vertical unroll')
	print('debug 16 : show column assignments')
	print('debug 32 : show layout construction')

def _print_version (o):
	print("Git-Historian %s © 2014-2015 Ivan Simonini" % o.version)

def parse_cmd_args ():

	sopts = 'ahvDd:n:p:xf:'
	lopts = ['help', 'verbose', 'version',
			'all', 'all-heads',
			'limit', 'pretty',
			'debug', 'all-debug',
			'--exact', '--exact-match', '--prefix', '--prefix-match',
			'--file']

	try:
		optlist, args = getopt.gnu_getopt(sys.argv[1:], sopts, lopts)
	except getopt.GetoptError as err:
		_print_help()
		raise(err)

	o = Option()
	filename = '.githistorian'

	for key, value in optlist:
		if key in ('-h', '--help'):
			_print_help()
			return False
		elif key in ('-v', '--verbose'):
			o.verbose = 1
		elif key in ('-a', '--all', '--all-heads'):
			o.all_heads = 1
		elif key in ('-D', '--all-debug'):
			o.all_debug = 1
		elif key in ('-d', '--debug'):
			o.debug += int(value)
		elif key in ('-n', '--limit'):
			o.size_limit = int(value)
		elif key in ('-p', '--pretty'):
			o.pretty = value
		elif key in ('-x', '--exact', '--exact-match'):
			o.match = True
		elif key in ('--prefix', '--prefix-match'):
			o.match = False
		elif key == '--version':
			_print_version(o)
			return False
		elif key in ('-f', '--file'):
			filename = value

	o.args = args
	return o

