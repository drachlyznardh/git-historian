# encoding: utf-8

from __future__ import print_function
from subprocess import check_output
import re

def _exact_match (one, two):
	return one == two

def _prefix_match (one, two):
	return one in two

def _get_all_heads (heads):
	seen = set()
	f = seen.add
	return [e[0] for e in heads if not (e[0] in seen or f(e[0]))]

def _get_selected_heads (f, heads, order):

	seen = set()
	g = seen.add
	result = []

	for name in order:
		for e in heads:
			if f(name, e[1]):
				heads.remove(e)
				result.append(e[0])

	return [e for e in result if not (e in seen or g(e))]

def _load_HEAD ():

	cmdlist = 'git show-ref --heads --head'.split()

	output = check_output(cmdlist)

	exp = re.compile(r'^(.*) HEAD$')

	for line in output.split('\n'):

		if len(line) == 0: continue

		token = exp.match(line)
		if not token: continue

		return [token.group(1)]

def _load_heads (opt, debug):

	collected = []

	# Looking for heads, i.e. active branches
	cmdlist = ['git', 'show-ref']
	if not opt.remotes: cmdlist.append('--heads')
	if opt.tags: cmdlist.append('--tags')

	# Print the command line request
	if debug: print('  Now invoking %s' % cmdlist)

	# Invoke Git
	git_output = check_output(cmdlist)

	# Print the output
	if debug: print(git_output)

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
		collected.append((name_n_ref.group(1), name_n_ref.group(2)))

	return collected

def hunt (opt, debug):

	need_order = len(opt.order)
	if opt.match: match = _exact_match
	else: match = _prefix_match

	if debug:
		print('  HeadHunter.Order (%s)' % ', '.join(order))

	if need_order or opt.heads:
		collected = _load_heads(opt, debug)
		if opt.heads: selected = _get_all_heads(collected)
		else: selected = _get_selected_heads(match, collected, opt.order)
	else: selected = _load_HEAD()

	if debug:
		print('  HeadHunter.Head(%s)' % ', '.join([e[:7] for e in selected]))

	return selected

