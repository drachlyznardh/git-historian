# encoding: utf-8

from .order import RowOrder

class Row:

	def __init__ (self, db, heads):

		self.db = db
		self.heads = heads

	def unroll (self, debug):

		if debug: print '-- Row Unroll --'

		# Visit starts with all the heads
		self.visit = RowOrder()
		self.visit.push(self.heads)

		# Reference to previous node, to build the chain
		self.previous = None

		# Starting over the first row
		self.row = -1

		# The first node
		self.first = None

		while self.visit.has_more():

			name = self.visit.pop()
			target = self.db.at(name)

			if debug:
				print 'Visiting %s %s' % (name[:7], self.visit.show())

			# Even if done, a node can drop down in the chain after its
			# last-calling child
			if target.done:

				# No need to drop down beyond the last element
				if self.previous == target.name: continue

				# Binding top and bottom nodes together
				if target.top:
					self.db.at(target.top).bottom = target.bottom
				self.db.at(target.bottom).top = target.top

				# Binding previous and current nodes together
				target.top = self.previous
				self.db.at(previous).bottom = name

				# Bumping the row number another time
				row += 1
				target.row = row

				# This node is now the last
				target.bottom = None

				# Recording current node as the next previous
				self.previous = name
				continue

			# No node can appear before any of its children
			children = self.db.skip_if_done(target.child)
			if len(children): continue

			# Bind this node with the previous, if any, or…
			if self.previous:
				target.top = self.previous
				self.db.at(self.previous).bottom = name

			# … record this node as the first in the chain
			else: self.first = name

			# Bumping the row number
			self.row += 1
			target.row = self.row

			# Add parents to the visit
			self.visit.push(self.db.skip_if_done(target.parent))

			# The current node is the next previous
			self.previous = name

			# The current node is done
			target.done = 1

		return self.first

