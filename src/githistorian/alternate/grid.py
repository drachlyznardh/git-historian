
class BaseGrid:

	class Column:
		def __init__(self, node):
			self.name = node.bottomName
			self.parents = set(node.parents)

		# Matching only the proper node
		def isSource(self, node): return self.name == node.topName

		# Mark parent as seen, removing it from the waiting list
		def parentSeen(self, node):
			self.parents.remove(node.topName)

	class Row:
		def __init__(self, nodeName, columns):
			self.nodeName = nodeName
			self.columns = columns

		# Append empty columns to match the target size
		def extend(self, targetSize):
			l = len(self.columns)
			if l == targetSize: return # We already match the layout size
			self.columns.extend([('', orientation.EMPTY, orientation.EMPTY) for e in range(targetSize - l)])

		# TODO please describe what is happening down there, it's scary!
		def dump(self, db, width, orientation):
			def _extend(s, w): return [e * w for e in s]

			# Extract index of last column, which does not to be repeated
			lastColumn = len(self.columns) -1

			# Compose layout format by exploding all columns, even and odd, and the adding the (fixed) description field
			# # print([(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)])
			# # print([(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)]])
			# # print([e for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)]])])
			# layout = ['{}{}'.format(e[0], '\x1b[m{}\x1b[m') for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)]])]
			# print([e for e in self.columns])
			# print([(i, c, e, [j for j in o]) for i, (c, e, o) in enumerate(self.columns)])
			# print([(i, c, e, _extend(o, width if lastColumn - i else 1)) for i, (c, e, o) in enumerate(self.columns)])
			# print([(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e, _extend(o, width if lastColumn - i else 1)) for i, (c, e, o) in enumerate(self.columns)]])
			# print([e[0] + '\x1b[m{}\x1b[m' for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e, _extend(o, width if lastColumn - i else 1)) for i, (c, e, o) in enumerate(self.columns)]])])
			layout = [e[0] + '\x1b[m{}\x1b[m' for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e, _extend(o, width if lastColumn - i else 1)) for i, (c, e, o) in enumerate(self.columns)]])]
			# layout = ['{}{}'.format(e[0], '\x1b[m{}\x1b[m') for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e, o * (width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)]])]
			# # layout = ''.join([c + e.get(flip, debug) + o.get(flip, debug, width if lastColumn - i else 1) for i,(c,e,o) in enumerate(self.columns)]) + '\x1b[m{}\x1b[m'
			return db[self.nodeName].dump(orientation, layout)

	def __init__(self, columns, rows):
		self.columns = columns
		self.rows = rows

	# Compose a row by computing all available columns
	def compose(self, node, orientation, verbose):

		def _color(i): return '\x1b[{}m'.format(31 + i % 6) # Helper function to set the color
		sIndex = 0 # Column of source node

		for i, c in enumerate(self.columns):

			# If this is my column
			if c.isSource(node): yield (_color(sIndex), orientation.SOURCE, orientation.EMPTY)

			# Am I straight below the source?
			elif node.topName in c.parents:
				sIndex = i # This is the source column
				c.parentSeen(node) # Above us, the parent has seen one child
				yield (_color(sIndex), orientation.RMERGE if c.parents else orientation.LCORNER, orientation.LARROW)

			# We have no relation, but arrows may pass through this cell
			else: yield (_color(sIndex), orientation.LARROW, orientation.LARROW) if i else (_color(sIndex), orientation.PIPE, orientation.EMPTY)

# This grid is a straight line
class NoGrid(BaseGrid):

	class AnyColumn:
		def __init__(self):
			self.name = []

		# Accepting anyone
		def isSource(self, node): return True

	def __init__(self):
		super().__init__([self.AnyColumn()], [])

	def dealWith(self, node, orientation, verbose):
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, orientation, verbose)]))

	def done(self, flip): return reversed(self.rows) if flip else self.rows

# This grid is simple and dumb, it assigns a new column to each chain
class DumbGrid(BaseGrid):

	# Append new column for each node, immediately define its row
	def dealWith(self, node, verbose):
		self.columns.append(self.Column(node))
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, verbose)]))

	# No post-processing, just extend columns to the limit for alignment
	def done(self, flip):
		s = len(self.columns)
		for r in self.rows: r.extend(s)
		return reversed(self.rows) if flip else self.rows

# Return grid class by name
def getGrid(name):
	return {
			'no': NoGrid,
			'dumb': DumbGrid,
		}.get(name.lower(), NoGrid)

