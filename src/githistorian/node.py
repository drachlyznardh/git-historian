# -*- encoding: utf-8 -*-

class Node:

	def __init__ (self):

		self.name = None
		self.parent = []
		self.child = []

		self.message = None
		self.done = 0

		self.column = -1
		self.border = -1
		self.row = -1

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
		return ' ' * 3 * self.column

	def to_oneline(self):
		data = (self.column, self.row, self.get_indent(), self.name[:7])
		return '(%2d, %2d)%s • \x1b[33m%s\x1b[m' % data

	def to_string(self):
		indent = ' ' * 2 * self.column
		str = "%s  Name {%s}" % (indent, self.name)
		for i in self.parent: str += "\n%sParent {%s}" % (indent, i)
		for i in self.child:  str += "\n%s Child {%s}" % (indent, i)
		return str

class NodeDB:

	def __init__ (self):
		self.store = {}
		self.fake = 0

	def stats (self):
		size = len(self.store)
		return size, size - self.fake, self.fake

	def add_node (self, node):
		self.store[node.name] = node

	def at (self, name):
		return self.store[name]

	def clear (self):
		for node in self.store.values():
			node.done = 0

	def drop_missing_refs (self):

		fakes = []
		for node in self.store.values():

			size = len(node.parent)

			if size == 0: continue

			elif size == 1:

				if node.parent[0] not in self.store:
					node.parent.pop(0)

			else:
				for name in node.parent:
					if name not in self.store:
						fake = Node()
						fake.name = name
						fake.message = ['[…]']
						fakes.append(fake)
						self.fake += 1

		for fake in fakes: self.add_node(fake)

	# Due to excessively restricting size limit, some heads may not appear at
	# all in the database. These heads are removed from the list
	def drop_missing_heads (self, heads):
		if not heads: return []
		available = []
		for name in heads:
			if name in self.store:
				available.append(name)
		return available

	def skip_if_done (self, names):
		result = []
		for name in names:
			if not self.store[name].done:
				result.append(name)
		return result

	def split_assigned_from_missing (self, names):
		assigned = []
		missing = []
		for name in names:
			if self.store[name].has_column():
				assigned.append(name)
			else: missing.append(name)
		return assigned, missing

	def select_highest (self, names, column, default):
		result = []
		for name in names:
			target = self.store[name]
			if target.has_column() and target.column <= column: continue
			result.append(target.row)
		if len(result) == 0: return default
		return min(result)

	def select_bounding_box (self, names, column):
		result = []
		for name in names:
			target = self.store[name]
			if target.has_column() and target.column < column: continue
			result.append(target.row)
		return result

	def select_starting_column (self, names):
		selection = []
		for name in names:
			target = self.store[name]
			if target.has_column():
				selection.append(target.column)
		return min(selection)

