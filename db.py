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
			if target.has_column() and target.column <= column: continue
			result.append(target.row)
		return result
