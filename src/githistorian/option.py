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
		self.mingle  = False
		self.flip    = False
		self.hflip   = False
		self.vflip   = False

		self.order   = []
		self.targets = []

		self.pretty  = False
		self.limit   = False
		self.match   = False

		self.mode    = 0

		self.needColorTrick = False

		version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
		self.version = open(version_file, 'r').read().strip()

	def override (self, other):

		self.verbose |= other.verbose

		self.heads   |= other.heads
		self.tags    |= other.tags
		self.remotes |= other.remotes
		self.mingle  |= other.mingle
		self.flip    |= other.flip
		self.hflip   |= other.hflip
		self.vflip   |= other.vflip

		if other.order: self.order = other.order
		if other.targets: self.targets = other.targets

		if other.pretty: self.pretty = other.pretty

		self.limit   |= other.limit
		self.match   |= other.match

		self.mode    |= other.mode

		return self

def _print_help ():

	print('Usage: %s [options] targets…' % sys.argv[0])
	print()
	print(' -a, --all, --heads : adds all heads to targets')
	print(' -t, --tags         : adds all tags to targets')
	print(' -r, --remotes      : adds all remote branches to targets')
	print()
	print(' -n<N>, --limit <N>  : cuts history to N commits')
	print(' -p<P>, --pretty <P> : uses P as the pretty format for messages')
	print()
	print(' -o<name[,names...]>, --order <name[,names...]> : show all targets in order')
	print()
	print(' --prefix, --prefix-match   : arguments match refnames by prefix')
	print(' -x, --exact, --exact-match : arguments must match refnames exactly')
	print()
	print(' -M, --mingle                          : interlap commit from parallel branches')
	print(' -F, --flip, --flip-heads              : flip heads from top to bottom')
	print(' -H, --horizontal, --flip-horizontally : flip layout from left to right')
	print(' -V, --vertical, --flip-vertically     : flip layout from top to bottom')
	print()
	print(' -f<name>, --file<name> : load preferences from <name> instead of default .githistorian')
	print()
	print(' -m[0,1], --mode[01] : select original bintrees mode [0, default] or new sortedcontainer mode [1, experimental]')

def _print_version (o):
	print("Git-Historian %s © 2014-2017 Ivan Simonini" % o.version)

def _parse(args, sopts, lopts):

	option = Option()
	filename = '.githistorian'

	try:
		optlist, args = getopt.gnu_getopt(args, sopts, lopts)
	except getopt.GetoptError as err:
		_print_help()
		return False, None

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
		elif key in ('-o', '--order'):
			option.order = value.split(',')
		elif key == '--version':
			_print_version(option)
			return False, False
		elif key in ('-f', '--file'):
			filename = value
		elif key in ('-M', '--mingle'):
			option.mingle = True
		elif key in ('-F', '--flip', '--flip-heads'):
			option.flip = True
		elif key in ('-H', '--horizontal', '--flip-horizontally'):
			option.hflip = True
		elif key in ('-V', '--vertical', '--flip-vertically'):
			option.vflip = True
		elif key in ('-m', '--mode'):
			option.mode = int(value)

	option.targets = args

	return option, filename

def parse (inargs):

	sopts = 'atrhvn:p:xo:MFHVm:'
	lopts = ['help', 'verbose', 'version',
			'all', 'heads', 'tags', 'remotes',
			'limit=', 'pretty=',
			'exact', 'exact-match', 'prefix', 'prefix-match',
			'order=',
			'mingle',
			'flip', 'flip-heads',
			'horizontal', 'flip-horizontally',
			'vertical', 'flip-vertically',
			'mode']

	option, filename = _parse(inargs or sys.argv[1:], sopts+'f:', lopts+['file'])
	if not option: return False

	if filename and os.path.exists(filename):
		token = []
		for line in open(filename, 'r').readlines():
			token.append(line.strip())

		doption, dfile = _parse(token, sopts, lopts)
	else: doption = Option()

	return doption.override(option)

