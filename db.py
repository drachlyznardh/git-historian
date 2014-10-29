# Database module for Git-Historian

class NodeDB:

	def __init__ (self):
		self.store = {}

	def add_node (self, node):
		self.store[node.name] = node

