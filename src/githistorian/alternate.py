
from .layout import Layout

def bind_children(opt, heads, db):

	order = [e for e in heads]

	while order:
		name = order.pop(0)
		print('Visiting {}'.format(name))
		commit = db.at(name)
		if commit.done: continue

		for i in commit.parent: db.at(i).add_child(name)

		order = db.skip_if_done(commit.parent) + order
		commit.done = 1

def reduce_graphs(opt, heads, db):

	grid = []
	counter = 0
	order = [e for e in heads]
	previous = None

	while order:
		name = order.pop(0)
		print('Reducing {}'.format(name))
		commit = db.at(name)
		if commit.done: continue

		for column in grid:
			if False: pass

		grid.append([name])
		commit.set_column(counter)
		commit.row = counter
		counter += 1

		order = db.skip_if_done(commit.parent) + order
		commit.done = 1

		if previous:
			previous.bottom = commit
			commit.top = previous
			previous.right = commit
			commit.left = previous
			print('{} above {}'.format(previous.name, commit.name))
		previous = commit

	print(grid)

# Given a complete grid, compute layout and print it, straight or flipped as
# requested by options
def _print_graph (history, first, width, hflip, vflip):

	t = Layout(width + 1, hflip, vflip)
	name = first
	bigblock = []

	while name:

		node = history.at(name)
		transition, padding = t.compute_layout(node)

		block = ['\x1b[m%s\x1b[m %s' % (transition, node.message[0])]
		for i in node.message[1:]: block.append('\x1b[m%s\x1b[m %s' % (padding, i))

		if vflip: bigblock.append('\n'.join(block))
		else: print('\n'.join(block))

		name = node.bottom

	if vflip:
		bigblock.reverse()
		print('\n'.join(bigblock))

def deploy(opt, heads, db):

	try:
		print(opt)
		print(heads)
		print(db)

		bind_children(opt, heads, db)
		db.clear()
		print('Children are bound')
		reduce_graphs(opt, heads, db)
		db.clear()
		print('Graph was reduced')

		_print_graph(db, heads[0], 20, opt.hflip, opt.vflip)

	except BrokenPipeError: pass
	return 0

