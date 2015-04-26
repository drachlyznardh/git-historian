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

class Hunter:

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

		need_order = len(self.order)

		if self.debug:
			print('  HeadHunter.Order (%s)' % ', '.join(self.order))

		if need_order or self.all_heads:
			self.load_heads()
			if self.all_heads: self.ohead = _get_all_heads(self.head)
			else: self.ohead = _get_selected_heads(self.match, self.head, self.order)
		else: self.load_HEAD()

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

