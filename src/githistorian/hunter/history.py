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

# Invokes git-log with optional size limit to collect commits, their relation
# with others and the custom messages
def _get_history_dump (opt, heads, limit):

	cmdlist = ['git', 'log', _select_pretty(opt.pretty)]
	if limit: cmdlist.append('-n%d' % limit)
	cmdlist.extend(heads)

	return check_output(cmdlist)

def hunt (opt, heads, limit):

	history = NodeDB()
	current = None

	for line in _get_history_dump(opt, heads, limit).split('\n'):

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
	return history

