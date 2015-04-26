# encoding: utf-8

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

def _print_graph (db, first, width):

	t = Layout(width + 1)
	name = first

	while name:

		node = db.at(name)
		transition, padding = t.compute_layout(node)

		print('\x1b[m%s\x1b[m %s' % (transition, node.message[0]))
		for i in node.message[1:]: print('\x1b[m%s\x1b[m %s' % (padding, i))

		name = node.bottom

def deploy (opt, roots, history):

	_bind_children(opt.d(4), roots, history)
	history.clear()
	first = row_unroll(history, roots, opt.d(8))
	history.clear()
	width = column_unroll(history, roots, opt.d(16))
	_print_graph(history, first, width)

