# Column module for Git-Historian

class Cell:

	def __init__ (self, name):
		self.name = name
		self.left = self.top = self.bottom = None
		self.upper = self.lower = None

class Layout:

	def __init__ (self, debug, commit, first):
		self.debug = debug
		self.commit = commit
		self.first = first
		self.cell = {}
		self.max_column = first

	def update(self, n):
		if n > self.max_column:
			self.max_column = n

	def check (self, commit):
		if commit.hash in self.cell:
			if self.debug: print '%s already done, skipping' % commit.hash[:7]
			return 1
		return 0

	def bottom_insert (self, commit):
		if self.debug: print '  bottom insert %s' % commit.hash[:7]
		if self.check(commit): return

		cell = Cell(commit)

		# Looking for non-static children
		candidates = []
		for name in commit.child:
			if self.commit[name].static: continue
			
			ccell = self.cell[name]
				
			# Free cell under this one
			if not ccell.bottom:
				ccell.bottom = commit.hash
				cell.top = ccell.name
				commit.column = self.commit[ccell.name]
				break

			# Move sideways until there is an opening
			while ccell.lower:
				ccell = self.cell[ccell.lower]

			# Free cell after this one
			ccell.lower = commit.hash
			cell.left = ccell.name
			commit.column = self.commit[ccell.name] + 1
			break

		commit.column = self.first

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
