# Headhunter module for Git-Historian
# -*- encoding: utf-8 -*-

from __future__ import print_function
from subprocess import check_output
import re
import sys
import json

from .node import Node, NodeDB

def _exact_match (one, two):
	return one == two

def _prefix_match (one, two):
	return one in two

class HeadHunter:

	def __init__ (self, o, debug):

		self.head = []
		self.ohead = []
		self.debug = debug

		self.order = o.order

		self.cname = []

		self.all_heads = o.heads
		self.all_tags = o.tags

		if o.match: self.match = _exact_match
		else: self.match = _prefix_match

	def hunt (self):

		if self.debug:
			print('  HeadHunter.Order (%s)' % ', '.join(self.order))

		self.load_heads()

		if self.debug:
			print('  HeadHunter.Head(%s)' % ', '.join([e[0][:7] for e in self.head]))

		self.order_heads()

		if self.debug:
			print('  HeadHunter.Head(%s)' % ', '.join([e[:7] for e in self.ohead]))

		return self.ohead

	def load_HEAD (self):

		cmdlist = 'git show-ref --heads --head'.split()

		output = check_output(cmdlist)

		exp = re.compile(r'^(.*) HEAD$')

		for line in output.split('\n'):

			if len(line) == 0: continue

			token = exp.match(line)
			if not token: continue

			self.ohead.append(token.group(1))
			return

	def load_heads (self):

		if len(self.order) == 0 and not self.all_heads:
			self.load_HEAD()
			return

		# Looking for heads, i.e. active branches
		cmdlist = ['git', 'show-ref']
		if self.all_tags: cmdlist.append('--tags')

		# Print the command line request
		if self.debug: print('  Now invoking %s' % cmdlist)

		# Invoke Git
		git_output = check_output(cmdlist)

		# Print the output
		if self.debug: print(git_output)

		# Parsing Git response
		for line in git_output.split('\n'):

			# Skipping empty lines (the last one should be empty)
			if len(line) == 0: continue

			# Matching name and name
			name_n_ref = re.compile(r'^(.*) refs\/.*\/(.*)$').match(line)

			# Broken ref: display message and skip line
			if not name_n_ref:
				print('No match for (%s)' % line)
				continue

			# Save result in order and by name
			self.head.append((name_n_ref.group(1), name_n_ref.group(2)))

	def order_heads (self):

		if self.all_heads:

			seen = set()
			f = seen.add
			self.ohead.extend([e[0] for e in self.head if not (e[0] in seen or f(e[0]))])

			return

		seen = set()

		for name in self.order:
			for e in self.head:
				if self.match(name, e[1]):
					self.head.remove(e)
					self.ohead.append(e[0])
					if e[0] not in seen:
						seen.add(e[0])
						self.ohead.append(e[0])

class HistoryHunter:

	def __init__ (self, target, options, debug = 0):

		self.target = target
		self.debug = debug

		# Parse options for format stuff…
		if options.pretty:
			self.pretty = r'''--pretty=%H %P#''' + options.pretty
		else:
			self.pretty = r'''--pretty=%H %P#%C(yellow)%h%C(auto)%d%Creset %s %C(bold red)%ar%Cblue %an'''

	def hunt (self, size_limit):

		nodes = NodeDB()

		# Looking for commit's and parents' names…
		cmdlist = ['git', 'log', '--pretty="%H %P"']
		cmdlist = ['git', 'log', self.pretty]

		# Optional limit to the size of the history
		if size_limit:
			cmdlist.append('-n%d' % size_limit)

		# … starting from know heads only
		cmdlist.extend(self.target)

		# Print the request
		if self.debug: print(cmdlist)

		# Invoking Git
		git_history_dump = check_output(cmdlist)

		# Print the output
		if self.debug: print(git_history_dump)

		# Ref for current node
		current = None

		# Parsing Git response
		for line in git_history_dump.split('\n'):

			# Skipping empty lines (the last one should be empty)
			if len(line) == 0: continue

			if '#' in line:

				# Store node in map if any, then create new one
				if current: nodes.add_node(current)
				current = Node()

				# Split line over the sharp character
				token = line.split('#', 1)

				# Store name, parents, message
				names = token[0].split()
				current.name = names[0]
				for i in names[1:]: current.parent.append(i)
				current.message = [token[1]]

			else:
				current.message.append(line)

		# Store the last node
		nodes.add_node(current)

		# Showing results
		if self.debug: print(nodes)
		return nodes

