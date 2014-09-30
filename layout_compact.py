# Compact Layout module for Git-Historian
# -*- encoding: utf-8 -*-

class Layout:
	def __init__ (self, size):
		self.size = size
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

	def draw_even_column(self, index, target):
		
		if index == target.column:
			self.layout += '⬤' # \u2b24
			return

		top = self.top[index]
		bottom = self.bottom[index]
		#print "#%02d ^(%s) v(%s)" % (index, top, bottom)

		if top and len(top):
			'CULO'

			if bottom and len(bottom):

				if top == bottom:
					self.layout += '│' # \u2502

				elif bottom == target.hash:
					self.layout += '├' # \u251c
		elif bottom and len(bottom):
			
			if bottom == target.hash:
				self.layout += '┐' # \u2510
				
		else:
			self.layout += ' '


	def draw_odd_column(self, index, target):

		west = target.hash in self.nw or target.hash in self.sw
		east = target.hash in self.ne or target.hash in self.se

		if west and east:

			if index > target.column:
				self.layout += '←'
			else:
				self.layout += '→'

		else: self.layout += ' '

	def draw_layout (self, target, padding = 0):
		
		self.layout = ''

		self.ne = self.top.values()
		self.nw = []
		self.se = self.bottom.values()
		self.sw = []

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

