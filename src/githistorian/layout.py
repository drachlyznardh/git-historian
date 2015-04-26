# -*- encoding: utf-8 -*-

class Column:

	def __init__ (self, color, transition, padding):
		self.color = color
		self.transition = transition
		self.padding = padding

class Layout:

	def __init__ (self, size):
		self.size = size
		self.layout = []
		self.track = {i:set() for i in xrange(-1, size)}

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
					self.put_char(index, '┤', '│') # \u2524 \u2502
				else:
					self.put_char(index, '┘', ' ') # \u2518
				return

			if len(self.track[index]):
				self.put_char(index, '│', '│')
				return

			for jndex in range(index, self.size):
				if target.name in self.track[jndex]:
					self.put_char(jndex, '→', ' ')
					return

		else:

			if target.name in self.track[index]:
				if len(self.track[index]) > 1:
					self.put_char(index, '├', '│') # \u251c \u2502
				else:
					self.put_char(index, '└', ' ') # \u2514
				return

			if len(self.track[index]):
				self.put_char(index, '│', '│')
				return

			for jndex in reversed(range(0, index)):
				if target.name in self.track[jndex]:
					self.put_char(jndex, '←', ' ') # \u2500
					return

		if len(self.track[index]):
			self.put_char(index, '│', '│') # \u2502
		else:
			self.put_char(index, ' ', ' ')

		return

	def compute_odd_column(self, index, target):

		if index > target.column:
			
			if target.name in self.track[index]:
				self.put_char(index, '→', ' ')
				return
			
			for jndex in range(index, self.size):
				if target.name in self.track[jndex]:
					self.put_char(jndex, '→', ' ')
					return
		
		else:

			if target.name in self.track[index - 1]:
				self.put_char(index - 1, '←', ' ')
				return

			for jndex in reversed(range(0, index - 1)):
				if target.name in self.track[jndex]:
					self.put_char(jndex, '←', ' ')
					return

		self.put_char(index, ' ', ' ')

	def compute_layout (self, target):

		self.layout = []

		if self.size: self.compute_even_column(0, target)

		for i in xrange(1, self.size):
			self.compute_odd_column(i, target)
			self.compute_even_column(i, target)

		for track in self.track.values():
			track.discard(target.name)

		for name in target.parent:
			self.track[target.column].add(name)

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

