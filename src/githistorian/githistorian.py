# Main module for Git-Historian
# -*- encoding: utf-8 -*-

from .option import parse_cmd_args
from .hunter import HeadHunter, HistoryHunter
from .order import LeftmostFirst

from .row import Row
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
	#first = _row_unroll(opt.d(8), heads, db)
	first= Row(db, heads).unroll(opt.d(8))
	db.clear()
	width = Column(db, heads).unroll(opt.d(16))
	_print_graph(opt.d(32), db, first, width)

