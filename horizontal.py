# Column module for Git-Historian

class Column:
	def __init__ (self, l):
		self.l = l
		self.index = -1
		self.available = 0
	
	def make_available (self):
		self.l = []
		self.index = -1
		self.available = 1

	def top (self):
		return self.l[0]
	
	def bottom (self):
		return self.l[-1]

	def append (self, bottom):
		self.l.append(bottom)

	def show (self):
		if len(self.l) == 0:
			print '[Avail]'
			return

		line = '[' + self.l[0][:7]
		for i in self.l[1:]:
			line += ', ' + i[:7]
		line += ']'
		print "%s" % line

class Order:
	def __init__ (self):
		self.l = []
		self.archived = []

	def trim_one_available (self, target):
		for i in xrange(target + 1, len(self.l)):
			if self.l[i].available:
				self.l.pop(i)
				break

	def insert (self, top, bottom):
		for i in self.l:
			if not i.available and i.bottom() == top:
				i.append(bottom)
				return
		#print "C.Insert (not found) (%s, %s)" % (top[:7], bottom[:7])
		for i in reversed(self.l):
			if not i.available and i.l[-2] == top:
				#self.show()
				index = self.l.index(i) + 1
				#print "C.Insert (father column index) (%d)" % index
				self.l.insert(index, Column([top, bottom]))
				self.trim_one_available(index)
				#self.show()
				return
		self.l.append(Column([top, bottom]))

	def archive (self, bottom, target):
		#print "C.Archive (%s, %s)" % (bottom[:7], target[:7])
		for index in reversed(xrange(len(self.l))):
			i = self.l[index]
			if not i.available and i.bottom() == bottom and target in i.l:
				#Archiving
				to_archive = Column(i.l[1:-1])
				to_archive.index = index
				self.archived.append(to_archive)
				self.l[index].make_available()
				
				#print "Archiving %s at index %d" % (target[:7], index)
				break

	def show (self):
		print '{'
		for i in self.l:
			i.show()
		print '}'

