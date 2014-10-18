# Main module for Git-Historian
# -*- encoding: utf-8 -*-

from subprocess import check_output
from subprocess import CalledProcessError
import re
import sys
import getopt

import node
import order

import layout

VERSION="0.0-a"

class Historian:
	def __init__ (self):

		self.verbose = 0
		self.debug = 0
		self.all_debug = 0

		self.head = []
		self.head_by_name = {}
		self.commit = {}

		self.first = None
		self.width = -1
		self.max_width = 0
	
	def get_heads_by_name (self, name, debug):

		# Looking for heads, i.e. active branches
		cmdlist = ['git', 'show-ref', '--heads']

		# If names are specified, we look for them
		if name: cmdlist.append(name)

		# Print the command line request
		if debug: print cmdlist

		# Invoke Git
		try: git_output = check_output(cmdlist)
		except CalledProcessError as error:
			print 'Command `%s` returned %d' % (' '.join(cmdlist), error.returncode)
			sys.exit(1)
			return

		# Print the output
		if debug: print git_output

		# Parsing Git response
		for line in git_output.split('\n'):
			
			# Skipping empty lines (the last one should be empty)
			if len(line) == 0: continue
			
			# Matching hash and name
			hash_n_ref = re.compile(r'''(.*) refs\/.*\/(.*)''').match(line)

			# Broken ref: display message and skip line
			if not hash_n_ref:
				print 'No match for (%s)' % line
				continue

			# Save result in order and by name
			self.head.append(hash_n_ref.group(1))
			self.head_by_name[hash_n_ref.group(2)] = hash_n_ref.group(1)

		# Showing results
		if debug: print self.head
		if debug: print self.head_by_name

	def get_heads (self, debug):

		if len(self.args) == 0:
			self.get_heads_by_name(None, debug)
			return

		for name in self.args:
			self.get_heads_by_name(name, debug)

	def get_history(self, debug):

		# Looking for commit's and parents' hashes…
		cmdlist = ['git', 'log', '--pretty="%H %P"']

		# … starting from know heads only
		cmdlist.extend(self.head)

		# Print the request
		if debug: print cmdlist

		# Invoking Git
		git_history_dump = check_output(cmdlist)

		# Print the output
		if debug: print git_history_dump

		# Parsing Git response
		for line in git_history_dump.split('\n'):

			# Skipping empty lines (the last one should be empty)
			if len(line) == 0: continue

			# New node to store info
			current = node.Node()

			hashes = line[1:-1].split()

			# Store self
			current.hash = hashes[0]

			# Store parents
			for i in hashes[1:]: current.parent.append(i)

			current.missing = len(current.parent)

			# Store node in map
			self.commit[current.hash] = current

		# Showing results
		if debug: print self.commit

	def select_column (self, commit):

		debug = 1

		if debug: print
		if not commit.top:
			if debug: print '  %s is the topmost' % commit.hash[:7]
			self.width += 1
			return self.width

		if len(commit.child) == 0:
			if debug: print '  %s has no children' % commit.hash[:7]
			self.width += 1
			return self.width

		result = self.width
		name = commit.top
		if debug: print '  Processing %s' % commit.hash[:7]
		while name:

			target = self.commit[name]

			if name in commit.child and target.has_column():
				if debug: print '  %s is a child of %s (%d), halting' % (
					name[:7], commit.hash[:7],
					self.commit[name].column)

				booked = 1 + max([self.commit[j].column for j in target.parent])
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

	def jump_to_head (self, arg):

		result = []
		names = list(arg)

		while len(names):
			name = names.pop(0)
			commit = self.commit[name]
			print '  Jumping to head %s (%d) (%d)' % (name[:7],
				len(names), len(result))
			if commit.done: continue
			children = self.skip_if_done(commit.child)
			print '\t%s has %d undone children' % (name[:7], len(children))
			if len(children) == 0:
				result.append(name)
				continue

			names.extend(self.skip_if_marked_or_mark(children))
			continue

		print 'Result (%s)' % ', '.join(result)

		return result

	def skip_if_marked_or_mark (self, names):

		result = []

		for name in names:
			target = self.commit[name]
			if not target.mark:
				target.mark = 1
				result.append(name)

		return result

	def skip_if_done (self, names):

		result = []

		for name in names:
			if not self.commit[name].done:
				result.append(name)

		return result

	def clear (self):

		for commit in self.commit.values():
			commit.done = 0

	def bind_children (self, debug):

		if debug: print '-- Binding Children --'

		visit = order.LeftmostFirst()

		for head in self.head:

			if debug: print '  Head %s' % head[:7]

			visit.push(head)

			while 1:

				if visit.is_empty(): break

				name = visit.pop()
				commit = self.commit[name]

				if debug: print '  Visiting %s' % name[:7]

				if commit.done:
					if debug: print '  %s is done, skipping…' % name[:7]
					continue

				for i in commit.parent:
					self.commit[i].add_child(name)

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
				commit = self.commit[name]

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
					self.commit[current].bottom = name
				else: self.first = name
				current = name

				visit.push_parents(self.skip_if_done(commit.parent))

				commit.done = 1

	def column_unroll (self, debug):

		if debug: print '-- Column Unroll --'

		self.width = -1

		visit = order.LeftmostFirst()
		visit.push(self.head[0])

		while visit.has_more():

			name = visit.pop()
			commit = self.commit[name]
			if debug: print '  Visiting %s' % name[:7]

			if commit.done: continue

			visit.push(self.skip_if_done(commit.parent))
			visit.push(self.jump_to_head(commit.child))

			commit.column = self.select_column(commit)
			commit.done = 1

	def print_graph (self, debug):
		
		if debug: print '-- Print Graph --'

		t = layout.Layout(self.max_width + 1, self.commit, debug)

		cmdargs = 'git show -s --oneline --decorate --color'.split(' ')
		#cmdargs.append(optargs)

		name = self.first

		while name:

			commit = self.commit[name]
			if not commit:
				print "No Commit for name %s" % name[:7]
				break

			if debug: print "\nP %s" % name[:7]
			
			t.compute_layout(commit)

			cmdargs.append(commit.hash)

			message = check_output(cmdargs).split('\n')

			print '%s\x1b[m %s' % (t.draw_transition(), message[0])
			for i in message[1:-1]:
			#for i in message[1:]:
				print '%s\x1b[m %s' % (t.draw_padding(), i)

			cmdargs.pop() # Remove current commit name from arg list
			name = commit.bottom

	def print_version(self):
		print "Git-Historian %s (C) 2014 Ivan Simonini" % VERSION

	def print_help(self):
		print "Usage: %s " % sys.argv[0]

	def get_options(self):

		try:
			optlist, args = getopt.gnu_getopt(sys.argv[1:], 'hvDd:',
				['help', 'verbose', 'version',
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
			elif key in ('-D', '--all-debug'):
				self.all_debug = 1
			elif key in ('-d', '--debug'):
				self.debug += int(value)
			elif key == '--version':
				self.print_version()
				sys.exit(0)

		self.args = args

	def tell_the_story(self):

		self.get_options()
		self.get_heads(self.all_debug or self.debug % 2)
		self.get_history(self.all_debug or self.debug / 2 % 2)

		self.bind_children(self.all_debug or self.debug / 4 % 2)
		self.clear()
		self.row_unroll(self.all_debug or self.debug / 8 % 2)
		self.clear()
		self.column_unroll(self.all_debug or self.debug / 16 % 2)

		self.print_graph(self.all_debug or self.debug / 32 % 2)

		return
