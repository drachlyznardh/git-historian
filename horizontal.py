# Column module for Git-Historian

class Column:

	def __init__ (self, l):
		self.content = l
		self.index = -1
		self.available = 0
	
	def make_available (self):
		self.content = []
		self.index = -1
		self.available = 1

	def top (self):
		if len(self.content) == 0: return ''
		return self.content[0]
	
	def bottom (self):
		if len(self.content) == 0: return ''
		return self.content[-1]

	def last2bottom (self):
		if len(self.content) < 2: return ''
		return self.content[-2]

	def append (self, bottom):
		self.available = 0
		self.content.append(bottom)

	def show (self):
		if len(self.content) == 0:
			print '[Avail]'
			return

		line = '[' + self.content[0][:7]
		for i in self.content[1:]:
			line += ', ' + i[:7]
		line += ']'
		print "%s" % line

class Order:

	def __init__ (self, commit, reserved, debug):
		self.active = []
		self.commit = commit
		self.reserved = reserved
		self.debug = debug
		for i in range(reserved):
			self.active.append(Column([]))
		self.archived = []

	def trim_one_available (self, target):
		for i in xrange(target + 1, len(self.active)):
			if self.active[i].available:
				self.active.pop(i)
				break

	def insert_from_left (self, target):
		for column in self.active:
			if column.available:
				column.append(target)
				return
		self.active.append(Column([target]))

	def insert_on_child_column (self, target, child):
		for column in self.active:
			if column.bottom() == child:
				column.append(target)
				return
		print "Child %s in nowhere to be found!" % child

	def head_insert (self, target):
		self.active.append(Column([target.hash]))

	def insert_static (self, target):
		if self.active[target.column].bottom() == target.hash:
			if self.debug:
				print "%s is already at the bottom" % target.hash[:7]
			return
		self.active[target.column].append(target.hash)

	def self_insert (self, target):

		children = len(target.child)

		# A head just takes the first slot available
		if children == 0:
			for column in self.active:
				if column.available:
					column.append(target.hash)
					return
			self.active.append(Column([target.hash]))
			return

		# A lone father should fall in line with its child
		if children == 1:
			''

		for name in target.child:
			child = self.commit[name]
			if not child: continue # Missing commit: skip
			if child.static: continue # Child on static column, not eligible

	def insert (self, top, bottom):

		if bottom.static:
			self.insert_static(bottom)
			return

		if top.static and not bottom.static and top.parent[0] == bottom.hash:
			self.active[top.column].append(bottom.hash)
			if self.debug:
				print "  %s statically assigned to %d, thanks to %s" % (
				bottom.hash[:7], top.column, top.hash[:7])
			return

		for i in reversed(self.active):
			if i.available: continue
			if bottom.hash == i.bottom():
				if self.debug:
					print "%s is already at the bottom of %d" % (
					bottom.hash, self.active.index(i))
				return

		for i in self.active[self.reserved:]:
			if i.available:
				if len(top.parent) > 1:
					i.append(bottom.hash)
					return
			if top.hash == i.bottom():
				i.append(bottom.hash)
				return
		
		if self.debug:
			print "C.Insert (not found) (%s, %s)" % (
			top.hash[:7], bottom.hash[:7])

		for i in reversed(self.active):
			if i.available: continue
			if bottom.hash == i.bottom():
				if self.debug:
					print "%s was already inside" % bottom.hash[:7]
				return
			
		for i in reversed(self.active):
			if not i.available and i.last2bottom() == top.hash:
				index = self.active.index(i) + 1
				if self.debug:
					print "C.Insert (father column index) (%d)" % index
				self.active.insert(index, Column([top.hash, bottom.hash]))
				self.trim_one_available(index)
				return

		self.active.append(Column([top.hash, bottom.hash]))

	def archive (self, bottom, target):

		for l in reversed(self.active):
			if l.available: continue
			if l.bottom() == target:
				to_archive = Column(l.content)
				index = self.active.index(l)
				to_archive.index = index
				self.archived.append(to_archive)
				self.active[index].make_available()
				if self.debug:
					print "Archiving %s at index %d" % (target[:7], index)
				return

		if self.debug: print "Oops. %s not archived" % (target[:7])

	def show (self):
		print '{'
		for i in self.active:
			i.show()
		print '}'

