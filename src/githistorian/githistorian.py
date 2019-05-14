# -*- encoding: utf-8 -*-
from __future__ import print_function
from subprocess import check_output, STDOUT

from .hunter.head import hunt as head_hunt
from .hunter.history import hunt as history_hunt
from .option import parse as parse_cmd_args

def tell_the_story(inargs=None):

	opt = parse_cmd_args(inargs)
	if not opt: return

	try: version = check_output('git --version'.split(), stderr=STDOUT, encoding='utf-8').strip()
	except:
		print('Git is not installed')
		return 1

	try: version = [x for x in version.split(' ')[2].split('.')]
	except:
		print('Unrecognized version %s' % version)
		return 1

	try: check_output('git rev-parse --git-dir'.split(), stderr=STDOUT)
	except:
		print('Not a repo')
		return 1

	# Hunting for history
	if int(version[0]) == 2 and int(version[1]) > 11: opt.needColorTrick = True
	targets = head_hunt(opt)
	roots, history = history_hunt(opt, targets, opt.limit)

	if opt.verbose:
		print('Targets list    %s' % opt.targets)
		print('Targets order   %s' % opt.order)
		print('Targets found   %s' % targets)
		print('Roots displayed %s' % roots)
		lines, commits, omitted = history.stats()
		print('Loaded %d commits, %d omitted' % (commits, omitted))

	# Graph unrolling
	if opt.mode == 1:
		from .alternate import deploy
		return deploy(opt, roots, history)

	from .graph import deploy as deploy_graph
	return deploy_graph(opt, roots, history)

