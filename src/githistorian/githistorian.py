# Main module for Git-Historian
# -*- encoding: utf-8 -*-

from __future__ import print_function

from .hunter.head import hunt as head_hunt
from .hunter.history import hunt as history_hunt
from .option import parse as parse_cmd_args
from .graph import deploy as deploy_graph

def tell_the_story():

	opt = parse_cmd_args()
	if not opt: return

	# Hunting for history
	targets = head_hunt(opt)
	roots, history = history_hunt(opt, targets, opt.limit)

	if opt.verbose:
		print('Targets order   %s' % opt.order)
		print('Targets found   %s' % targets)
		print('Roots displayed %s' % roots)

	# Graph unrolling
	deploy_graph(opt, roots, history)

