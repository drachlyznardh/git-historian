# -*- encoding: utf-8 -*-

from __future__ import print_function
from subprocess import check_output
import re
import sys
import json

from ..node import Node, NodeDB

def _select_pretty (value):
	if value: return r'--pretty=%H %P#' + value
	return r'--pretty=%H %P#%C(yellow)%h%C(auto)%d%Creset %s %C(bold red)%ar%Cblue %an'

def _get_history_dump (opt, debug, heads, limit):

	# Looking for commit's and parents' names…
	cmdlist = ['git', 'log', _select_pretty(opt.pretty)]

	# Optional limit to the size of the history
	if limit: cmdlist.append('-n%d' % limit)

	# … starting from know heads only
	cmdlist.extend(heads)

	# Print the request
	if debug: print(cmdlist)

	# Invoking Git
	return check_output(cmdlist)

def hunt (opt, debug, heads, limit):

	history = NodeDB()
	git_history_dump = _get_history_dump(opt, debug, heads, limit)

	# Print the output
	if debug: print(git_history_dump)

	# Ref for current node
	current = None

	# Parsing Git response
	for line in git_history_dump.split('\n'):

		# Skipping empty lines (the last one should be empty)
		if len(line) == 0: continue

		if '#' in line:

			# Store node in map if any, then create new one
			if current: history.add_node(current)
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
	history.add_node(current)

	# Showing results
	if debug: print(history)
	return history

	return HistoryHunter(heads, opt, debug).hunt(limit)
