# Database module for Git-Historian

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

