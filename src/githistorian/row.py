# encoding: utf-8

class VisitOrder:

	def __init__ (self, mingle):
		self.content = []
		self.mingle = mingle

	def has_more (self):
		return len(self.content)

	def push (self, arg):
		if len(arg) == 0: return
		if self.mingle: self.content.extend(reversed(arg))
		else:
			for e in reversed(arg): self.content.insert(0, e)

	def pop (self):
		try: return self.content.pop(0)
		except: return None

	def show (self):
		return '    [%s]' % ', '.join([e[:7] for e in self.content])

class Row:

	def __init__ (self, heads, history):
		self.heads = heads
		self.history = history

	def if_done (self, name, target):

		# No need to drop down beyond the last element
		if self.previous == target.name: return

		# Binding top and bottom nodes together
		if target.top:
			self.history.at(target.top).bottom = target.bottom
		self.history.at(target.bottom).top = target.top

		# Binding previous and current nodes together
		target.top = self.previous
		self.history.at(self.previous).bottom = name

		# Bumping the row number another time
		self.row += 1
		target.row = self.row

		# This node is now the last
		target.bottom = None

		# Recording current node as the next previous
		self.previous = name

	def if_not_done (self, name, target):

		# No node can appear before any of its children
		children = self.history.skip_if_done(target.child)
		if len(children): return

		# Bind this node with the previous, if any, or…
		if self.previous:
			target.top = self.previous
			self.history.at(self.previous).bottom = name

		# … record this node as the first in the chain
		else: self.first = name

		# Bumping the row number
		self.row += 1
		target.row = self.row

		# Add parents to the order
		self.order.push(self.history.skip_if_done(target.parent))

		# The current node is the next previous
		self.previous = name

		# The current node is done
		target.done = 1

	def unroll (self, mingle, flip):

		# Visit starts with all the heads
		self.order = VisitOrder(mingle)
		if flip: self.heads.reverse()
		self.order.push(self.heads)

		# Reference to previous node, to build the chain
		self.previous = None

		# Starting over the first row
		self.row = -1

		# The first node
		self.first = None

		while self.order.has_more():

			name = self.order.pop()
			target = self.history.at(name)

			# Even if done, a node can drop down in the chain after its
			# last-calling child
			if target.done: self.if_done(name, target)
			else: self.if_not_done(name, target)

		return self.first

def unroll (heads, history, mingle, flip):
	return Row(heads, history).unroll(mingle, flip)

