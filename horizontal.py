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
		if len(self.l) == 0: return ''
		return self.l[0]
	
	def bottom (self):
		if len(self.l) == 0: return ''
		return self.l[-1]

	def last2bottom (self):
		if len(self.l) < 2: return ''
		return self.l[-2]

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

	def __init__ (self, reserved, debug):
		self.l = []
		self.debug = debug
		for i in range(reserved):
			self.l.append(Column([]))
		self.archived = []

	def trim_one_available (self, target):
		for i in xrange(target + 1, len(self.l)):
			if self.l[i].available:
				self.l.pop(i)
				break

	def head_insert (self, target):
		self.l.append(Column([target.hash]))

	def static_insert (self, target):
		if self.l[target.column].bottom() == target.hash:
			if self.debug:
				print "%s is already at the bottom" % target.hash[:7]
			return
		self.l[target.column].append(target.hash)

	def insert (self, top, bottom):

		if bottom.static:
			self.static_insert(bottom)
			return

		if top.static and not bottom.static and top.parent[0] == bottom.hash:
			self.l[top.column].append(bottom.hash)
			if self.debug:
				print "  %s statically assigned to %d, thanks to %s" % (
				bottom.hash[:7], top.column, top.hash[:7])
			return

		for i in reversed(self.l):
			if i.available: continue
			if bottom.hash == i.bottom():
				if self.debug:
					print "%s is already at the bottom of %d" % (
					bottom.hash, self.l.index(i))
				return

		for i in self.l:
			if i.available: continue
			if top.hash == i.bottom():
				i.append(bottom.hash)
				return
		
		if self.debug:
			print "C.Insert (not found) (%s, %s)" % (
			top.hash[:7], bottom.hash[:7])

		for i in reversed(self.l):
			if i.available: continue
			if bottom.hash == i.bottom():
				if self.debug:
					print "%s was already inside" % bottom.hash[:7]
				return
			
		for i in reversed(self.l):
			if not i.available and i.last2bottom() == top.hash:
				index = self.l.index(i) + 1
				if self.debug:
					print "C.Insert (father column index) (%d)" % index
				self.l.insert(index, Column([top.hash, bottom.hash]))
				self.trim_one_available(index)
				return

		self.l.append(Column([top.hash, bottom.hash]))

	def archive (self, bottom, target):

		#print "C.Archive (%s, %s)" % (bottom[:7], target[:7])
		for l in reversed(self.l):
			if l.available: continue
			if l.bottom() == target:
				to_archive = Column(l.l)
				index = self.l.index(l)
				to_archive.index = index
				self.archived.append(to_archive)
				self.l[index].make_available()
				if self.debug:
					print "Archiving %s at index %d" % (target[:7], index)
				return

		if self.debug: print "Oops. %s not archived" % (target[:7])

	def show (self):
		print '{'
		for i in self.l:
			i.show()
		print '}'

	def show_wave_front (self):
		message = '<'
		for i in self.l:
			if len(i.l): message += ' %s' % (i.l[-1][:7])
			else: message += ' XXXXXXX'
		message += ' >'
		print message

