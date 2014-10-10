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
		self.width = -1
	
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
	
	def insert (self, commit):
		
		if commit.static:
			#if self.debug:
			print '%s is static, skipping' % commit.hash[:7]
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
				return

			# Move sideways until there is an opening
			while child.lower:
				child = self.commit[child.lower]

			# Free cell after this one
			child.lower = commit.hash
			commit.left = name
			commit.column = child.column + 1
			if commit.column > self.width:
				self.width = commit.column
			return
		
		#if self.debug:
		print 'No valid child found for %s, defaulting' % commit.hash[:7]
		commit.column = 2

	def unroll_graph(self, debug):

		if debug:
			print '\n-- Vertical unrolling --'

		#visit = vertical.Order()
		visit = horizontal.Order(0)

		for name, commit in self.commit.items():

			if debug: visit.show()

			if commit.done:
				if debug: print '%s is done, skipping' % name[:7]
				continue

			if debug: print 'pushing %s' % name[:7]
			#visit.push(name)
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
				if commit.done:
					if debug: print "%s is done, skipping" % commit.hash[:7]
					continue

				# Horizontal order
				self.insert(commit)

				children = len(commit.child)

				if children > 1:
					print '  Now pushing %d children' % children
					visit.push_many(commit.child)
					continue
					#skip = 0
					#for i in reversed(commit.child):
					#	child = self.commit[i]
					#	if child and not child.done:
					#		visit.cpush(i)
					#		skip = 1
					#if skip: continue
				elif children > 0:
					child = self.commit[commit.child[0]]
					if child and not child.done:
						#visit.cpush(commit.child[0])
						print '  Now pushing single child'
						visit.push_one(commit.child[0])
						continue
				
				# Vertical order is now fixed
				self.vertical.append(commit.hash)

				commit.done = 1

				print
				self.print_graph(1)

				parents = len(commit.parent)

				if parents > 1:
					#for i in commit.parent:
					#	parent = self.commit[i]
					#	if parent and not parent.done:
					#		visit.ppush(i)
					print '  Now pushing %d parents' % parents
					visit.push_many(commit.parent)
				elif parents > 0:
					parent = self.commit[commit.parent[0]]
					if parent and not parent.done:
						#visit.push(commit.parent[0])
						print '  Now pushing single parent'
						visit.push_one(commit.parent[0])
				

		if debug:
			print '  --'
			for name in self.vertical:
				print '%s' % name[:7]
			print '  --'

	def print_graph (self, debug):
		
		#t = layout.Layout(self.width, self.commit, debug)
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
			#for i in message[1:-1]:
			for i in message[1:]:
				print '%s\x1b[m %s' % (t.draw_padding(), i)

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

		self.width = 4 # Reserved columns

		for i in self.commit:
			self.commit[i].know_your_parents(self.commit)
			self.commit[i].know_your_column()

		if self.debug:
			print "%d commits in history" % len(self.commit)
		self.unroll_graph(self.debug or vdebug)
		self.print_graph(self.debug or ldebug)

		print 'Width %d' % self.width
