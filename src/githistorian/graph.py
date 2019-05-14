# encoding: utf-8
from __future__ import print_function

# Silencing BROKEN PIPE errors
import sys
if sys.platform != 'win32':
    from signal import signal, SIGPIPE, SIG_DFL
    signal(SIGPIPE, SIG_DFL)

from .row import unroll as row_unroll
from .column import unroll as column_unroll
from .layout import Layout

class VisitOrder:

	def __init__ (self):
		self.content = []

	def push (self, arg):
		if len(arg) == 0: return
		for e in reversed(arg):
			self.content.insert(0, e)

	def is_empty (self):
		return len(self.content) == 0

	def has_more (self):
		return len(self.content)

	def pop (self):
		try: return self.content.pop(0)
		except: return None

# Bind commits to their children to construct the reverse graph: each parent
# notifies its children so they can reach it
def _bind_children (heads, db):

	order = VisitOrder()
	order.push(heads)

	while order.has_more():

		name = order.pop()
		commit = db.at(name)

		if commit.done: continue

		for i in commit.parent:
			db.at(i).add_child(name)

		order.push(db.skip_if_done(commit.parent))

		commit.done = 1

# Given a complete grid, compute layout and print it, straight or flipped as
# requested by options
def _print_graph (history, first, width, hflip, vflip):

	t = Layout(width + 1, hflip, vflip)
	name = first
	bigblock = []

	while name:

		node = history.at(name)
		transition, padding = t.compute_layout(node)

		block = ['\x1b[m%s\x1b[m %s' % (transition, node.message[0])]
		for i in node.message[1:]: block.append('\x1b[m%s\x1b[m %s' % (padding, i))

		if vflip: bigblock.append('\n'.join(block))
		else: print('\n'.join(block))

		name = node.bottom

	if vflip:
		bigblock.reverse()
		print('\n'.join(bigblock))

def deploy (opt, roots, history):

	_bind_children(roots, history)
	history.clear()
	first = row_unroll(roots, history, opt.mingle, opt.flip)
	history.clear()
	width = column_unroll(roots, history, opt.flip)

	try: _print_graph(history, first, width, opt.hflip, opt.vflip)
	except BrokenPipeError: pass

	return 0

