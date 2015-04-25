# Main module for Git-Historian
# -*- encoding: utf-8 -*-

import bintrees

from .option import parse_cmd_args
from .hunter import HeadHunter, HistoryHunter
from .order import LeftmostFirst, ColumnOrder, RowOrder

from .layout import Layout

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

# Due to excessively restricting size limit, some heads may not appear at
# all in the database. These heads are removed from the list
def _drop_missing_heads (heads, db):
	available = []
	for name in heads:
		if name in db.store:
			available.append(name)
	return available

def _bind_children (debug, heads, db):

	if debug: print '-- Binding Children --'

	visit = LeftmostFirst()
	visit.push(heads)

	while visit.has_more():

		name = visit.pop()
		commit = db.at(name)

		if debug: print '  Visiting %s' % name[:7]

		if commit.done:
			if debug: print '  %s is done, skipping…' % name[:7]
			continue

		for i in commit.parent:
			db.at(i).add_child(name)

		visit.push(db.skip_if_done(commit.parent))

		commit.done = 1

def _row_unroll (debug, heads, db):

	if debug: print '-- Row Unroll --'

	# Visit starts with all the heads
	visit = RowOrder()
	visit.push(heads)

	# Reference to previous node, to build the chain
	previous = None

	# Starting over the first row
	row = -1

	# The first node
	first = None

	while visit.has_more():

		name = visit.pop()
		target = db.at(name)

		if debug:
			print 'Visiting %s %s' % (name[:7], visit.show())

		# Even if done, a node can drop down in the chain after its
		# last-calling child
		if target.done:

			# No need to drop down beyond the last element
			if previous == target.name: continue

			# Binding top and bottom nodes together
			if target.top:
				db.at(target.top).bottom = target.bottom
			db.at(target.bottom).top = target.top

			# Binding previous and current nodes together
			target.top = previous
			db.at(previous).bottom = name

			# Bumping the row number another time
			row += 1
			target.row = row

			# This node is now the last
			target.bottom = None

			# Recording current node as the next previous
			previous = name
			continue

		# No node can appear before any of its children
		children = db.skip_if_done(target.child)
		if len(children): continue

		# Bind this node with the previous, if any, or…
		if previous:
			target.top = previous
			db.at(previous).bottom = name

		# … record this node as the first in the chain
		else: first = name

		# Bumping the row number
		row += 1
		target.row = row

		# Add parents to the visit
		visit.push(db.skip_if_done(target.parent))

		# The current node is the next previous
		previous = name

		# The current node is done
		target.done = 1

	return first

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

	def column_unroll (self, debug):

		if debug: print '-- Column Unroll --'

		self.width = -1
		self.grid = Grid()

		# The visit starts for the named heads
		visit = ColumnOrder()
		visit.push(self.heads)

		while visit.has_more():

			name = visit.pop()
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

			# Parents are added to the visit, then the node is done
			visit.push(self.db.skip_if_done(target.parent))
			target.done = 1

		return self.width

def _print_graph (debug, db, first, width):

	if debug: print '-- Print Graph --'

	t = Layout(width + 1, db, debug)

	name = first

	while name:

		node = db.at(name)
		if not node:
			print "No Commit for name %s" % name[:7]
			break

		if debug: print "\nP %s" % name[:7]

		t.compute_layout(node)

		try:
			print '\x1b[m%s\x1b[m %s' % (t.draw_transition(), node.message[0])
			for i in node.message[1:]:
				print '\x1b[m%s\x1b[m %s' % (t.draw_padding(), i)
		except IOError as error: return

		name = node.bottom

	def tell_the_story(self):

		# Hunting for history
		self.head = HeadHunter(self.o, self.o.d(1)).hunt()
		self.db = HistoryHunter(self.head, self.o, self.o.d(2)).hunt(self.o.size_limit)

		# Cleaning database from missing refs
		self.db.drop_missing_refs()
		self.drop_missing_heads()

		# Graph unrolling
		self.bind_children(self.o.d(4))
		self.db.clear()
		self.row_unroll(self.o.d(8))
		self.db.clear()
		self.column_unroll(self.o.d(16))
		self.print_graph(self.o.d(32))

		return

def tell_the_story():

	opt = parse_cmd_args()
	if not opt: return

	# Hunting for history
	heads = HeadHunter(opt, opt.d(1)).hunt()
	db = HistoryHunter(heads, opt, opt.d(2)).hunt(opt.size_limit)

	# Cleaning database from missing refs
	db.drop_missing_refs()
	heads = _drop_missing_heads(heads, db)

	# Graph unrolling
	_bind_children(opt.d(4), heads, db)
	db.clear()
	first = _row_unroll(opt.d(8), heads, db)
	db.clear()
	width = Column(db, heads).column_unroll(opt.d(16))
	_print_graph(opt.d(32), db, first, width)

