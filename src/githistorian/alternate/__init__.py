
from .visit import getVisit
from .db import loadAndReduceDB
from .grid import getGrid
from .orientation import getOrientation

# Reading all lines from STDIN
def fromStdin():
	import sys
	while True:
		line = sys.stdin.readline()
		if not line: return
		yield line

# Creating and deploying graph, ignoring errors when output is cut off
def deploy(options):

	if ',' in options.visit:
		dbVisitClass, gridVisitClass = [getVisit(e) for e in options.visit.split(',')]
	else: dbVisitClass = gridVisitClass = getVisit(options.visit)

	heads, db = loadAndReduceDB(dbVisitClass, fromStdin(), options.verbose -4)
	orientation = getOrientation(options)

	try:
		for row in getGrid(options.grid)().unroll(gridVisitClass, heads, db, orientation, options.vflip, options.verbose):
			print(row.dump(db, options.width, orientation))
	except BrokenPipeError: pass

	return 0

