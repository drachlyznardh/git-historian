# Layout module for Git-Historian
# -*- encoding: utf-8 -*-

class Column:

	def __init__ (self, color, style, transition, padding):
		self.color = color
		self.style = style
		self.transition = transition
		self.padding = padding

class Layout:

	def __init__ (self, size, commit):
		
		self.size = size
		self.commit = commit
		self.bottom = {}
		for i in xrange(size):
			self.bottom[i] = ''
		#self.last = ''

		self.layout = []

	def swap (self):
		self.top = self.bottom.copy()

	def plot_top (self):
		transition = ''
		for i in self.top:
			c = self.top[i]
			if c: transition += " %s" % c[:7]
			else: transition += " %s" % "XXXXXXX"
		print "T {%s}" % transition

	def plot_bottom (self):
		transition = ''
		for i in self.bottom:
			c = self.bottom[i]
			if c: transition += " %s" % c[:7]
			else: transition += " %s" % "XXXXXXX"
		print "B {%s}" % transition

	def put_char(self, name, transition, padding):
		
		if name == None:
			color = 39
			style = 22
		elif isinstance(name, basestring):
			father = self.commit[name]
			color = 31 + father.column % 6
			if father.column / 6 % 2: style = 1
			else: style = 22
		elif isinstance(name, int):
			color = 31 + name
			if name / 6 % 2: style = 1
			else: style = 22

		self.layout.append(Column(color, style, transition, padding))
		#self.last = symbol
		#self.layout += '\x1b[3%dm%s' % (color, symbol)

	def compute_even_column(self, index, target):
		
		if index == target.column:
			if len(self.bottom[index]): padding = '│' # \u2502
			else: padding = ' '
			self.put_char(target.column, '•', padding) # \u2022 \u2502
			return

		top = self.top[index]
		bottom = self.bottom[index]

		if len(top) and len(bottom): # both ends are present

			if top == bottom:

				if bottom in target.parent:

					if target.hash in self.ne:
						
						self.put_char(bottom, '├', '│') # \u251c
					elif target.hash in self.nw:
						
						self.put_char(top, '┤', '│') # \u2524
					elif target.hash in self.commit[bottom].child:

						self.put_char(bottom, '├', '│') # \u251c
					else: #self.layout += '^'
						self.put_char(None, '^', '^')

				else: 
					self.put_char(top, '│', '│') # \u2502

			else: #self.layout += '@'
				self.put_char(None, '@', '@')

			return

		if len(bottom): # only lower end is present

			if bottom == target.hash:
				#self.layout += '┐' # \u2510
				self.put_char(None, '┐', '│') # \u2510 \u2502
				return

			if index > target.column:
				self.put_char(index, '┐', '│') # \u2510 \u2502
				return
			else:
				self.put_char(index, '┌', '│') # \u250c \u2502
				return
				
		if len(top): # only upper end is present

			self.put_char(None, '_', '_')
			return

		transition = ' '
		if len(self.layout):
			last = self.layout[-1]
			if last.transition == '←' or last.transition == '→':
				transition = '─' # \u2500
		self.put_char(None, transition, ' ')

	def compute_odd_column(self, index, target):

		father = None

		if index > target.column:
			
			for name in target.parent:
				if name in self.se:
					self.put_char(name, '←', ' ')
					return
		
		else:

			for name in reversed(target.parent):
				if name in self.sw:
					self.put_char(name, '→', ' ')
					return

		self.put_char(None, ' ', ' ')

	def compute_layout (self, target):

		self.layout = []

		self.ne = self.top.values()
		self.nw = []
		self.se = self.bottom.values()
		self.sw = []

		#print "North %s" % self.ne
		#print "South %s" % self.se

		'''
		if padding:
			if self.ne[0]: #self.layout += '│' # \u2502
				self.put_char(None, '│', '│') # \u2502
			else: #self.layout += ' '
				self.put_char(None, ' ', ' ')
			for i in self.ne[1:]:
				if i: #self.layout += ' │'
					self.put_char(None, '│', '│') # \u2502
				else: #self.layout += '  '
					self.put_char(None, ' ', ' ')
			#self.layout += '\n'
		'''

		if self.size:
			self.compute_even_column(0, target)
		for i in xrange(1, self.size):
			self.nw.append(self.ne.pop(0))
			self.sw.append(self.se.pop(0))
			#print "N (%s) (%s)" % (self.nw, self.ne)
			#print "S (%s) (%s)" % (self.sw, self.se)
			self.compute_odd_column(i, target)
			self.compute_even_column(i, target)
		#return self.layout

	def draw_padding (self):

		padding = ''
		for i in self.layout:
			padding += '\x1b[%d;%dm%s' % (i.color, i.style, i.padding)
		return padding

	def draw_transition (self):
		
		padding = ''
		for i in self.layout:
			if i.transition == '•': padding += '\x1b[m•'
			else: padding += '\x1b[%d;%dm%s' % (i.color, i.style, i.transition)
		return padding

