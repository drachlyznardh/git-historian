
# Visit the graph and populate the grid
def unroll(gridClass, visitClass, heads, db, verbose):

	visit = visitClass(heads)
	grid = gridClass()

	while visit:
		e = visit.pop()
		grid.dealWith(e, verbose)
		visit.push([db[p] for p in e.parents])

	return grid.done()

# Reading all lines from STDIN
def fromStdin():
	import sys
	while True:
		line = sys.stdin.readline()
		if not line: return
		yield line

from .visit import getVisit
from .db import loadAndReduceDB
from .grid import getGrid

# Creating and deploying graph, ignoring errors when output is cut off
def deploy(options):

	visitClass = getVisit('reverse')
	heads, db = loadAndReduceDB(visitClass, fromStdin(), options.verbose -2)
	gridClass = getGrid('no')

	try:
		for row in unroll(gridClass, visitClass, heads, db, options.verbose): print(row.dump(db, 2))
	except BrokenPipeError: pass

	return 0

