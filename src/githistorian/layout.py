# -*- encoding: utf-8 -*-

class Column:

	def __init__ (self, color, transition, padding):
		self.color = color
		self.transition = transition
		self.padding = padding

class Layout:

	def __init__ (self, size, hflip, vflip):

		self.size = size
		self.hflip = hflip

		self.layout = []
		self.track = {i:set() for i in range(-1, size)}

		self.ltee = '├' if self.hflip else '┤' # \u 251c or 2524
		self.rtee = '┤' if self.hflip else '├' # \u 2524 or 251c

		if vflip:
			self.lrcorner = '┌' if self.hflip else '┐' # \u 250c or 2510
			self.llcorner = '┐' if self.hflip else '┌' # \u 2510 or 250c
		else:
			self.lrcorner = '└' if self.hflip else '┘' # \u 2514 or 2518
			self.llcorner = '┘' if self.hflip else '└' # \u 2518 or 2514

		self.rarrow = '←' if self.hflip else '→' # \u 2192 or 2190
		self.larrow = '→' if self.hflip else '←' # \u 2190 or 2192

	def put_char(self, name, transition, padding):
		column = Column(31 + name % 6, transition, padding)
		self.layout.append(column)

	def compute_even_column(self, index, target):

		if index == target.column:

			if len(target.parent): padding = '│' # \u2502
			else: padding = ' '

			overlap = []
			for e in self.track[index]:
				if e == target.name: continue
				if e in target.parent: continue
				overlap.append(e)

			if len(overlap): transition = '╳' # \u2573
			else: transition = '•' # \u2022

			self.put_char(target.column, transition, padding)
			return

		if index > target.column:

			if target.name in self.track[index]:
				if len(self.track[index]) > 1:
					self.put_char(index, self.ltee, '│') # \u2502
				else:
					self.put_char(index, self.lrcorner, ' ')
				return

			if len(self.track[index]):
				self.put_char(index, '│', '│')
				return

			for jndex in range(index, self.size):
				if target.name in self.track[jndex]:
					self.put_char(jndex, self.rarrow, ' ')
					return

		else:

			if target.name in self.track[index]:
				if len(self.track[index]) > 1:
					self.put_char(index, self.rtee, '│') # \u2502
				else:
					self.put_char(index, self.llcorner, ' ')
				return

			if len(self.track[index]):
				self.put_char(index, '│', '│')
				return

			for jndex in reversed(range(0, index)):
				if target.name in self.track[jndex]:
					self.put_char(jndex, self.larrow, ' ') # \u2500
					return

		if len(self.track[index]):
			self.put_char(index, '│', '│') # \u2502
		else:
			self.put_char(index, ' ', ' ')

		return

	def compute_odd_column(self, index, target):

		if index > target.column:

			if target.name in self.track[index]:
				self.put_char(index, self.rarrow, ' ')
				return

			for jndex in range(index, self.size):
				if target.name in self.track[jndex]:
					self.put_char(jndex, self.rarrow, ' ')
					return

		else:

			if target.name in self.track[index - 1]:
				self.put_char(index - 1, self.larrow, ' ')
				return

			for jndex in reversed(range(0, index - 1)):
				if target.name in self.track[jndex]:
					self.put_char(jndex, self.larrow, ' ')
					return

		self.put_char(index, ' ', ' ')

	def compute_layout (self, target):

		self.layout = []

		if self.size: self.compute_even_column(0, target)

		for i in range(1, self.size):
			self.compute_odd_column(i, target)
			self.compute_even_column(i, target)

		for track in self.track.values():
			track.discard(target.name)

		for name in target.parent:
			self.track[target.column].add(name)

		if self.hflip: self.layout.reverse()
		return self.draw_transition(), self.draw_padding()

	def draw_padding (self):

		padding = ''
		for i in self.layout:
			padding += '\x1b[%dm%s' % (i.color, i.padding)
		return padding

	def draw_transition (self):

		padding = ''
		for i in self.layout:
			if i.transition == '•': padding += '\x1b[m•'
			else: padding += '\x1b[%dm%s' % (i.color, i.transition)
		return padding

