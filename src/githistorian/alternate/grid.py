
# Base class for all cells
class BaseCell:

	def isSource(self, node): raise NotImplemented()
	def isWaitingFor(self, node): raise NotImplemented()
	def isOnlyWaitingFor(self, node): raise NotImplemented()
	def isDoneWaiting(self): raise NotImplemented()
	def markSeen(self, node): raise NotImplemented()

# A cell to always accept any node
class AnyCell(BaseCell):
	def isSource(self, node): return True
	def isDoneWaiting(self): return False

class SimpleCell(BaseCell):
	def __init__(self, node):
		self._source = node.topName
		self._isMerge = len(node.parents) > 1
		self._waitList = set(node.parents)

	def isSource(self, node): return self._source == node.topName
	def isWaitingFor(self, node): return node.topName in self._waitList
	def isOnlyWaitingFor(self, node): return node.topName in self._waitList and len(self._waitList) == 1
	def isDoneWaiting(self): return len(self._waitList) == 0
	def markSeen(self, node): self._waitList.remove(node.topName)
	def isMerge(self): return self._isMerge

class Box:
	def __init__(self, color, evenCell, oddCell):
		self.evenColor = color[0]
		self.evenCell = evenCell
		self.oddColor = color[1]
		self.oddCell = oddCell

	def unpack(self, width):
		def _expand(s, w): return [e * w for e in s]

		first = '\x1b[{}m{}\x1b[{}m{}'.format(self.evenColor, self.evenCell[0], self.oddColor, self.oddCell[0] * width)
		other = '\x1b[{}m{}\x1b[{}m{}'.format(self.evenColor, self.evenCell[1], self.oddColor, self.oddCell[1] * width)
		alter = '\x1b[{}m{}\x1b[{}m{}'.format(self.evenColor, self.evenCell[2], self.oddColor, self.oddCell[2] * width)

		return first, other, alter

# Base class for all grids. Derived classes are expected to implement:
# * def dealWith(self, node, logger): node is visited, something must be done
# * def done(self, flip): visit is order, layout is expected row by row (according to vertical flip)
class BaseGrid:

	class Row:
		def __init__(self, nodeName, cell):
			self.nodeName = nodeName
			self.cell = cell

		# Append empty cell to match the target size
		def extend(self, orientation, gridWidth, logger):
			l = len(self.cell)
			logger.log('Extending from {} to {}', l, gridWidth)
			if l == gridWidth: return # We already match the layout size
			logger.log('Before {}', self.cell)
			self.cell.extend([Box((0, 0), orientation.EMPTY, orientation.EMPTY) for e in range(gridWidth - l)])
			logger.log('After {}', self.cell)

		# TODO please describe what is happening down there, it's scary!
		def dump(self, db, width, orientation, logger):

			# Expand odd cell to width
			def _expand(s, w): return [e * w for e in s]

			# Compute index of last column, which must not be expanded
			lastColumn = len(self.cell) -1

			return db[self.nodeName].dump(orientation, [
				'{}{}'.format(''.join(e), '\x1b[m{}\x1b[m') for e in zip(*[ box.unpack(width if lastColumn - index else 1) for index, box in enumerate(self.cell) ])
			], logger)

			# Each chain can dump its content according to the layout emerging from the cell
			return db[self.nodeName].dump(orientation, [

					# List of (colors and stacks of symbols) is zipped to lists of (colors and symbols), node description marker is appended
					''.join(e) + '\x1b[m{}\x1b[m' for e in zip(*[(
					ce + e1 + co + o1, ce + e2 + co + o2) for (
					ce, co),
					(e1, e2),
					(o1, o2) in [

						# Columns (one color and two stacks of symbols) are extracted one by one. Odd stacks are expanded to width
						(c, e, _expand(o, width if lastColumn - i else 1)) for i, (c, e, o) in enumerate(self.cell)]])], logger)

	def __init__(self, cell, rows):
		self.cell = cell
		self.rows = rows

	# Compose a row by computing all available cell
	def compose(self, node, orientation, logger):

		def _color(i): return 31 + i % 6 # Helper function to set the color
		def _oneColor(i): return _color(i), _color(i)
		def _twoColors(i, j): return _color(i), _color(j)

		sIndex = 0 # Column of source node
		stillMissing = True
		childSeen = False

		for i, c in enumerate(self.cell):

			# If this is my column
			if c.isSource(node):
				sIndex = i # This is the source column
				logger.log('{} is source for cell #{}', node, i)
				stillMissing = False
				yield Box(_oneColor(sIndex), orientation.SOURCE, orientation.EMPTY)
				continue

			# Am I straight below the source?
			if c.isWaitingFor(node):
				sIndex = i # Source is above
				logger.log('{} is in list for cell #{}', node, i)
				c.markSeen(node) # Above us, the parent has seen one child

				if c.isMerge() and not c.isDoneWaiting():
					yield Box(_oneColor(sIndex), orientation.RMERGE, orientation.LARROW)
				elif childSeen:
					yield Box(_oneColor(sIndex), orientation.BROTHER, orientation.LARROW)
				else:
					yield Box(_oneColor(sIndex), orientation.LCORNER, orientation.LARROW)

				childSeen = True
				continue

			# We have no relation, but arrows may pass through this cell
			isDoneWaiting = c.isDoneWaiting()
			logger.log('{} is unrelated to cell #{}', node, i)
			logger.log('Cell #{} has {}seen a child, is {}done waiting for parents', i, '' if childSeen else 'not ', '' if isDoneWaiting else 'not ')

			if isDoneWaiting:
				if childSeen:
					yield Box(_oneColor(sIndex), orientation.LARROW, orientation.LARROW)
				else:
					yield Box(_oneColor(sIndex), orientation.EMPTY, orientation.EMPTY)
			elif childSeen:
				yield Box(_twoColors(i, sIndex), orientation.PIPE, orientation.LARROW)
			else:
				yield Box(_twoColors(i, sIndex), orientation.PIPE, orientation.EMPTY)

		# No column was available, make a new one
		if stillMissing:
			logger.log('No cell was available for #{}, making one', node)
			self.cell.append(SimpleCell(node))
			yield Box(_oneColor(sIndex), orientation.SOURCE, orientation.EMPTY)

	# Visit the graph and populate the grid
	def unroll(self, visitClass, heads, db, orientation, vflip, logger):

		visit = visitClass(heads, db, logger -2)

		while visit:
			e = visit.pop()
			logger.log('{} unrolling {}', self.__class__.__name__, e)
			self.dealWith(e, orientation, logger -1)
			logger.log('Appending {} to visit', e.parents)
			visit.push([db[p] for p in e.parents])

		return self.done(orientation, vflip, logger)

# This grid is a straight line
class NoGrid(BaseGrid):
	def __init__(self): super().__init__([AnyCell()], [])

	def dealWith(self, node, orientation, logger):
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, orientation, logger)]))

	def done(self, orientation, flip, logger): return reversed(self.rows) if flip else self.rows

# This grid is a straight line, with vertical ordering
class StraightGrid(BaseGrid):
	def __init__(self): super().__init__([AnyCell()], [])

	def dealWith(self, node, orientation, logger):
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, orientation, logger)]))

	def done(self, orientation, flip, logger): return reversed(self.rows) if flip else self.rows

# This grid is simple and dumb, it assigns a new column to each chain
class StairsGrid(BaseGrid):
	def __init__(self):
		super().__init__([], [])
		self.width = 0

	# Append new column for each node, immediately define its row
	def dealWith(self, node, orientation, logger):
		self.cell.append(SimpleCell(node))
		self.width = max(self.width, len(self.cell))
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, orientation, logger)]))
		logger.log('Current width is {}', self.width)

	# No post-processing, just extend cell to the limit for alignment
	def done(self, orientation, flip, logger):
		for r in self.rows: r.extend(orientation, self.width, logger -2)
		return reversed(self.rows) if flip else self.rows

# This grid is ugly, but close to natural
class UglyGrid(BaseGrid):
	def __init__(self):
		super().__init__([], [])
		self.width = 0

	# Verify whether given node is a branching point. True when given node is
	# the only node in all waiting lists in which it appears
	def isBranchingPoint(self, node):
		for c in self.cell:
			if not c.isOnlyWaitingFor(node): return False
		return True

	def indexOfFirstChild(self, index, node):
		for i, c in enumerate(self.cell[index:]):
			if c.isWaitingFor(node): return index + i

	# Compose a row by computing all available cell
	def compose(self, node, orientation, logger):

		def _color(i): return 31 + i % 6 # Helper function to set the color
		def _oneColor(i): return _color(i), _color(i)
		def _twoColors(i, j): return _color(i), _color(j)

		sIndex = 0 # Column of source node
		stillMissing = True
		childSeen = False
		missingChildren = len(node.children)

		for i, c in enumerate(self.cell):

			# If this is my column
			if c.isSource(node):
				sIndex = i # This is the source column
				logger.log('{} is source for cell #{}', node, i)
				stillMissing = False
				yield Box(_oneColor(sIndex), orientation.SOURCE, orientation.EMPTY)
				continue

			# Am I straight below the source?
			if c.isWaitingFor(node):
				sIndex = i # Source is above
				logger.log('{} is in list for cell #{}', node, i)

				# Am I going to originate branches and free columns up?
				if self.isBranchingPoint(node):
					logger.log('{} is a branching point and is {}missing children', node, '' if missingChildren else 'not ')
					stillMissing = False
					c.markSeen(node) # Above us, the parent has seen one child
					if missingChildren:
						yield Box(_twoColors(sIndex, self.indexOfFirstChild(i, node)), orientation.SOURCE, orientation.RARROW)
					else:
						yield Box(_oneColor(sIndex), orientation.SOURCE, orientation.EMPTY)
					continue

				c.markSeen(node) # Above us, the parent has seen one child

				if c.isMerge() and not c.isDoneWaiting():
					yield Box(_oneColor(sIndex), orientation.RMERGE, orientation.LARROW)
				elif childSeen:
					yield Box(_oneColor(sIndex), orientation.BROTHER, orientation.LARROW)
				elif stillMissing: # Still waiting for source
					yield Box(_oneColor(sIndex), orientation.LCORNER, orientation.LARROW)
				else:
					yield Box(_oneColor(sIndex), orientation.RCORNER, orientation.EMPTY)

				childSeen = True
				missingChildren -= 1
				continue

			# We have no relation, but arrows may pass through this cell
			isDoneWaiting = c.isDoneWaiting()
			logger.log('{} is unrelated to cell #{}', node, i)
			logger.log('Cell #{} has {}seen a child, is waiting for {} children and is {}done waiting for parents', i, '' if childSeen else 'not ', missingChildren, '' if isDoneWaiting else 'not ')

			if isDoneWaiting:
				if childSeen:
					yield Box(_oneColor(sIndex), orientation.LARROW, orientation.LARROW)
				else:
					yield Box(_oneColor(sIndex), orientation.EMPTY, orientation.EMPTY)
			elif childSeen:
				yield Box(_twoColors(i, sIndex), orientation.PIPE, orientation.LARROW)
			else:
				yield Box(_twoColors(i, sIndex), orientation.PIPE, orientation.EMPTY)

		if stillMissing:
			logger.log('No cell was available for #{}, making one', node)
			self.cell.append(SimpleCell(node))
			yield Box(_oneColor(sIndex), orientation.SOURCE, orientation.EMPTY)

	# Append new column for each node, immediately define its row
	def dealWith(self, node, orientation, logger):
		row = self.Row(node.topName, [e for e in self.compose(node, orientation, logger)])
		self.rows.append(row)
		self.width = max(self.width, len(self.cell))
		logger.log('Current width is {}', self.width)

	# No post-processing, just extend cell to the limit for alignment
	def done(self, orientation, flip, logger):
		for r in self.rows: r.extend(orientation, self.width, logger -2)
		return reversed(self.rows) if flip else self.rows

# This grid is a straight line
# Return grid class by name or break
def getGrid(name):
	return {
			'no': NoGrid,
			'straight': StraightGrid,
			'stairs': StairsGrid,
			'ugly': UglyGrid,
		}.get(name.lower())

