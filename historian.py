# Main module for Git-Historian
# -*- encoding: utf-8 -*-

import sys
import getopt

import hunter
import order

import layout

VERSION="0.0-b"

class Option:

	def __init__ (self):

		self.verbose = 0
		self.debug = 0
		self.all_debug = 0

		self.all_heads = 0
		self.head = []
		self.head_by_name = {}
		self.node = {}

		self.first = None
		self.width = -1
		self.max_width = 0

		self.o = historian.Option()
		self.o.parse()

	def print_version(self):
		print "Git-Historian %s (C) 2014 Ivan Simonini" % VERSION

	def print_help(self):
		print "Usage: %s [options] heads…" % sys.argv[0]
		print
		print ' -D, --all-debug : print all kinds of debug messages'
		print ' -d N, --debug N : add N to the debug counter'
		print
		print 'debug  1 : show heads'
		print 'debug  2 : show data loading'
		print 'debug  4 : show bindings'
		print 'debug  8 : show vertical unroll'
		print 'debug 16 : show head jumps'
		print 'debug 32 : show column assignments'
		print 'debug 16 : show layout construction'

	def parse (self):

		try:
			optlist, args = getopt.gnu_getopt(sys.argv[1:], 'ahvDd:',
				['help', 'verbose', 'version',
				'all', 'all-heads',
				'debug', 'all-debug'])
		except getopt.GetoptError as err:
			print str(err)
			self.print_help()
			sys.exit(2)

		for key, value in optlist:
			if key in ('-h', '--help'):
				self.print_help()
				sys.exit(0)
			elif key in ('-v', '--verbose'):
				self.verbose = 1
			elif key in ('-a', '--all', '--all-heads'):
				self.all_heads = 1
			elif key in ('-D', '--all-debug'):
				self.all_debug = 1
			elif key in ('-d', '--debug'):
				self.debug += int(value)
			elif key == '--version':
				self.print_version()
				sys.exit(0)

		self.args = args
	
	def d (self, value):
		return self.all_debug or self.debug / value % 2

class Historian:

	def __init__ (self):

		self.verbose = 0
		self.debug = 0
		self.all_debug = 0

		self.all_heads = 0
		self.head = []
		self.head_by_name = {}
		self.node = {}

		self.first = None
		self.width = -1
		self.max_width = 0

	def select_column (self, commit, debug):

		if debug: print
		if not commit.top:
			if debug: print '  %s is the topmost' % commit.hash[:7]
			self.width += 1
			return self.width

		if len(commit.child) == 0:
			if debug: print '  %s has no children' % commit.hash[:7]
			self.width += 1
			#if len(self.skip_if_done(commit.parent)):
			#	self.width += 1
			return self.width

		result = self.width
		name = commit.top
		if debug: print '  Processing %s' % commit.hash[:7]
		while name:

			target = self.node[name]

			if name in commit.child and target.has_column():
				if debug: print '  %s is a child of %s (%d), halting' % (
					name[:7], commit.hash[:7],
					self.node[name].column)

				booked = 1 + max([self.node[j].column for j in target.parent])
				if debug: print booked
				column = max(result, target.column, booked)
				self.max_width = max(self.max_width, column)
				return column

			if debug: print '  Matching %s against %s (%d)' % (
				commit.hash[:7], name[:7], target.column)
			result = max(result, target.column)
			name = target.top

		if debug: print 'No assigned children found. Defaulting'
		self.width += 1
		return self.width

	def skip_if_done (self, names):

		result = []

		for name in names:
			if not self.node[name].done:
				result.append(name)

		return result

	def clear (self):

		for commit in self.node.values():
			commit.done = 0

	def bind_children (self, debug):

		if debug: print '-- Binding Children --'

		visit = order.LeftmostFirst()
		visit.push(self.head)

		while visit.has_more():

			name = visit.pop()
			commit = self.node[name]

			if debug: print '  Visiting %s' % name[:7]

			if commit.done:
				if debug: print '  %s is done, skipping…' % name[:7]
				continue

			for i in commit.parent:
				self.node[i].add_child(name)

			visit.push(self.skip_if_done(commit.parent))

			commit.done = 1

	def row_unroll (self, debug):

		if debug: print '-- Row Unroll --'

		visit = order.UppermostFirst()
		current = None

		for head in self.head:

			if debug: print '  Head %s' % head[:7]

			visit.push_children(head)

			while visit.has_more():
				
				name = visit.pop()
				commit = self.node[name]

				if debug: print '  Visiting %s' % name[:7]

				if commit.done:
					if debug: print '  %s is done, skipping…' % name[:7]
					continue

				children = self.skip_if_done(commit.child)
				if len(children):
					visit.push_children(children)
					continue

				if current:
					commit.top = current
					self.node[current].bottom = name
				else: self.first = name
				current = name

				visit.push_parents(self.skip_if_done(commit.parent))

				commit.done = 1

	def column_unroll (self, d1, d2):

		if d1 or d2: print '-- Column Unroll --'

		self.width = -1

		visit = order.LeftmostFirst()
		visit.push(self.head)

		while visit.has_more():

			name = visit.pop()
			commit = self.node[name]
			if d1 or d2: print '  Visiting %s' % name[:7]

			if commit.done: continue

			visit.push(self.skip_if_done(commit.parent))

			commit.column = self.select_column(commit, d2)
			commit.done = 1

	def print_graph (self, debug):
		
		if debug: print '-- Print Graph --'

		t = layout.Layout(self.max_width + 1, self.node, debug)
		h = hunter.MessageHunter()

		name = self.first

		while name:

			commit = self.node[name]
			if not commit:
				print "No Commit for name %s" % name[:7]
				break

			if debug: print "\nP %s" % name[:7]
			
			t.compute_layout(commit)

			message = h.describe(name)

			print '%s\x1b[m %s' % (t.draw_transition(), message[0])
			for i in message[1:-1]:
			#for i in message[1:]:
				print '%s\x1b[m %s' % (t.draw_padding(), i)

			name = commit.bottom

	def tell_the_story(self):

		self.head = hunter.HeadHunter(self.o).hunt()
		self.node = hunter.HistoryHunter(self.o).hunt()

		self.bind_children(self.o.d(4))
		self.clear()
		self.row_unroll(self.o.d(8))
		self.clear()
		self.column_unroll(self.o.d(16), self.o.d(32))

		self.print_graph(self.o.d(64))

		return

