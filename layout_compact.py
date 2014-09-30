# Compact Layout module for Git-Historian
# -*- encoding: utf-8 -*-

class Layout:
	def __init__ (self, size):
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

	def draw_layout (self, target):
		
		layout = ''

		top_right = self.top.values()
		top = None
		top_left = []
		bottom_right = self.bottom.values()
		bottom = None
		bottom_left = []
		#print "T-- (%s) '%s' (%s)" % (top_left, top, top_right)
		#print "B-- (%s) '%s' (%s)" % (bottom_left, bottom, bottom_right)

		for i in self.top:
	
			if top: top_left.append(top)
			top = top_right.pop(0)
			if bottom: bottom_left.append(bottom)
			bottom = bottom_right.pop(0)
			
			#print "\tC[%d][%d] ^(%s) v(%s)" % (i, target.column, top, bottom)
			#print "(%s) (%s)" % (hit_cols, missing_cols)
			#print "T%02d (%s) '%s' (%s)" % (i, top_left, top, top_right)
			#print "B%02d (%s) '%s' (%s)" % (i, bottom_left, bottom, bottom_right)

			# Commit column, print the star
			if i == target.column:
				layout += '⬤' # \U2B24
				continue

			# Every column before the commit has a preceeding whitespace
			#if i > target.column:
			#	if target.hash in top_right: layout += '─' # \U2500
			#	else: layout += ' '

			if top != '':
				
				if bottom != '':

					if i > target.column: # after the target commit
						layout += ' '
	
					if top == bottom:
						layout += '│'
					elif bottom == target.hash:
						layout += '├'
					else:
						layout += '?'

					if i < target.column: # before the target commit
						# Both top and bottom cells have values
						if (target.hash == bottom or target.hash in bottom_left) and (target.hash == top or target.hash in top_right):
							layout += '→' # \U251C \u2500
						elif top == bottom:
							#if target.hash == top_right[0]:
							#	layout += '│→' # \U2502
							#else:
							layout += ' ' # \U2502
						elif target.hash == bottom and target.hash in bottom_right:
							layout += '→'
						else:
							layout += '?'

				else:
					if top == target.hash:
						#or target.hash in top_right:
						layout += '→┘' # \u2500 \U2518
					else: layout += '^'

			elif bottom != '':
				
				if bottom == target.hash:
					layout += '←┐' # \u2500 \U2510
				else: layout += 'v'

			else: layout += '  '

			# Every column after the commit has a following whitespace
			#if i < target.column:
			#	if target.hash in top_right:
			#		layout += '─' # \U2500
			#	else: layout += ' '

		return layout

