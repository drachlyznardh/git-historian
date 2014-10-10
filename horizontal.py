# Column module for Git-Historian

class Column:

	def __init__ (self, l, count):
		self.content = l
		self.index = -1
		self.available = 0
		self.count = count
	
	def make_available (self):
		self.content = []
		self.index = -1
		self.available = 1
		self.count = 0

	def top (self):
		if len(self.content) == 0: return ''
		return self.content[0]
	
	def bottom (self):
		if len(self.content) == 0: return ''
		return self.content[-1]

	def last2bottom (self):
		if len(self.content) < 2: return ''
		return self.content[-2]

	def append (self, commit):
		self.available = 0
		self.content.append(commit.hash)
		self.count = len(commit.parent)

	def show (self):
		if len(self.content) == 0:
			print '%d [Avail]' % self.count
			return

		line = '%d [%s' % (self.count, self.content[0][:7])
		for i in self.content[1:]:
			line += ', ' + i[:7]
		line += ']'
		print "%s" % line

class Order:

	def __init__ (self, debug):
		self.content = []
		#self.commit = commit
		self.debug = debug

	def show (self):
		for e in self.content:
			print '%s' % e
	
	def push_one (self, one):
		self.content.insert(0, [one])
	
	def push_many (self, many):
		self.content.insert(0, many)
	
	def pop (self):
		try:
			while len(self.content[0]) == 0:
				self.content.pop(0)
			target = self.content[0].pop(0)
			if len(self.content[0]) == 0:
				self.content.pop(0)
			return target
		except:
			return None
