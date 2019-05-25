
# Base class for all cells
class BaseCell:
	# def __init__(self, source, waitList):
	#	self.source = source
	#	self.waitList = waitList

	def isSource(self, node): raise NotImplemented()
	def isWaitingFor(self, node): raise NotImplemented()
	def markSeen(self, node): raise NotImplemented()

# A cell to always accept any node
class AnyCell(BaseCell):
	def isSource(self, node): return True

# Base class for all grids. Derived classes are expected to implement:
# * def dealWith(self, node, logger): node is visited, something must be done
# * def done(self, flip): visit is order, layout is expected row by row (according to vertical flip)
class BaseGrid:

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

			# Expand odd columns to width
			def _expand(s, w): return [e * w for e in s]

			# Compute index of last column, which must not be expanded
			lastColumn = len(self.columns) -1

			# Each chain can dump its content according to the layout emerging from the columns
			return db[self.nodeName].dump(orientation, [

					# List of (colors and stacks of symbols) is zipped to lists of (colors and symbols), node description marker is appended
					e[0] + '\x1b[m{}\x1b[m' for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [

						# Columns (one color and two stacks of symbols) are extracted one by one. Odd stacks are expanded to width
						(c, e, _expand(o, width if lastColumn - i else 1)) for i, (c, e, o) in enumerate(self.columns)]])])

	def __init__(self, columns, rows):
		self.columns = columns
		self.rows = rows

	# Compose a row by computing all available columns
	def compose(self, node, orientation, logger):

		def _color(i): return '\x1b[{}m'.format(31 + i % 6) # Helper function to set the color
		sIndex = 0 # Column of source node

		for i, c in enumerate(self.columns):

			# If this is my column
			if c.isSource(node): yield (_color(sIndex), orientation.SOURCE, orientation.EMPTY)

			# Am I straight below the source?
			elif node.topName in c.parents:
				sIndex = i # This is the source column
				c.markSeen(node) # Above us, the parent has seen one child
				yield (_color(sIndex), orientation.RMERGE if c.parents else orientation.LCORNER, orientation.LARROW)

			# We have no relation, but arrows may pass through this cell
			else: yield (_color(sIndex), orientation.LARROW, orientation.LARROW) if i else (_color(sIndex), orientation.PIPE, orientation.EMPTY)

	# Visit the graph and populate the grid
	def unroll(self, visitClass, heads, db, orientation, vflip, logger):

		visit = visitClass(heads)

		while visit:
			e = visit.pop()
			self.dealWith(e, orientation, logger)
			visit.push([db[p] for p in e.parents])

		return self.done(vflip)

# This grid is a straight line
class NoGrid(BaseGrid):
	def __init__(self): super().__init__([AnyCell()], [])

	def dealWith(self, node, orientation, logger):
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, orientation, logger)]))

	def done(self, flip): return reversed(self.rows) if flip else self.rows

# This grid is simple and dumb, it assigns a new column to each chain
class DumbGrid(BaseGrid):

	# Append new column for each node, immediately define its row
	def dealWith(self, node, logger):
		self.columns.append(self.Column(node))
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, logger)]))

	# No post-processing, just extend columns to the limit for alignment
	def done(self, flip):
		s = len(self.columns)
		for r in self.rows: r.extend(s)
		return reversed(self.rows) if flip else self.rows

# This grid is a straight line, with vertical ordering
class StraightGrid(BaseGrid):
	def __init__(self): super().__init__([AnyCell()], [])

	def dealWith(self, node, orientation, logger):
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, orientation, logger)]))

	def done(self, flip): return reversed(self.rows) if flip else self.rows

	# Visit the graph and populate the grid
	def unroll(self, visitClass, heads, db, orientation, vflip, logger):

		logger.log('StraightGrid unrolling')
		visit = visitClass(heads)

		while visit:
			e = visit.pop()
			logger.log('StraightGrid unrolling {}', e)
			self.dealWith(e, orientation, logger)
			logger.log('Appending {} to visit', e.parents)
			visit.push([db[p] for p in e.parents])

		return self.done(vflip)

# This grid is a straight line
# Return grid class by name or break
def getGrid(name):
	return {
			'no': NoGrid,
			'straight': StraightGrid,
			'dumb': DumbGrid,
		}.get(name.lower())

