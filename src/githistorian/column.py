# encoding: utf-8

import bintrees

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
			print 'WTF is %s?' % arg
			return

		if len(arg) == 0: return

		self.content.extend(arg)

	def pop (self):
		try: return self.content.pop(0)
		except: return None

	def show (self):
		return '    [%s]' % ', '.join([e[:7] for e in self.content])

class Grid:

	def __init__ (self):
		self.store = {}

	def at (self, index):
		try:
			return self.store[index]
		except:
			#self.store[index] = bintrees.RBTree()
			self.store[index] = bintrees.BinaryTree()
			return self.store[index]

	def add (self, column, row, name):
		t = self.at(column)
		t.insert(row, name)

	def remove (self, column, row):
		t = self.at(column)
		t.remove(row)

	def upper (self, column, row):
		try:
			key, value = self.at(column).prev_item(row)
			return value
		except KeyError: return None

	def lower (self, column, row):
		try:
			key, value = self.at(column).succ_item(row)
			return value
		except KeyError: return None

class Column:

	def __init__ (self, db, heads):

		self.verbose = 0

		self.first = None
		self.width = -1

		self.db = db
		self.heads = heads

	def update_width (self, value):
		self.width = max(self.width, value)

	def find_column_for_head (self, name, debug):

		if debug: print '%s has to find its own column!!!' % name [:7]
		target = self.db.at(name)

		# Start at the immediate right of previous head
		previous = self.heads[self.heads.index(name) - 1]
		column = self.db.at(previous).column + 1
		if debug: print '  %s, Starting from column %d' % (name[:7], column)

		while 1:
			self.grid.add(column, target.row, 'MARKER')
			if self.lower_check(target, column) and self.upper_check(target, column):
				self.grid.add(column, target.row, name)
				target.set_column(column)
				self.update_width(column)
				if debug: print 'Test passed! %s on %d' % (target.name[:7], target.column)
				break

			self.grid.remove(column, target.row)
			column += 1
		return

	# This checks whether the target row overlaps with any arrow between
	# the upper node on the column and its parents
	def upper_check (self, target, column):

		upper = self.grid.upper(column, target.row)
		if not upper: return True
		parents = self.db.at(upper).parent
		if len(parents) == 0: return True
		lowest = max([self.db.at(e).row for e in parents])
		return lowest <= target.row

	# This checks whether the row of the following node on column overlaps
	# with any arrow between the target and its parents
	def lower_check (self, target, column):

		lower = self.grid.lower(column, target.row)
		if not lower: return True
		if len(target.parent) == 0: return True
		lowest = max([self.db.at(e).row for e in target.parent])
		return lowest <= self.db.at(lower).row

	def find_column_for_parents (self, name, debug):

		target = self.db.at(name)

		# Parents are processed in row order, from lower to upper
		target.parent.sort(key=lambda e: self.db.at(e).row, reverse=True)

		for parent in [self.db.at(e) for e in target.parent]:

			# If a parent has already a column, just push its border
			if parent.has_column():
				parent.set_border(target.column)
				if debug: print 'Pushing border (%s) to (%d)' % (parent.name[:7], parent.border)
				continue

			column = self.db.select_starting_column(parent.child)
			while 1:
				self.grid.add(column, parent.row, 'MARKER')

				if self.upper_check(parent, column) and self.lower_check(parent, column):
					self.grid.add(column, parent.row, parent.name)
					parent.set_column(column)
					self.update_width(column)
					if debug: print 'Both tests passed! %s on %d' % (parent.name[:7], column)
					break

				self.grid.remove(column, parent.row)
				column += 1
		return

	def unroll (self, debug):

		if debug: print '-- Column Unroll --'

		self.width = -1
		self.grid = Grid()

		# The order starts for the named heads
		order = VisitOrder()
		order.push(self.heads)

		while order.has_more():

			name = order.pop()
			target = self.db.at(name)
			
			# No node is processed more than once
			if target.done: continue

			if debug: print '  Visiting %s' % name[:7]

			# If a node is a named head and has not yet a column assigned, it
			# must look for a valid column on its own
			if target.name in self.heads and not target.has_column():
				self.find_column_for_head (name, debug)

			# The node assigns a column to each of its parents, in order,
			# ensuring each starts off on a valid position
			self.find_column_for_parents (name, debug)

			# Parents are added to the order, then the node is done
			order.push(self.db.skip_if_done(target.parent))
			target.done = 1

		return self.width

def unroll (db, heads, debug):
	return Column(db, heads).unroll(debug)
