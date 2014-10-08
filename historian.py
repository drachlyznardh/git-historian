# Main module for Git-Historian
# -*- encoding: utf-8 -*-

from subprocess import check_output
import re
import sys
import getopt

import node
import vertical
import horizontal

import layout as layout

VERSION="0.0-a"

class Historian:
	def __init__ (self):

		self.verbose = 0
		self.debug = 0

		self.head = 0
		self.commit = {}
		self.vertical = []
		self.max_column = -1
	
	def get_history(self):
		git_history_dump = check_output(["git", "log", '--pretty="%H %P%d"', "--all"])

		for line in git_history_dump.split('\n'):
			if len(line) == 0: continue

			hashes_n_refs = re.compile(r'''"(.*) \((.*)\)"''').match(line)
			if hashes_n_refs:
				hashes = hashes_n_refs.group(1).split()
				refs = hashes_n_refs.group(2).split(',')
			else:
				hashes = line[1:-1].split()
				refs = ""

			current = node.Node()
			if hashes:
				current.hash = hashes[0]
				for i in hashes[1:]: current.parent.append(i)
			for i in refs: current.ref.append(i.strip())

			if not self.head: self.head = current.hash
			self.commit[current.hash] = current
	
	def unroll_vertically(self, debug):

		if debug:
			print '\n-- Vertical unrolling --'

		visit = vertical.Order()

		for name, commit in self.commit.items():

			if debug: visit.show()

			if commit.done:
				if debug: print '%s is done, skipping' % name[:7]
				continue

			if debug: print 'pushing %s' % name[:7]
			visit.push(name)

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
				if commit.done:
					if debug: print "%s is done, skipping" % commit.hash[:7]
					continue

				if len(commit.child) > 1:
					skip = 0
					for i in reversed(commit.child):
						child = self.commit[i]
						if child and not child.done:
							visit.cpush(i)
							skip = 1
					if skip: continue
				elif len(commit.child) > 0:
					child = self.commit[commit.child[0]]
					if child and not child.done:
						visit.cpush(commit.child[0])
						continue
				
				self.vertical.append(commit.hash)

				if len(commit.parent) > 1:
					for i in commit.parent:
						parent = self.commit[i]
						if parent and not parent.done:
							visit.ppush(i)
				elif len(commit.parent) > 0:
					parent = self.commit[commit.parent[0]]
					if parent and not parent.done:
						visit.push(commit.parent[0])
				
				if debug: visit.show()
				commit.done = 1

		if debug:
			print '  --'
			for name in self.vertical:
				print '%s' % name[:7]
			print '  --'

	def unroll_horizontally(self, debug):

		if debug:
			print '\n-- Horizontal unrolling --'

		reserved = 2
		order = horizontal.Order(self.commit, reserved, debug)

		# Children must appear in their vertical order
		for name in self.vertical:
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

			if commit.static:
				order.insert_static(commit)
			elif children == 0:
				order.insert_from_left(name)
			elif children == 1:
				child = self.commit[commit.child[0]]
				if child.static:
					order.insert_from_left(name)
				else:
					order.insert_on_child_column(name, commit.child[0])
			else:
				#candidates = []
				for child in commit.child:
					#if not self.commit[child].static:
						#candidates.append(child)
					order.archive_commit(child)
				#for candidate in candidates:
				#	order.archive_commit(candidate)
				order.insert_from_left(name)

			if parents == 0:
				order.archive_commit(name)
			elif parents > 1:
				order.archive_commit(name)
				#candidates = []
				for parent in commit.parent:
					if not self.commit[parent].static:
						#candidates.append(parent)
						order.insert_from_left(parent)
				#order.insert_from_right_of(name, candidates, commit.static)

		order.flush_active()

		for index in range(len(order.active)):
			for name in order.active[index].content:
				if debug:
					print "Calling %s with %d from column" % (
					name[:7], index)
				target = self.commit[name]
				if target and target.column == -1:
					target.column = index

		#for i in reversed(range(len(order.archived))):
		for index, column in order.archived.items():
			#index = column.index
			for name in column:#.content:
				if debug:
					print "Calling %s with %d from archive" % (
					name[:7], index)
				target = self.commit[name]
				if target and target.column == -1:
					target.column = index
		
		self.max_column = len(order.active)

	def print_graph (self, debug):
		
		head = self.commit[self.head]
		if not head:
			print "Wut!"
			return

		t = layout.Layout(self.max_column, self.commit)

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

			if debug: t.plot_top()
			if debug: t.plot_bottom()
			
			#print "%s %s" % (t.draw_layout(commit), commit.to_oneline())
			print "%s" % t.draw_padding()
			t.compute_layout(commit)
			print "%s %s" % (t.draw_transition(), commit.to_oneline())

	def print_version(self):
		print "Git-Historian %s (C) 2014 Ivan Simonini" % VERSION

	def print_help(self):
		print "Usage: %s " % sys.argv[0]

	def tell_the_story(self):

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

		if not self.commit:
			self.get_history()

		for i in self.commit:
			self.commit[i].know_your_parents(self.commit)

		if self.debug:
			print "%d commits in history" % len(self.commit)
		self.unroll_vertically(self.debug or vdebug)
		self.unroll_horizontally(self.debug or hdebug)
		self.print_graph(self.debug or ldebug)

