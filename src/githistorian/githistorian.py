# Main module for Git-Historian
# -*- encoding: utf-8 -*-

from __future__ import print_function

from .hunter.head import hunt as head_hunt
from .hunter.history import hunt as history_hunt

from .option import parse_cmd_args
from .order import LeftmostFirst

from .row import unroll as row_unroll
from .column import unroll as column_unroll
from .layout import Layout

def _bind_children (debug, heads, db):

	if debug: print('-- Binding Children --')

	visit = LeftmostFirst()
	visit.push(heads)

	while visit.has_more():

		name = visit.pop()
		commit = db.at(name)

		if debug: print('  Visiting %s' % name[:7])

		if commit.done:
			if debug: print('  %s is done, skipping…' % name[:7])
			continue

		for i in commit.parent:
			db.at(i).add_child(name)

		visit.push(db.skip_if_done(commit.parent))

		commit.done = 1

def _print_graph (debug, db, first, width):

	if debug: print('-- Print Graph --')

	t = Layout(width + 1, debug)

	name = first

	while name:

		node = db.at(name)
		if not node:
			print("No Commit for name %s" % name[:7])
			break

		if debug: print("\nP %s" % name[:7])

		t.compute_layout(node)

		try:
			print('\x1b[m%s\x1b[m %s' % (t.draw_transition(), node.message[0]))
			for i in node.message[1:]:
				print('\x1b[m%s\x1b[m %s' % (t.draw_padding(), i))
		except: pass

		name = node.bottom

def _deploy_graph (opt, roots, history):

	_bind_children(opt.d(4), roots, history)
	history.clear()
	first = row_unroll(history, roots, opt.d(8))
	history.clear()
	width = column_unroll(history, roots, opt.d(16))
	_print_graph(opt.d(32), history, first, width)

def tell_the_story():

	opt = parse_cmd_args()
	if not opt: return

	# Hunting for history
	targets = head_hunt(opt, opt.d(1))
	roots, history = history_hunt(opt, targets, opt.limit)

	if opt.verbose:
		print('Targets order   %s' % opt.order)
		print('Targets found   %s' % targets)
		print('Roots displayed %s' % roots)

	# Graph unrolling
	_deploy_graph(opt, roots, history)
