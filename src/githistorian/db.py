# Database module for Git-Historian
# encoding: utf-8

from .node import Node

class NodeDB:

	def __init__ (self):
		self.store = {}

	def add_node (self, node):
		self.store[node.name] = node

	def at (self, name):
		return self.store[name]

	def clear (self):
		for node in self.store.values():
			node.done = 0

	def drop_missing_refs (self):

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
						self.add_node(fake)

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
