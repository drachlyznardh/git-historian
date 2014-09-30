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

	def draw_layout (self, target):
		
		self.layout = ''

		self.top_right = self.top.values()
		self.top_current = None
		self.top_left = []
		self.bottom_right = self.bottom.values()
		self.bottom_current = None
		self.bottom_left = []
		#print "T-- (%s) '%s' (%s)" % (top_left, top, top_right)
		#print "B-- (%s) '%s' (%s)" % (bottom_left, bottom, bottom_right)

		self.ne = self.top.values()
		self.nw = []
		self.se = self.bottom.values()
		self.sw = []

		if self.size:
			self.draw_even_column(0, target)
		for i in xrange(1, self.size):
			self.nw.append(self.ne.pop(0))
			self.sw.append(self.se.pop(0))
			#print "N (%s) (%s)" % (self.nw, self.ne)
			#print "S (%s) (%s)" % (self.sw, self.se)
			self.draw_odd_column(i, target)
			self.draw_even_column(i, target)
		#self.layout += '\n'
		return self.layout

		for i in self.top:
	
			if self.top_current:
				self.top_left.append(self.top_current)
			self.top_current = self.top_right.pop(0)

			if self.bottom_current:
				self.bottom_left.append(self.bottom_current)
			self.bottom_current = self.bottom_right.pop(0)
			
			#print "\tC[%d][%d] ^(%s) v(%s)" % (i, target.column, top, bottom)
			#print "(%s) (%s)" % (hit_cols, missing_cols)
			#print "T%02d (%s) '%s' (%s)" % (i, top_left, top, top_right)
			#print "B%02d (%s) '%s' (%s)" % (i, bottom_left, bottom, bottom_right)

			# Commit column, print the star
			if i == target.column:
				self.layout += '⬤' # \U2B24
				continue

			# Every column before the commit has a preceeding whitespace
			#if i > target.column:
			#	if target.hash in top_right: layout += '─' # \U2500
			#	else: layout += ' '

			if self.top_current != '':
				
				if self.bottom_current != '':

					if i > target.column: # after the target commit
						self.layout += ' '
	
					if self.top_current == self.bottom_current:
						self.layout += '│'
					elif self.bottom_current == target.hash:
						self.layout += '├'
					else:
						self.layout += '?'

					if i < target.column: # before the target commit
						# Both top and bottom cells have values
						if (target.hash == self.bottom_current or target.hash in self.bottom_left) and (target.hash == self.top_current or target.hash in self.top_right):
							self.layout += '→' # \U251C \u2500
						elif self.top_current == self.bottom_current:
							#if target.hash == top_right[0]:
							#	layout += '│→' # \U2502
							#else:
							self.layout += ' ' # \U2502
						elif target.hash == bottom_current and target.hash in bottom_right:
							self.layout += '→'
						else:
							self.layout += '?'

				else:
					if self.top_current == target.hash:
						#or target.hash in top_right:
						self.layout += '→┘' # \u2500 \U2518
					else: self.layout += '^'

			elif self.bottom_current != '':
				
				if self.bottom_current == target.hash:
					self.layout += '←┐' # \u2500 \U2510
				else: self.layout += 'v'

			else: self.layout += '  '

			# Every column after the commit has a following whitespace
			#if i < target.column:
			#	if target.hash in top_right:
			#		layout += '─' # \U2500
			#	else: layout += ' '

		return self.layout

