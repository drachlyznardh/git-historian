# encoding: utf-8
from __future__ import print_function

import sys
import os
import getopt

class Option:

	def __init__ (self):

		self.verbose = 0

		self.heads   = False
		self.tags    = False
		self.remotes = False
		self.order   = []

		self.pretty = False
		self.limit  = False
		self.match  = False

		version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
		self.version = open(version_file, 'r').read().strip()

	def override (self, other):

		self.verbose |= other.verbose

		self.heads   |= other.heads
		self.tags    |= other.tags
		self.remotes |= other.remotes
		self.order.extend(other.order)

		self.pretty |= other.pretty
		self.limit  |= other.limit
		self.match  |= other.match

def _print_help ():

	print('Usage: %s [options] targets…' % sys.argv[0])
	print()
	print(' -a, --all, --heads : adds all heads to targets')
	print(' -t, --tags         : adds all tags to targets')
	print(' -r, --remotes      : adds all remote branches to targets')
	print()
	print(' -n<N>, --limit<N>  : cuts history to N commits')
	print(' -p<P>, --pretty<P> : uses P as the pretty format for messages')
	print()
	print(' --prefix, --prefix-match   : arguments match refnames by prefix')
	print(' -x, --exact, --exact-match : arguments must match refnames exactly')
	print()
	print(' -f<name>, --file<name> : load preferences from <name> instead of default .githistorian')

def _print_version (o):
	print("Git-Historian %s © 2014-2015 Ivan Simonini" % o.version)

def _parse(args, sopts, lopts):

	option = Option()
	filename = False

	try:
		optlist, args = getopt.gnu_getopt(sys.argv[1:], sopts, lopts)
	except getopt.GetoptError as err:
		_print_help()
		return False

	for key, value in optlist:
		if key in ('-h', '--help'):
			_print_help()
			return False, False
		elif key in ('-v', '--verbose'):
			option.verbose = 1
		elif key in ('-a', '--all', '--heads'):
			option.heads = True
		elif key in ('-t', '--tags'):
			option.tags = True
		elif key in ('-r', '--remotes'):
			option.remotes = True
		elif key in ('-n', '--limit'):
			option.limit = int(value)
		elif key in ('-p', '--pretty'):
			option.pretty = value
		elif key in ('-x', '--exact', '--exact-match'):
			option.match = True
		elif key in ('--prefix', '--prefix-match'):
			option.match = False
		elif key == '--version':
			_print_version(option)
			return False, False
		elif key in ('-f', '--file'):
			filename = value

	return filename, option

def parse ():

	sopts = 'atrhvn:p:x'
	lopts = ['help', 'verbose', 'version',
			'all', 'heads', 'tags', 'remotes',
			'limit', 'pretty',
			'exact', 'exact-match', 'prefix', 'prefix-match']

	option, filename = _parse(sys.argv[1:], sopts+'f:', lopts+['file'])
	if not option: return False

	if filename and os.path.exists(filename):
		token = []
		for line in open(filename, 'r').readlines():
			token.extend(line.strip().split())

		doption, dfile = _parse(token, sopts, lopts)
	else: doption = Option()

	return doption.override(option)
		

	try:
		optlist, args = getopt.gnu_getopt(sys.argv[1:], sopts, lopts)
	except getopt.GetoptError as err:
		_print_help()
		return False

	o = Option()
	filename = '.githistorian'

	for key, value in optlist:
		if key in ('-h', '--help'):
			_print_help()
			return False
		elif key in ('-v', '--verbose'):
			o.verbose = 1
		elif key in ('-a', '--all', '--heads'):
			o.heads = True
		elif key in ('-t', '--tags'):
			o.tags = True
		elif key in ('-r', '--remotes'):
			o.remotes = True
		elif key in ('-n', '--limit'):
			o.limit = int(value)
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

	if os.path.exists(filename):
		d = eval(open(filename, 'r').read())
	else: d = {}

	if 'order' in d:
		o.order = d['order']
		o.order.extend(args)
	else: o.order = args

	if 'pretty' in d and not o.pretty:
		o.pretty =  d['pretty']

	return o

