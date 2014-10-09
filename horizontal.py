# Column module for Git-Historian

class Node:

	def __init__ (self, commit):
		self.name = commit.hash
		self.count = len(commit.parent)

	def show (self):
		return '(%s %d)' % (self.name[:7], self.count)

class Column:

	def __init__ (self, commit):
		if commit: self.content = [Node(commit)]
		else: self.content = []
		#self.index = -1
		self.available = 0
	
	def make_available (self):
		self.content = []
		#self.index = -1
		self.available = 1
		#self.count = 0

	def top (self):
		if len(self.content) == 0: return None
		return self.content[0]
	
	def bottom (self):
		if len(self.content) == 0: return None
		return self.content[-1]

	def last2bottom (self):
		if len(self.content) < 2: return None
		return self.content[-2]

	def append (self, commit):
		self.available = 0
		self.content.append(Node(commit))
		#self.count = len(commit.parent)

	def show (self):
		if len(self.content) == 0:
			print '[Avail]'
			return

		line = '[%s' % (self.content[0].show())
		for i in self.content[1:]:
			line += ', ' + i.show()
		line += ']'
		print "%s" % line

class Order:

	def __init__ (self, commit, debug):
		self.active = []
		self.commit = commit
		self.debug = debug
		self.archived = {}

	def at_bottom(self, target):
		
		for column in self.active:
			if column.available: continue
			if column.bottom() == target:
				if self.debug: print "%s at the bottom" % target[:7]
				return 1
		return 0

	def trim_one_available (self, target):
		for i in xrange(target + 1, len(self.active)):
			if self.active[i].available:
				self.active.pop(i)
				break

	def insert_from_left (self, target):
		if self.at_bottom(target.hash): return
		if self.debug:
			print "Insert from left (%s)" % target.hash[:7]
		for column in self.active:
			if column.available:
				column.append(target)
				return
		self.active.append(Column(target))#Column([target.hash], len(target.parent)))

	def insert_on_child_column (self, target, child):
		if self.at_bottom(target.hash): return
		if self.debug:
			print "Insert %s on child column %s" % (target.hash[:7], child[:7])
		for column in self.active:
			bottom = column.bottom()
			if bottom and bottom.name == child:
				column.append(target)
				return
		print "Child %s in nowhere to be found!" % child
		self.insert_from_left(target)

	def insert_before_or_on_child_column(self, target, child):
	
		#if self.at_bottom(target): return
		if self.debug:
			print "Insert %s before or on child %s" % (target.hash[:7], child[:7])
		missing = 1
		for column in self.active:
			if column.available or column.bottom() == child:
				column.append(target)
				missing = 1
				break
		if missing:
			if self.debug:
				print "No child of %s found" % target.hash[:7]
			self.insert_from_left(target)
		return

		self.show()
		for column in self.active:
			if column.available: continue
			print "Now purgin closed branches (%s)" % column.bottom()
			if column.bottom() in children:
				index = self.active.index(column)
				self.archive_column(index, column)

	def insert_from_right_of(self, child, targets, static):
		
		if self.debug:
			print "Inserting from right of %s" % child[:7]
			print targets

		index = len(self.active)
		for column in self.active:
			if column.available: continue
			if column.bottom() == child:
				index = self.active.index(column)
				break

		# Child is static: its column cannot be inherited
		if static:
			for target in targets:
				if self.at_bottom(target): continue
				self.active.insert(index + 1, Column([target]))
				self.trim_one_available(index + 1)
			return

		free = 1
		for target in targets:
			if self.at_bottom(target): continue
			if free:
				self.active[index].append(targets[0])
				free = 0
				continue
			index += 1
			self.active.insert(index, Column([target]))
			self.trim_one_available(index)

	def self_insert (self, target):

		children = len(target.child)

		# A head just takes the first slot available
		if children == 0:
			for column in self.active:
				if column.available:
					column.append(target.hash)
					return
			self.active.append(Column([target.hash], len(target.parent)))
			return

		# A lone father should fall in line with its child
		if children == 1:
			''

		for name in target.child:
			child = self.commit[name]
			if not child: continue # Missing commit: skip
			if child.static: continue # Child on static column, not eligible

	def search_child (self, commit):
		
		for column in self.active:
			for child in commit.child:
				for element in column.content:
					if child == element.name:
						return [column, element]
		return [None, None]

	def push_column_up_to (self, column, node):
		
		cindex = self.active.index(column)
		eindex = column.content.index(node)

	def insert(self, commit):
		
		if self.debug: print 'Inserting %s' % commit.hash[:7]

		[column, element] = self.search_child(commit)
		if column and element:
			print 'Found column %d and element %s' % (
				self.active.index(column), element.name[:7])
			self.push_column_up_to(column, element)
			column.append(commit)
		else:
			print 'Not found'
			for column in self.active:
				if column.available:
					column.append(commit)
					return
			self.active.append(Column(commit))

	def ye_old_insert (self, top, bottom):

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

		for i in self.active:
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

	def archive_column (self, index, column):
		
		if self.debug:
			print "Archiving column (%d)" % index
		for e in column.content:
			try: self.archived[index].append(e.name)
			except: self.archived[index] = [e.name]
		
		column.make_available()

	def archive_commit (self, target):
	
		if self.debug:
			print "Archiving commit (%s)" % target[:7]
		for column in self.active:
			if column.available: continue
			bottom = column.bottom()
			if bottom and bottom.name == target:
			#if column.bottom() == target:
				if bottom.count == 1:
					index = self.active.index(column)
					self.archive_column(index, column)
				else:
					bottom.count -= 1

	# When every commit has been assigned to a column, it's time to archive any
	# current data
	def flush_active (self):
		
		for index in range(len(self.active)):
			for e in self.active[index].content:
				try: self.archived[index].append(e.name)
				except: self.archived[index] = [e.name]

	def show (self):
		print '{'
		for i in self.active:
			i.show()
		print '}'

