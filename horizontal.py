# Column module for Git-Historian

class Cell:

	def __init__ (self, name):
		self.name = name
		self.left = self.top = self.bottom = ''
		self.upper = self.lower = ''

class Layout:

	def __init__ (self, debug):
		self.debug = debug
		self.commit = {}
		self.head = []

	def bottom_insert (self, commit):
		if self.debug: print '  bottom insert %s' % commit.hash[:7]
	
	def top_insert (self, commit):
		if self.debug: print '  top insert %s' % commit.hash[:7]
	
	def brand_new_insert (self, commit):
		if self.debug: print '  brand new insert %s' % commit.hash[:7]
	
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
