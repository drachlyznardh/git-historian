# Layout module for Git-Historian
# -*- encoding: utf-8 -*-

class Column:

	def __init__ (self, color, transition, padding):
		self.color = color
		self.transition = transition
		self.padding = padding

class Layout:

	def __init__ (self, size, commit, debug):
		
		self.size = size
		self.debug = debug

		self.layout = []

		self.track = {i:set() for i in xrange(size)}

	def plot_track (self):
		for track in self.track.values():
			print track

	def put_char(self, name, transition, padding):
		
		if isinstance(name, basestring):
			father = self.commit[name]
			color = 31 + father.column % 6
		elif isinstance(name, int):
			color = 31 + name % 6
		else:
			print 'WTF is %s' % name
			color = 39

		self.layout.append(Column(color, transition, padding))

	def compute_even_column(self, index, target):
		
		if index == target.column:

			if len(target.parent): padding = '│' # \u2502
			else: padding = ' '
			
			self.put_char(target.column, '•', padding) # \u2022 \u2502
			return

		if index > target.column:

			if target.hash in self.track[index]:
				if len(self.track[index]) > 1:
					self.put_char(index, '┤', '│') # \u2524 \u2502
				else:
					self.put_char(index, '┘', ' ') # \u2518
				return

			if len(self.track[index]):
				self.put_char(index, '│', '│')
				return

			for jndex in range(index, self.size):
				if target.hash in self.track[jndex]:
					self.put_char(jndex, '→', ' ')
					return

		else:

			if target.hash in self.track[index]:
				if len(self.track[index]) > 1:
					self.put_char(index, '├', '│') # \u251c \u2502
				else:
					self.put_char(index, '└', ' ') # \u2514
				return

			if len(self.track[index]):
				self.put_char(index, '│', '│')
				return

			for jndex in reversed(range(0, index)):
				if target.hash in self.track[jndex]:
					self.put_char(jndex, '←', ' ') # \u2500
					return

		if len(self.track[index]):
			self.put_char(index, '│', '│') # \u2502
		else:
			self.put_char(index, ' ', ' ')

		return

	def compute_odd_column(self, index, target):

		if index > target.column:
			
			if target.hash in self.track[index]:
				self.put_char(index, '→', ' ')
				return
			
			for jndex in range(index, self.size):
				if target.hash in self.track[jndex]:
					self.put_char(jndex, '→', ' ')
					return
		
		else:

			if target.hash in self.track[index - 1]:
				self.put_char(index - 1, '←', ' ')
				return

			for jndex in reversed(range(0, index - 1)):
				if target.hash in self.track[jndex]:
					self.put_char(jndex, '←', ' ')
					return

		self.put_char(index, ' ', ' ')

	def compute_layout (self, target):

		self.layout = []

		if self.debug:
			self.plot_track()
			print target.child

		if self.size:
			self.compute_even_column(0, target)
		for i in xrange(1, self.size):
			self.compute_odd_column(i, target)
			self.compute_even_column(i, target)

		for track in self.track.values():
			track.discard(target.hash)

		for name in target.parent:
			self.track[target.column].add(name)

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

