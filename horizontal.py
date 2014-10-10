# Column module for Git-Historian

class Cell:

	def __init__ (self, name):
		self.name = name
		self.left = self.top = self.bottom = ''
		self.upper = self.lower = ''

class Layout:

	def __init__ (self, debug, commit, first):
		self.debug = debug
		self.commit = commit
		self.first = first
		self.cell = {}

	def check (self, commit):
		if commit.hash in self.commit:
			if self.debug: print '%s already done, skipping' % commit.hash[:7]
			return 1
		return 0

	def bottom_insert (self, commit):
		if self.debug: print '  bottom insert %s' % commit.hash[:7]
		if self.check(commit): return
	
	def top_insert (self, commit):
		if self.debug: print '  top insert %s' % commit.hash[:7]
		if self.check(commit): return

		cell = Cell(commit)
		
		# Looking for non-static parents
		candidates = []
		for name in commit.parent:
			if not self.commit[name].static:
				candidates.append(name)
		
		if len(candidates) == 0:
			commit.column = self.first
			self.commit[commit.hash] = cell
			return
		
		print 'This case is not yet covered!!!'

		self.commit[commit.hash] = cell

	def brand_new_insert (self, commit):
		if self.debug: print '  brand new insert %s' % commit.hash[:7]
		if self.check(commit): return
	
class Order:

	def __init__ (self, debug):
		self.content = []
		self.debug = debug

	def show (self):
		for l in self.content:
			if len(l): message = l[0][:7]
			for e in l[1:]: message += ', %s' % e[:7]
			print '[%s]' % message
	
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
