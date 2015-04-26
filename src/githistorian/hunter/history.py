# Headhunter module for Git-Historian
# -*- encoding: utf-8 -*-

from __future__ import print_function
from subprocess import check_output
import re
import sys
import json

from ..node import Node, NodeDB

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

def hunt (opt, debug, heads, limit):
	return HistoryHunter(heads, opt, debug).hunt(limit)
