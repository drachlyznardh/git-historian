# Main module for Git-Historian
# -*- encoding: utf-8 -*-

from .option import parse_cmd_args
from .hunter import HeadHunter, HistoryHunter
from .order import LeftmostFirst, RowOrder

from .column import Column
from .layout import Layout

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

