# Order module for Git-Historian

class LeftmostFirst:

	def __init__ (self):

		self.content = []

	def push (self, l):

		for e in reversed(l):
			self.content.insert(0, e)

	def is_empty (self):

		return len(self.content) == 0

	def pop (self):

		try: return self.content.pop(0)
		except: return None
