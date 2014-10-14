# Order module for Git-Historian

class LeftmostFirst:

	def __init__ (self):

		self.content = []

	def push (self, arg):

		if isinstance(arg, basestring):
			self.content.insert(0, arg)
			return

		if not isinstance(arg, list):
			print 'WTF is %s?' % arg

		if len(arg) == 0: return

		for e in reversed(arg):
			self.content.insert(0, e)

	def is_empty (self):

		return len(self.content) == 0

	def pop (self):

		try: return self.content.pop(0)
		except: return None
