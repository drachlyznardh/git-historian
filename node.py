# Node module for Git-Historian
# -*- encoding: utf-8 -*-

class Node:

	def __init__ (self, real):

		self.hash = None
		self.parent = []
		self.child = []

		self.column = -1
		self.row = -1

		self.real = real

		self.done = 0
		self.top = None    # Previous commit
		self.bottom = None # Next commit

	def add_child (self, name):

		if name not in self.child:
			self.child.append(name)

	def has_column (self):
		return self.column >= 0

	def is_real (self):
		return self.real

	def is_virtual (self):
		return not self.real

	def get_indent (self):
		if self.column > 0:
			return ('%%%ds' % (3 * self.column)) % (' ')
		return ''

	def to_oneline(self):
	
		return '(%2d, %2d)%s • \x1b[33m%s\x1b[m' % (
			self.column, self.row,
			self.get_indent(),
			self.hash[:7])

	def to_string(self):
		if self.column > 0:
			indent = ('%%%ds' % (2 * self.column)) % (' ')
		else: indent = ''
		str = "%s  Hash {%s}" % (indent, self.hash)
		for i in self.parent: str += "\n%sParent {%s}" % (indent, i)
		for i in self.child:  str += "\n%s Child {%s}" % (indent, i)
		return str

