
# Base class for all visits. Manages the visit of a graph, tracking nodes we
# need to visit (in a certain order) and those we are already aware of
class BaseVisit:

	# Inititialise visit with items, all of which are immediately seen
	def __init__(self, items, db, logger):
		self.items = items
		self.db = db
		self.seen = set(items)
		self.logger = logger

	def __bool__(self):        return len(self.items) > 0   # Visit is truthy until there are items to visit
	def pop(self):             return self.items.pop(0)     # Pop the first item in the list
	def isUnseen(self, item):  return item not in self.seen # True if items was not yet seen
	def getItems(self):        return self.items            # Get current item list
	def setItems(self, items): self.items = items           # Set current item list

	# Pushing items according to policy
	def push(self, items):
		if not items: return # Skip empty lists
		self.logger.log('{} has seen {}', self.__class__.__name__, ['{}'.format(e) for e in self.seen])
		self.logger.log('{} about to push {}', self.__class__.__name__, ['{}'.format(e) for e in items])
		pushed = self._push(items) # Actually pushing items
		self.logger.log('{} actually pushing {}', self.__class__.__name__, ['{}'.format(e) for e in pushed])
		for e in pushed: self.seen.add(e) # So they won't be added again

# Items are prepended in order
class DirectPreVisit(BaseVisit):
	def _push(self, items):
		filtered = [e for e in items if self.isUnseen(e)]
		self.setItems(filtered + self.getItems())
		return filtered

# Items are prepended in reverse order
class ReversePreVisit(BaseVisit):
	def _push(self, items):
		filtered = [e for e in reversed(items) if self.isUnseen(e)]
		self.setItems(filtered + self.getItems())
		return filtered

# Items are appended in order
class DirectPostVisit(BaseVisit):
	def _push(self, items):
		filtered = [e for e in items if self.isUnseen(e)]
		self.setItems(self.getItems() + filtered)
		return filtered

# Items are appended in reverse order
class ReversePostVisit(BaseVisit):
	def _push(self, items):
		filtered = [e for e in reversed(items) if self.isUnseen(e)]
		self.setItems(self.getItems() + filtered)
		return filtered

class ChildrenAwareVisit(BaseVisit):
	def _check(self, e):
		self.logger.log('Checking {} children', e)
		for c in e.children:
			if self.isUnseen(self.db[c]):
				self.logger.log('{} is unseen, blocking', c)
				return False
		self.logger.log('All children have been seen')
		return self.isUnseen(e)

	def _push(self, items):
		filtered = [e for e in reversed(items) if self._check(e)]
		self.setItems(filtered + self.getItems())
		return filtered

# Return visit class by name, or ReverseVisit by default
def getVisit(name):
	return {
			'direct-pre'     : DirectPreVisit,
			'reverse-pre'    : ReversePreVisit,
			'direct-post'    : DirectPostVisit,
			'reverse-post'   : ReversePostVisit,
			'children-aware' : ChildrenAwareVisit,
		}.get(name.lower(), ReversePreVisit)

