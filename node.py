# Node module for Git-Historian
# -*- encoding: utf-8 -*-

class Node:

	def __init__ (self):

		self.name = None
		self.parent = []
		self.child = []

		self.column = -1
		self.border = -1
		self.row = -1

		self.done = 0
		self.top = None    # Previous commit by line
		self.bottom = None # Next commit by line
		self.left = None   # Previous commit by column
		self.right = None  # Next commit by line

	def add_child (self, name):

		if name not in self.child:
			self.child.append(name)

	def has_column (self):
		return self.column >= 0

	def set_column (self, value):
		self.column = value
		self.set_border(value)

	def set_border (self, value):
		self.border = max(self.border, value)

	def get_indent (self):
		if self.column > 0:
			return ('%%%ds' % (3 * self.column)) % (' ')
		return ''

	def to_oneline(self):
	
		return '(%2d, %2d)%s • \x1b[33m%s\x1b[m' % (
			self.column, self.row,
			self.get_indent(),
			self.name[:7])

	def to_string(self):
		if self.column > 0:
			indent = ('%%%ds' % (2 * self.column)) % (' ')
		else: indent = ''
		str = "%s  Name {%s}" % (indent, self.name)
		for i in self.parent: str += "\n%sParent {%s}" % (indent, i)
		for i in self.child:  str += "\n%s Child {%s}" % (indent, i)
		return str

