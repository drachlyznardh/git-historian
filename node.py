# Node module for Git-Historian

import re

class Node:
	def __init__ (self):
		self.hash = ""
		self.parent = []
		self.child = []
		self.ref = []
		self.column = -1
		self.static = 0
		self.printed = 0
		self.nth_child = 0

		# Visit marks
		self.done = 0
		self.mark = 0
		self.missing = 0
		self.vdone = 0
		self.hdone = 0

		# Layout relation
		self.left = None   # Cell on left
		self.top = None    # Cell on top
		self.upper = None  # Cell on top-right
		self.bottom = None # Cell on bottom
		self.lower = None  # Cell on bottom-right

	def add_child (self, name):

		self.child.append(name)

	def has_column (self):
		return self.column >= 0

	def print_cell (self):
		
		message = '       '
		
		if self.top: message += ' %s' % self.top[:7]
		else: message += ' XXXXXXX'
		if self.upper: message += ' %s' % self.upper[:7]
		else: message += ' XXXXXXX'
		
		message += '\n'
		
		if self.left: message += ' %s' % self.left[:7]
		else: message += ' XXXXXXX'
		if self.hash: message += ' %s' % self.hash[:7]
		else: message += ' XXXXXXX'
		
		message += '\n        '
		
		if self.bottom: message += ' %s' % self.bottom[:7]
		else: message += ' XXXXXXX'
		if self.lower: message += ' %s' % self.lower[:7]
		else: message += ' XXXXXXX'

		print '(%s)' % message

	def print_graph(self, commit_map):
		if self.printed: return
		self.printed = 1

		for i in self.child:
			commit_map[i].print_graph(commit_map)
		print("%s" % self.to_oneline())
		for i in reversed(self.parent):
			commit_map[i].print_graph(commit_map)

	def to_oneline(self):
	
		line = ''
		if len(self.ref):
			line += ' \x1b[32;1m(' + self.ref[0]
			for i in self.ref[1:]:
				line += ', ' + i
			line += ')'
		
		return '(%d) \x1b[m%s%s\x1b[m (%d) (%d)' % (self.column,
			self.hash[:7],
			line, self.column, self.missing)

	def to_string(self):
		if self.column > 0:
			indent = ('%%%ds' % (2 * self.column)) % (' ')
		else: indent = ''
		str = "%s  Hash {%s}" % (indent, self.hash)
		for i in self.parent: str += "\n%sParent {%s}" % (indent, i)
		for i in self.child:  str += "\n%s Child {%s}" % (indent, i)
		for i in self.ref:    str += "\n%s   Ref {%s}" % (indent, i)
		return str

	def know_your_children(self, child, i):
		if child not in self.child:
			self.child.append(child)
			self.nth_child += i

	def know_your_parents(self, commit_map):
		for i in range(len(self.parent)):
			name = self.parent[i]
			parent = commit_map[name]
			if parent:
				parent.know_your_children(self.hash, i)

	def know_your_column (self):
		if len(self.ref):
			for i in self.ref:
				if re.match(r'''^tag: r[0-9]+''', i):
					self.static = 1
					self.column = 1
					break
				if 'release-' in i:
					self.static = 1
					self.column = 1
					break
				if re.match(r'''^tag: h[0-9]+''', i):
					self.static = 1
					self.column = 0
					break
				if 'hotfix-' in i:
					self.static = 1
					self.column = 0
					break
		return self.static

