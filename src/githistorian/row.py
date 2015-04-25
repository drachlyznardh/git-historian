# encoding: utf-8

from __future__ import print_function

class VisitOrder:

	def __init__ (self):
		self.content = []

	def has_more (self):
		return len(self.content)

	def push (self, arg):

		if isinstance(arg, basestring):
			self.content.append(arg)
			return

		if not isinstance(arg, list):
			print('WTF is %s?' % arg)
			return

		if len(arg) == 0: return

		self.content.extend(reversed(arg))

	def pop (self):
		try: return self.content.pop(0)
		except: return None

	def show (self):
		return '    [%s]' % ', '.join([e[:7] for e in self.content])

class Row:

	def __init__ (self, db, heads):

		self.db = db
		self.heads = heads

	def if_done (self, name, target):

		# No need to drop down beyond the last element
		if self.previous == target.name: return

		# Binding top and bottom nodes together
		if target.top:
			self.db.at(target.top).bottom = target.bottom
		self.db.at(target.bottom).top = target.top

		# Binding previous and current nodes together
		target.top = self.previous
		self.db.at(self.previous).bottom = name

		# Bumping the row number another time
		self.row += 1
		target.row = self.row

		# This node is now the last
		target.bottom = None

		# Recording current node as the next previous
		self.previous = name

	def if_not_done (self, name, target):

		# No node can appear before any of its children
		children = self.db.skip_if_done(target.child)
		if len(children): return

		# Bind this node with the previous, if any, or…
		if self.previous:
			target.top = self.previous
			self.db.at(self.previous).bottom = name

		# … record this node as the first in the chain
		else: self.first = name

		# Bumping the row number
		self.row += 1
		target.row = self.row

		# Add parents to the order
		self.order.push(self.db.skip_if_done(target.parent))

		# The current node is the next previous
		self.previous = name

		# The current node is done
		target.done = 1

	def unroll (self, debug):

		if debug: print('-- Row Unroll --')

		# Visit starts with all the heads
		self.order = VisitOrder()
		self.order.push(self.heads)

		# Reference to previous node, to build the chain
		self.previous = None

		# Starting over the first row
		self.row = -1

		# The first node
		self.first = None

		while self.order.has_more():

			name = self.order.pop()
			target = self.db.at(name)

			if debug:
				print('Visiting %s %s' % (name[:7], self.order.show()))

			# Even if done, a node can drop down in the chain after its
			# last-calling child
			if target.done: self.if_done(name, target)
			else: self.if_not_done(name, target)

		return self.first

def unroll (db, heads, debug):
	return Row(db, heads).unroll(debug)

