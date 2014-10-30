# Main module for Git-Historian
# -*- encoding: utf-8 -*-

import option
import hunter
import order

import layout

VERSION="0.0-c"

import bintrees

class Grid:

	def __init__ (self):
		self.store = {}

	def at (self, index):
		try:
			return self.store[index]
		except:
			self.store[index] = bintrees.RBTree()
			return self.store[index]

	def add (self, column, row, name):
		#print 'Adding (%d × %d) (%s)' % (column, row, name)
		t = self.at(column)
		t.insert(row, name)

	def remove (self, column, row):
		#print 'Removin (%d × %d)' % (column, row)
		t = self.at(column)
		t.remove(row)

	def upper (self, column, row):
		try:
			key, value = self.at(column).prev_item(row)
			#print 'Up   Grid (%d × %d) = %s' % (column, row, value)
			return value
		except KeyError: return None

	def lower (self, column, row):
		try:
			key, value = self.at(column).succ_item(row)
			#print 'Down Grid (%d × %d) = %s' % (column, row, value)
			return value
		except KeyError: return None

class Historian:

	def __init__ (self):

		self.verbose = 0

		self.head = []
		self.db = None

		self.first = None
		self.width = -1

		self.o = option.Option()
		self.o.parse()

	def update_width (self, value):
		self.width = max(self.width, value)

	def bind_children (self, debug):

		if debug: print '-- Binding Children --'

		visit = order.LeftmostFirst()
		visit.push(self.head)

		while visit.has_more():

			name = visit.pop()
			commit = self.db.at(name)

			if debug: print '  Visiting %s' % name[:7]

			if commit.done:
				if debug: print '  %s is done, skipping…' % name[:7]
				continue

			for i in commit.parent:
				self.db.at(i).add_child(name)

			visit.push(self.db.skip_if_done(commit.parent))

			commit.done = 1

	def row_unroll (self, debug):

		if debug: print '-- Row Unroll --'

		# Visit starts with all the heads
		visit = order.RowOrder()
		visit.push(self.head)

		# Reference to previous node, to build the chain
		previous = None

		# Starting over the first row
		row = -1

		while visit.has_more():

			name = visit.pop()
			target = self.db.at(name)

			if debug:
				print 'Visiting %s %s' % (name[:7], visit.show())

			# Even if done, a node can drop down in the chain after its
			# last-calling child
			if target.done:

				# No need to drop down beyond the last element
				if previous == target.name: continue

				# Binding top and bottom nodes together
				self.db.at(target.top).bottom = target.bottom
				self.db.at(target.bottom).top = target.top

				# Binding previous and current nodes together
				target.top = previous
				self.db.at(previous).bottom = name

				# Bumping the row number another time
				row += 1
				target.row = row

				# This node is now the last
				target.bottom = None

				# Recording current node as the next previous
				previous = name
				continue

			# No node can appear before any of its children
			children = self.db.skip_if_done(target.child)
			if len(children): continue

			# Bind this node with the previous, if any, or…
			if previous:
				target.top = previous
				self.db.at(previous).bottom = name

			# … record this node as the first in the chain
			else: self.first = name

			# Bumping the row number
			row += 1
			target.row = row

			# Add parents to the visit
			visit.push(self.db.skip_if_done(target.parent))

			# The current node is the next previous
			previous = name

			# The current node is done
			target.done = 1

	def find_column_for_head (self, name, grid, debug):

		if debug: print '%s has to find its own column!!!' % name [:7]
		target = self.db.at(name)

		# Start at the immediate right of previous head
		previous = self.head[self.head.index(name) - 1]
		column = self.db.at(previous).column + 1
		print '  %s, Starting from column %d' % (name[:7], column)

		while 1:
			grid.add(column, target.row, 'MARKER')
			if self.lower_check(target, column, grid):
				grid.remove(column, target.row)
				column += 1
			else:
				print 'Test passed! %s on %d' % (name[:7], column)
				grid.add(column, target.row, name)
				target.set_column(column)
				self.update_width(column)
				print 'Test passed! %s on %d' % (target.name[:7], target.column)
				break
		return

	# This should check whether the target row overlaps with any arrow between
	# the upper node on the column and its parents
	def upper_check (self, target, column, grid):

		upper = grid.upper(column, target.row)
		if not upper: return 0
		lowest = max([self.db.at(e).row for e in self.db.at(upper).parent])
		return lowest > target.row

	# This should check whether the row of the following node on column overlaps
	# with any arrow between the target and its parents
	def lower_check (self, target, column, grid):

		lower = grid.lower(column, target.row)
		if not lower: return 0
		if len(target.parent) == 0: return 0
		lowest = max([self.db.at(e).row for e in target.parent])
		return lowest > self.db.at(lower).row

	def find_column_for_parents (self, name, grid, debug):

		target = self.db.at(name)
		column = target.column

		print
		print '  Parents of (%s), starting on (%d)' % (name[:7],
			column)

		# Parents are processed in row order, from lower to upper
		target.parent.sort(key=lambda e: self.db.at(e).row, reverse=True)

		print '  Calling (%s)' % ', '.join([e[:7] for e in target.parent])

		for parent in [self.db.at(e) for e in target.parent]:

			# If a parent has already a column, the column next to its marks the
			# leftmost spot for the following parents, as the border for the
			# target node
			if parent.has_column():
				parent.set_border(target.column)
				column = parent.border + 1
				if debug: print 'Pushing column beyond %s\'s border %d' % (e[:7], parent.border)
				continue

			# Check should probably test whever the bounding boxes overlap. One
			# check between the lowest parent of previous node on column and the
			# target; one check between the lowest parent of target and the
			# following node on column
			upper_flag = 1
			lower_flag = 1
			while 1:

				# Try column
				grid.add(column, parent.row, 'MARKER')

				# Test
				upper_flag = self.upper_check(parent, column, grid)
				lower_flag = self.lower_check(parent, column, grid)

				# Verify
				if upper_flag or lower_flag:
					grid.remove(column, parent.row)
					column += 1
				else:
					print 'Both tests passed! %s on %d' % (e[:7], column)
					grid.add(column, parent.row, e)
					parent.set_column(column)
					self.update_width(column)
					break
		return

	def column_unroll (self, debug):

		if debug: print '-- Column Unroll --'

		self.width = -1
		grid = Grid()

		# The visit starts for the named heads
		visit = order.ColumnOrder()
		visit.push(self.head)

		while visit.has_more():

			name = visit.pop()
			target = self.db.at(name)
			
			# No node is processed more than once
			if target.done: continue

			if debug: print '  Visiting %s' % name[:7]

			# If a node is a named head and has not yet a column assigned, it
			# must look for a valid column on its own
			if target.name in self.head and not target.has_column():
				self.find_column_for_head (name, grid, debug)

			# The node assigns a column to each of its parents, in order,
			# ensuring each starts off on a valid position
			self.find_column_for_parents (name, grid, debug)

			# Parents are added to the visit, then the node is done
			visit.push(self.db.skip_if_done(target.parent))
			target.done = 1

	def print_graph (self, debug):
		
		if debug: print '-- Print Graph --'

		t = layout.Layout(self.width + 1, self.db, debug)
		h = hunter.MessageHunter()

		name = self.first

		while name:

			node = self.db.at(name)
			if not node:
				print "No Commit for name %s" % name[:7]
				break

			if debug: print "\nP %s" % name[:7]
			
			t.compute_layout(node)

			message = h.describe(name)

			try:
				print '%s\x1b[m %s' % (t.draw_transition(), message[0])
				for i in message[1:-1]:
					print '%s\x1b[m %s' % (t.draw_padding(), i)
			except IOError as error: return

			name = node.bottom

	def tell_the_story(self):

		self.head = hunter.HeadHunter(self.o, self.o.d(1)).hunt()
		self.db = hunter.HistoryHunter(self.head, self.o.d(2)).hunt()

		self.bind_children(self.o.d(4))
		self.db.clear()
		self.row_unroll(self.o.d(8))
		self.db.clear()
		self.column_unroll(self.o.d(16))
		self.print_graph(self.o.d(32))

		return

