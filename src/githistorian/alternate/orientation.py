
from enum import Enum

class CellState(Enum):
	EMPTY   = 0 # Column is empty with no arrow
	SOURCE  = 1 # Column holds the current commit
	LCORNER = 2 # Left corner, arrow bending up from yet unseen source node
	RCORNER = 3 # Right corner, arrow bending up from already seen source node
	LMERGE  = 4 # Left merge, arrow joining from yet unseen source node
	RMERGE  = 5 # Right merge, arrow joining from already seen source node
	PIPE    = 6 # Straight line
	LARROW  = 7 # Arrow towards target's column from yet unseen source node
	RARROW  = 8 # Arrow towards target's column from already seen source node

class Orientation:
	def __init__(self, highlight, flip):
		self.EMPTY   = '00' if highlight else '  '
		self.SOURCE  = '11' if highlight else ('{}', '{}')
		self.LCORNER = '22' if highlight else '└┘┌┐'[flip] + ' ' # U+2514 2518 250c 2510
		self.RCORNER = '33' if highlight else '┘└┐┌'[flip] + ' ' # U+2518 2514 2510 250c
		self.LMERGE  = '44' if highlight else '┤├┤├'[flip] + '│' # U+251c 2524 251c 2524
		self.RMERGE  = '55' if highlight else '├┤├┤'[flip] + '│' # U+251c 2524 251c 2524
		self.PIPE    = '66' if highlight else '││││'[flip] + '│' # U+2502 2502 2502 2502
		self.LARROW  = '77' if highlight else '←→←→'[flip] + ' '
		self.RARROW  = '88' if highlight else '→←→←'[flip] + ' '

# NONE  = 0 # No flip, top to bottom, left to right
# HFLIP = 1 # Horizontal flip, top to bottom, right to left
# VFLIP = 2 # Vertical flip, bottom to top, left to right
# BOTH  = 3 # Both flips, bottom to top, right to left
def getOrientation(options): #horizontalFlip, verticalFlip):
	return Orientation(options.highlight, 1 * options.hflip + 2 * options.vflip)
	return 1 * horizontalFlip + 2 * verticalFlip

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
			}[self][flip], '{}' if self is EvenColumn.SOURCE else '│'

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

