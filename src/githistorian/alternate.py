
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

def deploy(opt, heads, db):

	try:
		print(opt)
		print(heads)
		print(db)
	except BrokenPipeError: pass

	bind_children(opt, heads, db)
	print('Children are bound')
	reduce_graphs(opt, heads, db)
	print('Graph was reduced')

	return 0

