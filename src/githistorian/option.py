# Option module for Git-Historian
# -*- encoding: utf-8 -*-

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

	def print_version(self):
		print "Git-Historian %s (C) 2014 Ivan Simonini" % self.version

	def parse (self):

		try:
			optlist, args = getopt.gnu_getopt(sys.argv[1:], 'ahvDd:n:p:x',
				['help', 'verbose', 'version',
				'all', 'all-heads',
				'limit', 'pretty',
				'debug', 'all-debug',
				'--exact', '--exact-match', '--prefix', '--prefix-match'])
		except getopt.GetoptError as err:
			print str(err)
			self.print_help()
			sys.exit(2)

		for key, value in optlist:
			if key in ('-h', '--help'):
				self.print_help()
				sys.exit(0)
			elif key in ('-v', '--verbose'):
				self.verbose = 1
			elif key in ('-a', '--all', '--all-heads'):
				self.all_heads = 1
			elif key in ('-D', '--all-debug'):
				self.all_debug = 1
			elif key in ('-d', '--debug'):
				self.debug += int(value)
			elif key in ('-n', '--limit'):
				self.size_limit = int(value)
			elif key in ('-p', '--pretty'):
				self.pretty = value
			elif key in ('-x', '--exact', '--exact-match'):
				self.match = True
			elif key in ('--prefix', '--prefix-match'):
				self.match = False
			elif key == '--version':
				self.print_version()
				sys.exit(0)

		self.args = args
	
	def d (self, value):
		return self.all_debug or self.debug / value % 2

def _print_help ():

	print "Usage: %s [options] heads…" % sys.argv[0]
	print
	print ' -a, --all, --all-heads : consider all refnames'
	print ' -n, --limit : size limit'
	print ' -p, --pretty : format options'
	print
	print ' --prefix, --prefix-match   : arguments match refnames by prefix'
	print ' -x, --exact, --exact-match : arguments must match refnames exactly'
	print
	print ' -D, --all-debug : print all kinds of debug messages'
	print ' -d N, --debug N : add N to the debug counter'
	print
	print 'debug  1 : show heads'
	print 'debug  2 : show data loading'
	print 'debug  4 : show bindings'
	print 'debug  8 : show vertical unroll'
	print 'debug 16 : show column assignments'
	print 'debug 32 : show layout construction'

def parse_cmd_args():

	sopts = 'ahvDd:n:p:x'
	lopts = ['help', 'verbose', 'version',
			'all', 'all-heads',
			'limit', 'pretty',
			'debug', 'all-debug',
			'--exact', '--exact-match', '--prefix', '--prefix-match']

	try:
		optlist, args = getopt.gnu_getopt(sys.argv[1:], sopts, lopts)
	except getopt.GetoptError as err:
		print str(err)
		self.print_help()
		sys.exit(2)

	o = Option()

	for key, value in optlist:
		if key in ('-h', '--help'):
			o.print_help()
			sys.exit(0)
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
			o.print_version()
			sys.exit(0)

	o.args = args

