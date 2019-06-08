
def getOrientation(options):
	class Orientation:
		def __init__(self, highlight, flip):
			self.EMPTY   = '000' if highlight else '   '
			self.SOURCE  = '{}', '{}', '{}'
			self.LCORNER = '222' if highlight else '┗┛┏┓'[flip] + ' 2' # U+2517 251b 250f 2513
			self.RCORNER = '333' if highlight else '┛┗┓┏'[flip] + ' 3' # U+251b 2517 2513 250f
			self.LMERGE  = '444' if highlight else '┫┣┫┣'[flip] + '┃4' # U+252b 2523 252b 2523 2503
			self.RMERGE  = '555' if highlight else '┣┫┣┫'[flip] + '┃┃' # U+2523 252b 2523 252b 2503 2503
			self.PIPE    = '666' if highlight else '┃┃┃┃'[flip] + '┃6' # U+2503 2503 2503 2503 2503
			self.LARROW  = '777' if highlight else '«»«»'[flip] + '  '
			self.RARROW  = '888' if highlight else '»«»«'[flip] + ' 8'
			self.BROTHER = '999' if highlight else '┻┻┳┳'[flip] + '  ┃┃'[flip] + '9' # U+253b 253b 2533 2533 2503 2503
			self.HEAD    = 'aaa' if highlight else '┳┳┻┻'[flip] + '┃┃  '[flip] + 'a' # U+2533 2533 253b 253b 2503 2503
			self.NODE    = 'bbb' if highlight else '•┃'                        + 'b' # U+2022 2503
			self.ROOT    = 'ccc' if highlight else '┻┻┳┳'[flip] + '  ┃┃'[flip] + 'c' # U+253b 253b 2537 252f 2503 2503

	return Orientation(options.highlight, 1 * options.hflip + 2 * options.vflip)

	'''
	self.LCORNER = '22' if highlight else '└┘┌┐'[flip] + ' ' # U+2514 2518 250c 2510
	self.RCORNER = '33' if highlight else '┘└┐┌'[flip] + ' ' # U+2518 2514 2510 250c
	self.LMERGE  = '44' if highlight else '┤├┤├'[flip] + '│' # U+2524 251c 2524 251c 2502
	self.RMERGE  = '55' if highlight else '├┤├┤'[flip] + '│' # U+251c 2524 251c 2524 2502
	self.PIPE    = '66' if highlight else '││││'[flip] + '│' # U+2502 2502 2502 2502 2502
	self.LARROW  = '77' if highlight else '←→←→'[flip] + ' '
	self.RARROW  = '88' if highlight else '→←→←'[flip] + ' '
	self.BROTHER = '99' if highlight else '┴┴┬┬'[flip] + '  ││'[flip] # U+2534 2534 252c 252c 2502
	self.HEAD    = 'aa' if highlight else '┯┯┷┷'[flip] + '││  '[flip] # U+252f 2537 252f 2537 2502 2502
	self.NODE    = 'bb' if highlight else '•│'                        # U+2022 2502
	self.ROOT    = 'cc' if highlight else '┷┷┯┯'[flip] + '  ││'[flip] # U+2537 252f 2537 252f 2502 2502
	'''

