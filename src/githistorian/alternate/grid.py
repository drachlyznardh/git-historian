
from enum import Enum

# NONE  = 0 # No flip, top to bottom, left to right
# HFLIP = 1 # Horizontal flip, top to bottom, right to left
# VFLIP = 2 # Vertical flip, bottom to top, left to right
# BOTH  = 3 # Both flips, bottom to top, right to left
def getOrientation(horizontalFlip, verticalFlip): return 1 * horizontalFlip + 2 * verticalFlip

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

	# Select symbols according to flip status, return one for the first line
	# and another for the following line. When debugging, dump the enum value
	def get(self, flip:int, debug:int):
		if debug: return ['{}'.format(self.value) for e in range(2)]
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
			}[self][flip], '││││'[flip]

# Helper class for odd, repeatble columns holding only arrows
class OddColumn(Enum):
	EMPTY   = 0 # Column is empty
	LARROW  = 1 # Arrow towards target's column from yet unseen source node
	RARROW  = 2 # Arrow towards target's column from already seen source node

	# Select symbols according to flip status, return one for the first line
	# and another for the following line. When debugging, dump the enum value
	def _get(self, flip:int, debug:int):
		if debug: return ['{}'.format(self.value) for e in range(2)]
		return {
				OddColumn.EMPTY  : '    ',
				OddColumn.LARROW : '←→←→',
				OddColumn.RARROW : '→←→←',
			}[self][flip], ' '

	# Odd columns are repeatable, so we get the symbol once and then repeat it
	def get(self, flip:int, debug:int, counter:int):
		symbol = self._get(flip, debug)
		if counter == 1: return symbol
		return [e * counter for e in symbol]
		return symbol[0] * counter, symbol[1] * counter
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

		# TODO please describe what is happening down there, it's scary!
		def dump(self, db, width, flip, debug):

			# Extract index of last column, which does not to be repeated
			lastColumn = len(self.columns) -1

			# Compose layout format by exploding all columns, even and odd, and the adding the (fixed) description field
			# print([(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)])
			# print([(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)]])
			print([e for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)]])])
			layout = ['{}{}'.format(e[0], '\x1b[m{}\x1b[m') for e in zip(*[(c + e1 + o1, c + e2 + o2) for c, (e1, e2), (o1, o2) in [(c, e.get(flip, debug), o.get(flip, debug, width if lastColumn - i else 1)) for i,(c,e,o) in enumerate(self.columns)]])]
			# layout = ''.join([c + e.get(flip, debug) + o.get(flip, debug, width if lastColumn - i else 1) for i,(c,e,o) in enumerate(self.columns)]) + '\x1b[m{}\x1b[m'
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

