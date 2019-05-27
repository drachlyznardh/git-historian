
from .visit import getVisit
from .db import loadAndReduceDB
from .grid import getGrid
from .orientation import getOrientation

class Logger:
	def __init__(self, value, prefix=' ', step=' '):
		self.value = value
		self.prefix = prefix
		self.step = step

	def log(self, *args):
		if self.value > 0:
			from sys import stderr
			print(self.prefix + args[0].format(*args[1:]), file=stderr)

	def __sub__(self, value):
		return Logger(self.value - value, self.prefix + self.step * value, self.step)

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

	logger = Logger(options.verbose)
	heads, db = loadAndReduceDB(dbVisitClass, fromStdin(), logger -4)
	orientation = getOrientation(options)

	try:
		for row in getGrid(options.grid)().unroll(gridVisitClass, heads, db, orientation, options.vflip, Logger(options.verbose)):
			print(row.dump(db, options.width, orientation))
	except BrokenPipeError: pass

	return 0

