
# Manages the visit of a graph, tracking nodes we need to visit (in order) and
# those we are already aware of
class Visit:

	# Costructor from initial set of nodes to visit, in the proper order
	def __init__(self, arg):
		self.order = [e for e in arg] # Deep copy of input list
		self.seen = set(self.order) # Won't be added again

	# Visit is valid until we run out of nodes to visit
	def __bool__(self):
		return len(self.order) > 0

	# Prepend nodes in reverse order
	def push(self, arg):
		if not arg: return # Skip empty list

		# Selecting only previously unseen nodes
		filtered = [e for e in reversed(arg) if e not in self.seen]
		self.order = filtered + self.order
		for e in filtered: self.seen.add(e) # Won't be added again

	# Pop the first node in the list
	def pop(self):
		return self.order.pop(0)

# Loads a graph from given lines
def loadDB(lines, verbose):

	# Helper class representing a single commit
	class SingleNode:
		def __init__(self, name, parents, text):
			self.name = name
			self.parents = parents if parents[0] else []
			self.children = []
			self.text = [text]

		def __str__(self):
			return 'SingleNode ({}) P({}) C({}) "{}\x1b[m"'.format(
				self.name, ', '.join(self.parents), ', '.join(self.children), self.text)

	def nodesFromLines(lines, verbose):

		node = None
		for line in lines:
			if verbose > 0: print('nodeFromLine({}, {}\x1b[m)'.format(node, line.strip()))

			# This line contains a new node
			if '#' in line:
				hashes, text = line.strip().split('#', 1)
				hashes = hashes.split(' ')
				node = SingleNode(hashes[0], hashes[1:], text)
				yield node
				continue

			# Append description to previous node
			node.text.append(line.strip())

	# Build a node from each line in input
	db = {e.name: e for e in nodesFromLines(lines, verbose)}

	# Bind children to their parent
	for e in db.values():
		for p in e.parents:
			db[p].children.append(e.name)

	# Nodes with no children are heads, return them along with the graph
	return [e for e in db.values() if len(e.children) == 0], db

# Reduce graph by collapsing chains of nodes into supernodes
def reduceDB(heads, sdb, verbose):

	# Helper class representing a straight chain of nodes
	class MultiNode:
		def __init__(self, node):
			self.topName = self.bottomName = node.name
			self.children = node.children
			self.parents = node.parents
			self.content = [node.text]

		def __str__(self):
			return 'MultiNode ({}) P({}) C({}) "{}\x1b[m"'.format(
				self.topName if self.topName == self.bottomName else '{}/{}'.format(self.topName, self.bottomName),
				', '.join(self.parents), ', '.join(self.children),
				'\x1b[m", "'.join([' \\n '.join(e) for e in self.content]) if len(self.content) > 1 else ''.join(self.content[0]))

		# Append a node at the end of the chain, updating boundaries
		def absorb(self, node):
			previousBottom = self.bottomName
			self.bottomName = node.name
			self.parents = node.parents
			self.content.append(node.text)

			# If the previous bottom node was not the only node in this chain,
			# it can be cleared from the keys. Returned along with a ref to
			# this chain for convenience
			return previousBottom if previousBottom != self.topName else None, self

		# Given a layout line, dump the whole chain node-by-node, line-by-line
		def dump(self, layout):
			def _dump(self, layout, symbols, content):
				first = layout.format('\x1b[m' + symbols[0], content[0])
				if len(content) == 1: return first
				return first + '\n' + '\n'.join([layout.format(symbols[1], line) for line in content[1:]])

			# U+252f 2502 2537 ' ' 2022 2502
			if len(self.content) == 1:
				return _dump(self, layout, ('┯', '│') if not self.children else ('┷', ' ') if not self.parents else ('•', '│'), self.content[0])

			# U+252f 2022 2022 U+2537 2022
			return '\n'.join(
					[_dump(self, layout, ('┯', '│') if not self.children else ('•', '│'), self.content[0])] +
					[_dump(self, layout, ('•', '│'), e) for e in self.content[1:-1]] +
					[_dump(self, layout, ('┷', ' ') if not self.parents else ('•', '│'), self.content[-1])]
				)

	# All heads are converted to MultiNodes are recorded in the new graph
	bigHeads = [MultiNode(e) for e in heads]
	mdb = {e.topName:e for e in bigHeads}

	visit = Visit(heads)
	while visit:
		e = visit.pop()
		if e in mdb: continue
		if verbose > 0: print('testing {}'.format(e))

		# If this node belongs to a chain, absorb it
		if len(e.children) == 1 and len(mdb[e.children[0]].parents) == 1:
			oldKey, ref = mdb[e.children[0]].absorb(e)
			mdb[e.name] = ref
			if verbose > 0: print('{} was absorbed by {}'.format(e.name, mdb[e.children[0]]))
			if oldKey: del mdb[oldKey]

		# Otherwise, create new dedicated node
		elif e.name not in mdb:
			s = MultiNode(e)
			mdb[e.name] = s
			if verbose > 0: print('{} was promoted'.format(e.name))

		elif verbose > 0: print('{} was preserved'.format(e.name))

		visit.push([sdb[p] for p in e.parents])

	return bigHeads, mdb

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

# Visit the graph and populate the grid
def unroll(grid, visit, heads, db, verbose):

	while visit:
		e = visit.pop()
		grid.dealWith(e, verbose)
		visit.push([db[p] for p in e.parents])

	return grid.done()

# Reading all lines from STDIN
def fromStdin():
	import sys
	return sys.stdin.readlines()

# Creating and deploying graph, ignoring errors when output is cut off
def deploy(options):

	try:

		heads, db = loadDB(fromStdin(), options.verbose -1)
		heads, db = reduceDB(heads, db, options.verbose -1)

		# visit = Visit(heads)
		# grid = Grid()
		# while visit:
		# 	e = visit.pop()
		# 	layout = grid.dealWith(e)
		# 	for s, t in e.getContent(): print(layout.format(s, t))
		# 	visit.push([db[p] for p in e.parents])

		# for row in unroll(DumbGrid(), Visit(heads), heads, db, verbose): print(row.dump(db, 2))
		for row in unroll(NoGrid(), Visit(heads), heads, db, options.verbose): print(row.dump(db, 2))

	except BrokenPipeError: pass

	return 0

