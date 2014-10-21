# Headhunter module for Git-Historian
# -*- encoding: utf-8 -*-

from subprocess import check_output
from subprocess import CalledProcessError
import re
import sys
import json

import node

class HeadHunter:

	def __init__ (self, debug):

		self.head = []
		self.ohead = []
		self.debug = debug

		self.name = []
		self.cname = []

		self.cmdargs = 'git show -s --oneline --decorate --color'.split(' ')

	def hunt (self, all_heads, args):

		self.load_configfile('.git-historian')
		self.load_args(args)

		if self.debug:
			print '  HeadHunter.Name (%s)' % ', '.join(self.name)

		self.load_heads()

		if self.debug:
			print '  HeadHunter.Head(%s)' % ', '.join([e[0][:7] for e in self.head])

		self.order_heads(all_heads)

		if self.debug:
			print '  HeadHunter.Head(%s)' % ', '.join([e[:7] for e in self.ohead])

		return self.ohead

	def load_configfile (self, target_file):

		try: f = open(target_file, 'r')
		except IOError as e: return

		self.cname = json.load(f)

	def load_args (self, args):

		if len(args) == 0:
			self.name.extend(self.cname)
			return

		self.name.extend(args)

	def load_heads (self):

		# Looking for heads, i.e. active branches
		cmdlist = ['git', 'show-ref', '--heads']

		# Print the command line request
		if self.debug: print '  Now invoking %s' % cmdlist

		# Invoke Git
		try: git_output = check_output(cmdlist)
		except CalledProcessError as error:
			print 'Command `%s` returned %d' % (' '.join(cmdlist), error.returncode)
			sys.exit(1)
			return

		# Print the output
		if self.debug: print git_output

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
			self.head.append((hash_n_ref.group(1), hash_n_ref.group(2)))

	def order_heads (self, all_heads):

		for name in self.name:
			for e in self.head:
				if name in e[1]:
					self.head.remove(e)
					self.ohead.append(e[0])

		if not all_heads: return

		self.ohead.extend([e[0] for e in self.head])

	def get_history(self, debug):

		nodes = {}

		# Looking for commit's and parents' hashes…
		cmdlist = ['git', 'log', '--pretty="%H %P"']

		# … starting from know heads only
		cmdlist.extend(self.ohead)

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
			current = node.Node(1)

			hashes = line[1:-1].split()

			# Store self
			current.hash = hashes[0]

			# Store parents
			for i in hashes[1:]: current.parent.append(i)

			# Store node in map
			nodes[current.hash] = current

		# Showing results
		if debug: print nodes
		return nodes

	def describe (self, name):

		self.cmdargs.append(name)
		message = check_output(self.cmdargs).split('\n')
		self.cmdargs.pop()
		return message
