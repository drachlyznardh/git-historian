# encoding: utf-8

from .row import unroll as row_unroll
from .column import unroll as column_unroll
from .layout import Layout

class LeftmostFirst:

	def __init__ (self):

		self.content = []

	def push (self, arg):

		if isinstance(arg, basestring):
			self.content.insert(0, arg)
			return

		if not isinstance(arg, list):
			print('WTF is %s?' % arg)
			return

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

def _bind_children (heads, db):

	visit = LeftmostFirst()
	visit.push(heads)

	while visit.has_more():

		name = visit.pop()
		commit = db.at(name)

		if commit.done: continue

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

	_bind_children(roots, history)
	history.clear()
	first = row_unroll(history, roots, opt.d(8))
	history.clear()
	width = column_unroll(history, roots, opt.d(16))
	_print_graph(history, first, width)

