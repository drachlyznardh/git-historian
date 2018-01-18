# -*- encoding: utf-8 -*-
from __future__ import print_function
from subprocess import check_output, STDOUT

from .hunter.head import hunt as head_hunt
from .hunter.history import hunt as history_hunt
from .option import parse as parse_cmd_args
from .graph import deploy as deploy_graph

def get_version():

	try: return check_output('git --version'.split(), stderr=STDOUT).strip()
	except: return None

def tell_the_story():

	opt = parse_cmd_args()
	if not opt: return

	version = get_version()
	if not version:
		print('Git is not installed')
		return

	try:
		version = [int(x) for x in version.split(' ')[2].split('.')]
		if version[0] == 2 and version[1] > 11: opt.needColorTrick = True
	except:
		print('Unrecognized version %s' % version)
		return

	try: check_output('git rev-parse --git-dir'.split(), stderr=STDOUT)
	except:
		print('Not a repo')
		return

	# Hunting for history
	targets = head_hunt(opt)
	roots, history = history_hunt(opt, targets, opt.limit)

	if opt.verbose:
		print('Targets list    %s' % opt.targets)
		print('Targets order   %s' % opt.order)
		print('Targets found   %s' % [targets])
		print('Roots displayed %s' % roots)
		lines, commits, omitted = history.stats()
		print('Loaded %d commits, %d omitted' % (commits, omitted))

	# Graph unrolling
	deploy_graph(opt, roots, history)

