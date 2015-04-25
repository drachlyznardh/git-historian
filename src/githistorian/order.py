# Order module for Git-Historian

class ColumnOrder:

	def __init__ (self):
		self.content = []

	def has_more (self):
		return len(self.content)

	def push (self, arg):

		if isinstance(arg, basestring):
			self.content.append(arg)
			return

		if not isinstance(arg, list):
			print 'WTF is %s?' % arg
			return

		if len(arg) == 0: return

		self.content.extend(arg)

	def pop (self):
		try: return self.content.pop(0)
		except: return None

	def show (self):
		return '    [%s]' % ', '.join([e[:7] for e in self.content])

class LeftmostFirst:

	def __init__ (self):

		self.content = []

	def push (self, arg):

		if isinstance(arg, basestring):
			self.content.insert(0, arg)
			return

		if not isinstance(arg, list):
			print 'WTF is %s?' % arg
			return

		if len(arg) == 0: return

		for e in reversed(arg):
			self.content.insert(0, e)

	def is_empty (self):

		return len(self.content) == 0

	def has_more (self):

		return len(self.content)

	def pop (self):

		try: return self.content.pop(0)
		except: return None

