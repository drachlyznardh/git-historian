
class Order:
	def __init__ (self):
		self.order = []

	def __bool__ (self):
		return True if self.order else False

	def push (self, arg):
		if arg: self.order = arg + self.order

	def pop (self):
		try: return self.order.pop(0)
		except: return None

def reduce_graphs(opt, heads, db):

	grid = []
	order = Order()

	order.push(heads)

	while order:
		name = order.pop()
		print('Visiting {}'.format(name))

def deploy(opt, heads, db):

	try:
		print(opt)
		print(heads)
		print(db)
	except BrokenPipeError: pass

	reduce_graphs(opt, heads, db)

	return 0

