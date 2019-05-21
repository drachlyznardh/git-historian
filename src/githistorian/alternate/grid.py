
class Grid:

	class Column:
		def __init__(self):
			self.occupiedBy = None
			self.waitingFor = set()

		def assign(self, node):
			self.occupiedBy = node
			self.waitingFor = set(node.children)

		def wasSeen(self, name):
			if name in self.waitingFor: self.waitingFor.remove(name)

		def get(self, index, node):
			if node is self.occupiedBy: return '\x1b[m{} '
			return '\x1b[{}m| '.format(31 + index % 7)

	def __init__(self):
		self.columns = [self.Column()]

	def assign(self, node):

		print('Checking node {}'.format(node))

		dealtWith = False
		state = 0 # Looking
		for c in self.columns: # Look for column where node belongs
			print('\tChecking column {}/{}'.format(c.occupiedBy, c.waitingFor))
			if state == 0: # Looking for waiting
				if node.topName in c.waitingFor:
					c.assign(node)
					state = 1 # Closing others
					continue
			elif state == 1: # Closing others
				c.wasSeen(node.name)

		if not dealtWith: # Node does not belong in any columns
			print('\tNo column is waiting for {}'.format(node.topName))
			for c in self.columns:
				if not c.occupiedBy:
					c.assign(node)
					dealtWith = True

		if not dealtWith: # There are no free columns
			print('\tNo column is free for {}'.format(node.topName))
			c = self.Column()
			c.assign(node)
			self.columns.append(c)

	def dealWith(self, node):

		self.assign(node)
		return '{}{}'.format(''.join(c.get(i, node) for i, c in enumerate(self.columns)), '\x1b[32m{}\x1b[m')

from enum import Enum

# Single-value representation of flip
class FlipState(Enum):
	NONE  = 0 # No flip, top to bottom, left to right
	HFLIP = 1 # Horizontal flip, top to bottom, right to left
	VFLIP = 2 # Vertical flip, bottom to top, left to right
	BOTH  = 3 # Both flips, bottom to top, right to left

# Helper class for even, unrepeatable columns holding commits and relationships
class EvenColumn(Enum):
	EMPTY   = 0 # Column is empty with no arrow
	SOURCE  = 1 # Column holds the current commit
	LCORNER = 2 # Left corner, arrow bending up from yet unseen source node
	RCORNER = 3 # Right corner, arrow bending up from already seen source node
	LMERGE  = 4 # Left merge, arrow joining from yet unseen source node
	RMERGE  = 5 # Right merge, arrow joining from already seen source node
	PIPE    = 6 # Straight line
	LARROW  = 7 # Arrow towards target's column from yet unseen source node
	RARROW  = 8 # Arrow towards target's column from already seen source node

	def get(self, flip, debug):
		if debug: return '{}'.format(self.value)
		return {
				EvenColumn.EMPTY   : '    ',
				EvenColumn.SOURCE  : ['{}' for e in range(4)],
				EvenColumn.LCORNER : '└┘┌┐', # U+2514 2518 250c 2510
				EvenColumn.RCORNER : '┘└┐┌', # U+2518 2514 2510 250c
				EvenColumn.LMERGE  : '┤├┤├', # U+251c 2524 251c 2524
				EvenColumn.RMERGE  : '├┤├┤', # U+251c 2524 251c 2524
				EvenColumn.PIPE    : '││││', # U+2502 2502 2502 2502
				EvenColumn.LARROW  : '←→←→',
				EvenColumn.RARROW  : '→←→←',
			}[self][flip.value]

# Helper class for odd, repeatble columns holding only arrows
class OddColumn(Enum):
	EMPTY   = 0 # Column is empty
	LARROW  = 1 # Arrow towards target's column from yet unseen source node
	RARROW  = 2 # Arrow towards target's column from already seen source node

	def _get(self, flip, debug):
		if debug: return '{}'.format(self.value)
		return {
				OddColumn.EMPTY  : '    ',
				OddColumn.LARROW : '←→←→',
				OddColumn.RARROW : '→←→←',
			}[self][flip.value]

	# Odd columns are repeatable, so we get the symbol once and then repeat it
	def get(self, flip, debug, counter):
		symbol = self._get(flip, debug)
		if counter == 1: return symbol
		return ''.join([symbol for e in range(counter)])

# Each line type requires a slightly different column layout, structure remains
# the same but symbols in the source column vary
class RowState(Enum):
	CHAINFIRST  = 0 # First line of first commit in chain
	COMMITFIRST = 1 # First line of commit, second in chain or later
	CONTENT     = 2 # Second or following line in commit

# Base class for all grids
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
			self.columns.extend([('', EvenColumn.EMPTY, OddColumn.EMPTY) for e in range(targetSize - l)])

		def dump(self, db, oddRange):

			# Simulating options
			flip = FlipState.NONE
			debug = False

			# Extract index of last column, which does not to be repeated
			lastColumn = len(self.columns) -1

			# Compose layout format by exploding all columns, even and odd, and the adding the (fixed) description field
			layout = ''.join([c + e.get(flip, debug) + o.get(flip, debug, oddRange if lastColumn - i else 1) for i,(c,e,o) in enumerate(self.columns)]) + '\x1b[m{}\x1b[m'
			return db[self.nodeName].dump(layout)

	def __init__(self):
		self.columns = []
		self.rows = []

	# Compose a row by computing all available columns
	def compose(self, node, verbose):

		def _color(i): return '\x1b[{}m'.format(31 + i % 6) # Helper function to set the color
		sIndex = 0 # Column of source node

		for i, c in enumerate(self.columns):

			# If this is my column
			if c.isSource(node): yield (_color(sIndex), EvenColumn.SOURCE, OddColumn.EMPTY)

			# Am I straight below the source?
			elif node.topName in c.parents:
				sIndex = i # This is the source column
				c.parentSeen(node) # Above us, the parent has seen one child
				yield (_color(sIndex), EvenColumn.RMERGE if c.parents else EvenColumn.LCORNER, OddColumn.LARROW)

			# We have no relation, but arrows may pass through this cell
			else: yield (_color(sIndex), EvenColumn.LARROW, OddColumn.LARROW) if i else (_color(sIndex), EvenColumn.PIPE, OddColumn.EMPTY)

# This grid is a straight line
class NoGrid(BaseGrid):

	class AnyColumn:
		def __init__(self):
			self.name = []

		# Accepting anyone
		def isSource(self, node): return True

	def __init__(self):
		super().__init__()
		self.columns.append(self.AnyColumn())

	def dealWith(self, node, verbose):
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, verbose)]))

	def done(self): return self.rows

# This grid is simple and dumb, it assigns a new column to each chain
class DumbGrid(BaseGrid):

	# Append new column for each node, immediately define its row
	def dealWith(self, node, verbose):
		self.columns.append(self.Column(node))
		self.rows.append(self.Row(node.topName, [e for e in self.compose(node, verbose)]))

	# No post-processing, just extend columns to the limit for alignment
	def done(self):
		s = len(self.columns)
		for r in self.rows: r.extend(s)
		return self.rows

# Return grid class by name
def getGrid(name):
	return {
			'no': NoGrid,
			'dumb': DumbGrid,
		}.get(name.lower(), NoGrid)

