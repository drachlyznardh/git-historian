# Compact Layout module for Git-Historian
# -*- encoding: utf-8 -*-

class Layout:
	def __init__ (self, size, commit):
		
		self.size = size
		self.commit = commit
		self.bottom = {}
		for i in xrange(size):
			self.bottom[i] = ''

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

	def put_char(self, name, symbol):
		
		if name:
			father = self.commit[name]
			color = 1 + father.column % 7
		else: color = 9

		self.last = symbol
		self.layout += '\x1b[3%dm%s' % (color, symbol)

	def draw_even_column(self, index, target):
		
		if index == target.column:
			self.put_char(None, '⬤') # \u2b24
			return

		top = self.top[index]
		bottom = self.bottom[index]
		#print "#%02d ^(%s) v(%s)" % (index, top, bottom)

		if len(top) and len(bottom): # both ends are present

			if top == bottom:

				if bottom in target.parent:

					if target.hash in self.ne:
						
						self.put_char(bottom, '├') # \u251c
					elif target.hash in self.nw:
						
						self.put_char(top, '┤') # \u2524
					elif target.hash in self.commit[bottom].child:

						self.put_char(bottom, '├') # \u251c
					else: self.layout += '^'

				else: 
					self.put_char(top, '│') # \u2502

			else: self.layout += '@'

			return

		if len(bottom): # only lower end is present

			if bottom == target.hash:
				self.layout += '┐' # \u2510
				return

			for name in target.parent:
				if name in self.se:
					self.put_char(name, '┐') # \u2510
					return

			self.layout += '\x1b[m '
				
		if len(top): # only upper end is present

			self.put_char(None, '_')
			return

		if self.last == '←' or self.last == '→':
			self.layout += '─' # \u2500
		else: self.layout += ' '

	def draw_odd_column(self, index, target):

		father = None

		if index > target.column:
			
			for name in target.parent:
				if name in self.se:
					self.put_char(name, '←')
					return
		
		else:

			for name in reversed(target.parent):
				if name in self.sw:
					self.put_char(name, '→')
					return

		self.put_char(None, ' ')

	def draw_layout (self, target, padding = 0):
		
		self.layout = ''

		self.ne = self.top.values()
		self.nw = []
		self.se = self.bottom.values()
		self.sw = []

		#print "North %s" % self.ne
		#print "South %s" % self.se

		if padding:
			if self.ne[0]: self.layout += '│' # \u2502
			else: self.layout += ' '
			for i in self.ne[1:]:
				if i: self.layout += ' │'
				else: self.layout += '  '
			self.layout += '\n'

		if self.size:
			self.draw_even_column(0, target)
		for i in xrange(1, self.size):
			self.nw.append(self.ne.pop(0))
			self.sw.append(self.se.pop(0))
			#print "N (%s) (%s)" % (self.nw, self.ne)
			#print "S (%s) (%s)" % (self.sw, self.se)
			self.draw_odd_column(i, target)
			self.draw_even_column(i, target)
		return self.layout

