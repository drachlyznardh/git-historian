# Main module for Git-Historian
# -*- encoding: utf-8 -*-

from subprocess import check_output
from subprocess import CalledProcessError
import re
import sys
import getopt

import node
import order

import vertical
import horizontal

import layout as layout

VERSION="0.0-a"

class Historian:
	def __init__ (self):

		self.verbose = 0
		self.debug = 0

		self.head = []
		self.head_by_name = {}
		self.commit = {}
		self.vertical = []
		self.horizonal = {}
		
		self.width = -1
	
		self.max_column = -1

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
		cmdlist = ['git', 'log', '--pretty="%H %P%d"']

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

			# Matching hashes and ref names
			hashes_n_refs = re.compile(r'''"(.*) \((.*)\)"''').match(line)

			# Match successulf, store values
			if hashes_n_refs:
				hashes = hashes_n_refs.group(1).split()
				refs = hashes_n_refs.group(2).split(',')

			# Match failed, no refs found, only hashes
			else:
				hashes = line[1:-1].split()
				refs = ""

			# New node to store info
			current = node.Node()

			if hashes:

				# Store self
				current.hash = hashes[0]

				# Store parents
				for i in hashes[1:]: current.parent.append(i)

			current.missing = len(current.parent)

			# Store refs, if any
			for i in refs: current.ref.append(i.strip())

			# Store node in map
			self.commit[current.hash] = current

		# Showing results
		if debug: print self.commit

	def select_column (self, commit):

		print
		if not commit.top:
			print '  %s is the topmost' % commit.hash[:7]
			return self.width

		if len(commit.child) == 0:
			print '  %s has no children' % commit.hash[:7]
			self.width += 1
			return self.width

		result = self.width
		name = commit.top
		print '  Processing %s' % commit.hash[:7]
		while name:

			target = self.commit[name]

			if name in commit.child and target.has_column():
				print '  %s is a child of %s (%d), halting' % (
					name[:7], commit.hash[:7],
					self.commit[name].column)

				booked = 1 + max([self.commit[j].column for j in target.parent])
				print booked
				return max(result, booked)

			print '  Matching %s against %s %d' % (
				commit.hash[:7], name[:7], target.column)
			result = max(result, target.column)
			name = target.top

		return self.width

	def jump_to_head (self, arg):

		result = []
		names = list(arg)

		while len(names):
			name = names.pop(0)
			commit = self.commit[name]
			if commit.done: continue
			if commit.mark: continue
			children = self.skip_if_done(commit.child)
			if len(children) == 0:
				commit.mark = 1
				result.append(name)
			else: names.extend(children)

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

				if current: commit.top = current
				current = name
				self.vertical.append(name)

				visit.push_parents(self.skip_if_done(commit.parent))

				commit.done = 1

	def column_unroll (self, debug):

		#self.horizon = {}
		self.width = 0

		visit = order.LeftmostFirst()
		visit.push(self.head[0])

		#previous = len(self.vertical)
		#current = -1

		while visit.has_more():

			name = visit.pop()
			commit = self.commit[name]

			if commit.done: continue

			visit.push(self.jump_to_head(commit.child))
			visit.push(self.skip_if_done(commit.parent))

			commit.column = self.select_column(commit)
			commit.done = 1

	def insert (self, commit):

		if commit.hdone: return

		if commit.static:
			#if self.debug:
			print '%s is static, skipping' % commit.hash[:7]
			commit.hdone = 1
			return

		for name in commit.child:
			child = self.commit[name]
			if child.static:
				#if self.debug:
				print 'child %s is static, skipping' % name[:7]
				continue
			
			# Free cell under this one
			if not child.bottom:
				child.bottom = commit.hash
				commit.top = name
				commit.column = child.column
				commit.hdone = 1
				return

			# Move sideways until there is an opening
			while child.lower:
				child.print_cell()
				child = self.commit[child.lower]

			child.print_cell()

			# Free cell after this one
			child.lower = commit.hash
			commit.left = name
			commit.column = child.column + 1
			commit.hdone = 1
			if commit.column > self.width:
				self.width = commit.column
			return
		
		#if self.debug:
		print 'No valid child found for %s, defaulting' % commit.hash[:7]
		commit.column = 2
		commit.hdone = 1

	def unroll_graph(self, debug):

		if debug:
			print '\n-- Vertical unrolling --'

		visit = horizontal.Order(0)

		for name in self.head:

			if debug: visit.show()

			commit = self.commit[name]
			if commit.done:
				if debug: print '%s is done, skipping' % name[:7]
				continue

			if debug: print 'pushing %s' % name[:7]
			visit.push_one(name)

			while 1:

				if debug: visit.show()

				target = visit.pop()
				if not target:
					if debug: print "No Target"
					break

				commit = self.commit[target]
				if not commit:
					if debug: print "No Commit"
					break

				if debug: print 'Unrolling %s' % target[:7]
				if commit.vdone:
					if debug: print "%s is vdone, skipping" % commit.hash[:7]
					continue

				# Horizontal order
				self.insert(commit)

				children = len(commit.child)

				if children > 1:
					print '  Now pushing %d children' % children
					visit.push_many(self.skip_if_vdone(commit.child))
					continue
				elif children > 0:
					child = self.commit[commit.child[0]]
					if child and not child.vdone:
						print '  Now pushing single child'
						visit.push_one(commit.child[0])
						continue
				
				# Vertical order is now fixed
				self.vertical.append(commit.hash)
				commit.vdone = 1

				#print
				#self.print_graph(1)

				parents = len(commit.parent)

				if parents > 1:
					print '  Now pushing %d parents' % parents
					visit.push_many(self.skip_if_vdone(commit.parent))
				elif parents > 0:
					parent = self.commit[commit.parent[0]]
					if parent and not parent.vdone:
						print '  Now pushing single parent'
						visit.push_one(commit.parent[0])
				

		if debug:
			print '  --'
			for name in self.vertical:
				print '%s' % name[:7]
			print '  --'

	def horizontal_unroll(self, debug):

		if debug:
			print '\n-- Horizontal unrolling --'

		for name in self.head:
			commit = self.commit[name]
			if commit: commit.child = []

		for name in self.vertical:
			commit = self.commit[name]
			if commit: commit.know_your_parents(self.commit)

		for name in self.vertical:
			commit = self.commit[name]
			if commit: commit.know_your_column()

		for name in self.vertical:
			
			if debug: order.show()
			commit = self.commit[name]
			if not commit:
				if debug:
					print "No Commit for name %s" % name[:7]
				break

			children = len(commit.child)
			parents = len(commit.parent)
			if debug:
				print "Vertical unrolling of %s (%d, %d)" % (
					name[:7], children, parents)

			# deal with self: it this static?
			if not commit.static:
				order.insert(commit)
				#if children == 1:
				#	order.insert_on_child_column(commit, commit.child[0])
				#else:
				#	order.insert_from_left(commit)

			continue
			# deal with children: it this a split?
			if children > 1:
				for child in commit.child:
					order.archive_commit(child)

			# deal with parents: it this a merge?
			continue
			if parents > 1:
				# selecting non-static parents
				candidates = []
				for name in commit.parent:
					parent = self.commit[name]
					if not parent.static: candidates.append(name)

				for name in candidates:
					parent = self.commit[name]
					order.insert_before_or_on_child_column(parent, commit.hash)
				#if len(candidates):
				#	first = self.commit[candidates[0]]
				#	order.insert_on_child_column(first, commit.hash)
				#for name in candidates[1:]:
				#	parent = self.commit[name]
				#	if not parent.static:
				#		order.insert_from_left(parent)

		order.flush_active()

		for index, column in order.archived.items():
			for name in column:
				if debug:
					print "Calling %s with %d from archive" % (
					name[:7], index)
				target = self.commit[name]
				if target and target.column == -1:
					target.column = reserved + index
		
		self.max_column = reserved + len(order.archived)

	def print_graph (self, debug):
		
		t = layout.Layout(self.width, self.commit, debug)

		cmdargs = 'git show -s --oneline --decorate --color'.split(' ')
		#cmdargs.append(optargs)
		cmdargs.append('<commit>')

		for name in self.vertical:

			commit = self.commit[name]
			if not commit:
				print "No Commit for name %s" % name[:7]
				break

			if debug: print "\nP %s" % name[:7]
			
			t.swap()

			t.bottom[commit.column] = ''
			for name in commit.parent:
				parent = self.commit[name]
				if not parent:
					print "No parent with name %s" % name[:7]
				t.bottom[parent.column] = name

			#if debug: t.plot_top()
			#if debug: t.plot_bottom()
			#if debug: t.plot_track()
			
			t.compute_layout(commit)

			cmdargs.pop() # Remove previous commit from list
			cmdargs.append(commit.hash)

			message = check_output(cmdargs).split('\n')

			print '%s\x1b[m %s' % (t.draw_transition(), message[0])
			for i in message[1:-1]:
			#for i in message[1:]:
				print '%s\x1b[m %s' % (t.draw_padding(), i)

	def print_version(self):
		print "Git-Historian %s (C) 2014 Ivan Simonini" % VERSION

	def print_help(self):
		print "Usage: %s " % sys.argv[0]

	def get_options(self):

		try:
			optlist, args = getopt.getopt(sys.argv[1:], 'hvd',
				['help', 'verbose', 'version',
				'debug', 'vdebug', 'hdebug', 'ldebug'])
		except getopt.GetoptError as err:
			print str(err)
			self.print_help()
			sys.exit(2)

		vdebug = 0
		hdebug = 0
		ldebug = 0

		for key, value in optlist:
			if key in ('-h', '--help'):
				self.print_help()
				return
			elif key in ('-v', '--verbose'):
				self.verbose = 1
			elif key in ('-d', '--debug'):
				self.debug = 1
			elif key == '--vdebug':
				vdebug = 1
			elif key == '--hdebug':
				hdebug = 1
			elif key == '--ldebug':
				ldebug = 1
			elif key == '--version':
				self.print_version()
				return

		self.args = args

	def tell_the_story(self):

		self.get_options()
		self.get_heads(0)
		self.get_history(0)

		self.bind_children(0)
		self.clear()
		self.row_unroll(0)
		self.clear()
		self.column_unroll(1)

		print '--'
		for i in self.vertical:
			print self.commit[i].to_oneline()

		return

		self.width = 3 # Reserved columns

		for i in self.commit:
			self.commit[i].know_your_parents(self.commit)
			self.commit[i].know_your_column()

		if self.debug:
			print "%d commits in history" % len(self.commit)
		self.unroll_graph(self.debug or vdebug)
		#self.print_graph(self.debug or ldebug)
		for name in self.vertical:
			print self.commit[name].to_oneline()

		print 'Width %d' % self.width
