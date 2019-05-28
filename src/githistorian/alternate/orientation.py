
def getOrientation(options):
	class Orientation:
		def __init__(self, highlight, flip):
			self.EMPTY   = '00' if highlight else '  '
			self.SOURCE  = '{}', '{}'
			self.LCORNER = '22' if highlight else '└┘┌┐'[flip] + ' ' # U+2514 2518 250c 2510
			self.RCORNER = '33' if highlight else '┘└┐┌'[flip] + ' ' # U+2518 2514 2510 250c
			self.LMERGE  = '44' if highlight else '┤├┤├'[flip] + '│' # U+251c 2524 251c 2524 2502
			self.RMERGE  = '55' if highlight else '├┤├┤'[flip] + '│' # U+251c 2524 251c 2524 2502
			self.PIPE    = '66' if highlight else '││││'[flip] + '│' # U+2502 2502 2502 2502 2502
			self.LARROW  = '77' if highlight else '←→←→'[flip] + ' '
			self.RARROW  = '88' if highlight else '→←→←'[flip] + ' '
			self.BROTHER = '99' if highlight else '┴┴┬┬'[flip] + '  ││'[flip] # U+2534 2534 252c 252c 2502
			self.HEAD    = 'aa' if highlight else '┯┯┷┷'[flip] + '││  '[flip] # U+252f 2537 252f 2537 2502 2502
			self.NODE    = 'bb' if highlight else '•│'                        # U+2022 2502
			self.ROOT    = 'cc' if highlight else '┷┷┯┯'[flip] + '  ││'[flip] # U+2537 252f 2537 252f 2502 2502

	return Orientation(options.highlight, 1 * options.hflip + 2 * options.vflip)

