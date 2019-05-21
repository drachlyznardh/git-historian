
# Base class for all visits. Manages the visit of a graph, tracking nodes we
# need to visit (in a certain order) and those we are already aware of
class BaseVisit:

	# Inititialise visit with items, all of which are immediately seen
	def __init__(self, items):
		self.items = items
		self.seen = set(items)

	def __bool__(self):        return len(self.items) > 0   # Visit is truthy until there are items to visit
	def pop(self):             return self.items.pop(0)     # Pop the first item in the list
	def isUnseen(self, item):  return item not in self.seen # True if items was not yet seen
	def getItems(self):        return self.items            # Get current item list
	def setItems(self, items): self.items = items           # Set current item list

	# Pushing items according to policy
	def push(self, items):
		if not items: return # Skip empty lists
		pushed = self._push(items) # Actually pushing items
		for e in pushed: self.seen.add(e) # So they won't be added again

# Items are prepended in order
class DirectVisit(BaseVisit):
	def _push(self, items):
		filtered = [e for e in items if self.isUnseen(e)]
		self.setItems(filtered + self.getItems())
		return filtered

# Items are prepended in reverse order
class ReverseVisit(BaseVisit):
	def _push(self, items):
		filtered = [e for e in reversed(items) if self.isUnseen(e)]
		self.setItems(filtered + self.getItems())
		return filtered

# Return visit class by name, or ReverseVisit by default
def getVisit(name):
	return {
			'Direct': DirectVisit,
			'Reverse': ReverseVisit,
		}.get(name, ReverseVisit)

