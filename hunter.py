# Headhunter module for Git-Historian
# -*- encoding: utf-8 -*-

from subprocess import check_output
from subprocess import CalledProcessError
import re
import sys
import json

import node
import db

class HeadHunter:

	def __init__ (self, o, debug):

		self.head = []
		self.ohead = []
		self.debug = debug

		self.name = []
		self.cname = []

		self.all_heads = o.all_heads
		self.args = o.args

	def hunt (self):

		self.load_configfile('.git-historian')
		self.load_args()

		if self.debug:
			print '  HeadHunter.Name (%s)' % ', '.join(self.name)

		self.load_heads()

		if self.debug:
			print '  HeadHunter.Head(%s)' % ', '.join([e[0][:7] for e in self.head])

		self.order_heads()

		if self.debug:
			print '  HeadHunter.Head(%s)' % ', '.join([e[:7] for e in self.ohead])

		return self.ohead

	def load_configfile (self, target_file):

		try: f = open(target_file, 'r')
		except IOError as e: return

		self.cname = json.load(f)

	def load_args (self):

		if len(self.args) == 0:
			self.name.extend(self.cname)
			return

		self.name.extend(self.args)

	def load_HEAD (self):

		cmdlist = 'git show-ref --heads --head'.split()

		try: output = check_output(cmdlist)
		except CalledProcessError as error:
			print 'Command `%s` returned %d' % (' '.join(cmdlist), error.returncode)
			sys.exit(1)
			return

		exp = re.compile(r'''(.*) HEAD''')

		for line in output.split('\n'):

			if len(line) == 0: continue

			token = exp.match(line)
			if not token: continue

			self.ohead.append(token.group(1))

	def load_heads (self):

		if len(self.name) == 0 and not self.all_heads:
			self.load_HEAD()
			return

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

			# Matching name and name
			name_n_ref = re.compile(r'''(.*) refs\/.*\/(.*)''').match(line)

			# Broken ref: display message and skip line
			if not name_n_ref:
				print 'No match for (%s)' % line
				continue

			# Save result in order and by name
			self.head.append((name_n_ref.group(1), name_n_ref.group(2)))

	def order_heads (self):

		for name in self.name:
			for e in self.head:
				if name in e[1]:
					self.head.remove(e)
					self.ohead.append(e[0])

		if not self.all_heads: return

		self.ohead.extend([e[0] for e in self.head])

class HistoryHunter:

	def __init__ (self, target, debug = 0):

		self.target = target
		self.debug = debug

	def hunt (self):

		nodes = db.NodeDB()

		# Looking for commit's and parents' names…
		cmdlist = ['git', 'log', '--pretty="%H %P"']

		# … starting from know heads only
		cmdlist.extend(self.target)

		# Print the request
		if self.debug: print cmdlist

		# Invoking Git
		git_history_dump = check_output(cmdlist)

		# Print the output
		if self.debug: print git_history_dump

		# Parsing Git response
		for line in git_history_dump.split('\n'):

			# Skipping empty lines (the last one should be empty)
			if len(line) == 0: continue

			# New node to store info
			current = node.Node(1)

			names = line[1:-1].split()

			# Store self
			current.name = names[0]

			# Store parents
			for i in names[1:]: current.parent.append(i)

			# Store node in map
			nodes.add_node(current)

		# Showing results
		if self.debug: print nodes
		return nodes

class MessageHunter:

	def __init__ (self):

		self.cmdargs = 'git show -s --oneline --decorate --color'.split(' ')

	def describe (self, name):

		self.cmdargs.append(name)
		message = check_output(self.cmdargs).split('\n')
		self.cmdargs.pop()
		return message
