# Column module for Git-Historian

class Layout:

	def __init__ (self, debug, commit, first):
		self.debug = debug
		self.commit = commit
		self.first = first
		self.max_column = first

	def update(self, n):
		if n > self.max_column:
			self.max_column = n

	def bottom_insert (self, commit):
		if self.debug: print '  bottom insert %s' % commit.hash[:7]

		# Looking for non-static children
		for name in commit.child:
			
			child = self.commit[name]
			if child.static: continue
			
			# Free cell under this one
			if not child.bottom:
				child.bottom = commit.hash
				commit.top = name
				commit.column = child.column
				break

			# Move sideways until there is an opening
			while child.lower:
				child = self.commit[child.lower]

			# Free cell after this one
			child.lower = commit.hash
			commit.left = name
			commit.column = child.column + 1
			break

		commit.column = self.first

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
