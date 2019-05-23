
from .visit import getVisit
from .db import loadAndReduceDB
from .grid import getGrid, getOrientation

# Visit the graph and populate the grid
def unroll(gridClass, visitClass, heads, db, options, verbose):

	visit = visitClass(heads)
	grid = gridClass()

	while visit:
		e = visit.pop()
		grid.dealWith(e, verbose)
		visit.push([db[p] for p in e.parents])

	return grid.done(options.vflip)
	return reversed(rows) if options.vflip else rows

# Reading all lines from STDIN
def fromStdin():
	import sys
	while True:
		line = sys.stdin.readline()
		if not line: return
		yield line

# Creating and deploying graph, ignoring errors when output is cut off
def deploy(options):

	# visitClass = getVisit(options.visit)
	if ',' in options.visit:
		dbVisitClass, gridVisitClass = [getVisit(e) for e in options.visit.split(',')]
	else: dbVisitClass = gridVisitClass = getVisit(options.visit)

	heads, db = loadAndReduceDB(dbVisitClass, fromStdin(), options.verbose -4)
	gridClass = getGrid(options.grid)
	orientation = getOrientation(options.hflip, options.vflip)

	try:
		for row in unroll(gridClass, gridVisitClass, heads, db, options, options.verbose):
			print(row.dump(db, options.width, orientation, options.highlight))
	except BrokenPipeError: pass

	return 0

