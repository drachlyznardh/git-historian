# encoding: utf-8

from __future__ import print_function
from subprocess import check_output, STDOUT
import re

def _exact_match (one, two):
	return one == two

def _prefix_match (one, two):
	return one in two

def _get_all_heads (heads):
	seen = set()
	f = seen.add
	return [e[0] for e in heads if not (e[0] in seen or f(e[0]))]

def _get_selected_heads (f, heads, order, all_heads):

	seen = set()
	g = seen.add
	result = []

	for name in order:
		for e in heads:
			if f(name, e[1]):
				# heads.remove(e)
				result.append(e[0])

	if all_heads:
		for e in heads:
			result.append(e[0])

	return [e for e in result if not (e in seen or g(e))]

def _load_HEAD (outputTuple):

	cmdlist = 'git show-ref --heads --head'.split()

	try: output = check_output(cmdlist, stderr=STDOUT, encoding='utf-8')
	except:
		print('No HEAD')
		return False

	exp = re.compile(r'^(.*) HEAD$')

	for line in output.split('\n'):

		if len(line) == 0: continue

		token = exp.match(line)
		if not token: continue

		if outputTuple: return [(token.group(1), 'HEAD')]
		return [token.group(1)]

	# HEAD may not exist
	return False

def _load_heads (opt):

	# Looking for heads, i.e. active branches
	cmdlist = ['git', 'show-ref']
	if not opt.remotes: cmdlist.append('--heads')
	if opt.tags: cmdlist.append('--tags')

	# Invoke Git
	try: git_output = check_output(cmdlist, stderr=STDOUT, encoding='utf-8')
	except:
		print('No HEADs')
		return []

	collected = []
	exp = re.compile(r'^(.*) refs\/.*\/(.*)$')

	# Parsing Git response
	for line in git_output.split('\n'):

		# Skipping empty lines (the last one should be empty)
		if len(line) == 0: continue

		# Matching name and name
		name_n_ref = exp.match(line)

		# Broken ref: display message and skip line
		if not name_n_ref:
			print('No match for (%s)' % line)
			continue

		# Save result in order and by name
		collected.append((name_n_ref.group(1), name_n_ref.group(2)))

	return collected

def hunt (opt):

	if len(opt.targets) == 0 and not opt.heads: return _load_HEAD(False)

	wanted = []
	for e in opt.order:
		if e in opt.targets:
			wanted.append(e)
	for e in opt.targets:
		if e not in wanted:
			wanted.append(e)

	collected = [x for x in _load_heads(opt) + _load_HEAD(True) if x]
	return _get_selected_heads(_exact_match if opt.match else _prefix_match, collected, wanted, opt.heads)

