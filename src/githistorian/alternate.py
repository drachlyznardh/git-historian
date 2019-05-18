
class SingleNode:
	def __init__(self, name, parents, text):
		self.name = name
		self.parents = parents if parents[0] else []
		self.children = []
		self.text = text

	def __str__(self):
		return 'SingleNode ({}) P({}) C({}) "{}"'.format(self.name, ', '.join(self.parents), ', '.join(self.children), self.text)

	def getSymbol(self):
		if not self.parents: return '┷' # U+2537 Bottom root
		if not self.children: return '┯' # U+252f Top head
		return '•' # U+2022 Not a top

class MultiNode:
	def __init__(self, node):
		self.topName = self.bottomName = node.name
		self.children = node.children
		self.parents = node.parents
		self.content = [node.text]

	def __str__(self):
		return 'MultiNode ({}) P({}) C({}) "{}"'.format(
			self.topName if self.topName == self.bottomName else '{}/{}'.format(self.topName, self.bottomName),
			', '.join(self.parents), ', '.join(self.children),
			'", "'.join(self.content) if len(self.content) > 1 else self.content[0])

	def getContent(self):
		content = [['•', e] for e in self.content] # U+2022 Common node
		if not self.parents: content[-1][0] = '┷' # U+2537 Bottom root
		if not self.children: content[0][0] = '┯' # U+252f Top head
		return content

	def absorb(self, node):
		previousBottom = self.bottomName
		self.bottomName = node.name
		self.parents = node.parents
		self.content.append(node.text)
		return previousBottom if previousBottom != self.topName else None, self

class Visit:
	def __init__(self, arg=None):
		self.order = [e for e in arg] if arg else []
		self.seen = set()
		for e in self.order: self.seen.add(e)

	def __bool__(self):
		return len(self.order) > 0

	def push(self, arg):
		if not arg: return
		filtered = [e for e in reversed(arg) if e not in self.seen]
		self.order = filtered + self.order
		for e in filtered: self.seen.add(e)

	def pop(self):
		return self.order.pop(0)

def nodeFromLine(line):
	hashes, text = line.strip().split('#', 1)
	hashes = hashes.split(' ')
	return SingleNode(hashes[0], hashes[1:], text)

def loadDB():
	import sys

	db = {e.name:e for e in [nodeFromLine(e) for e in sys.stdin.readlines()]}

	for e in db.values():
		for p in e.parents:
			db[p].children.append(e.name)

	return [e for e in db.values() if len(e.children) == 0], db

def reduceDB(heads, sdb, verbose):

	bigHeads, mdb = [MultiNode(e) for e in heads], {}
	for e in bigHeads:
		if e.topName not in mdb: mdb[e.topName] = e
		if e.bottomName not in mdb: mdb[e.bottomName] = e

	visit = Visit(heads)
	while visit:
		e = visit.pop()
		if e in mdb: continue
		if verbose: print('testing {}'.format(e))

		# If this node belongs to a chain
		if len(e.children) == 1 and len(mdb[e.children[0]].parents) == 1:
			oldKey, ref = mdb[e.children[0]].absorb(e)
			mdb[e.name] = ref
			if verbose: print('{} was absorbed by {}'.format(e.name, mdb[e.children[0]]))
			if oldKey: del mdb[oldKey]

		# Create new node
		elif e.name not in mdb:
			s = MultiNode(e)
			mdb[e.name] = s
			if verbose: print('{} was promoted'.format(e.name))

		elif verbose: print('{} was preserved'.format(e.name))

		visit.push([sdb[p] for p in e.parents])

	return bigHeads, mdb

class Grid:
	def __init__(self):
		self.columns = []

	def dealWith(self, chain):
		return '\x1b[31m| \x1b[m{} \x1b[32m{}'

def deploy():

	try:

		heads, db = loadDB()
		heads, db = reduceDB(heads, db, True)

		print('\x1b[m')
		visit = Visit(heads)
		grid = Grid()
		while visit:
			e = visit.pop()
			layout = grid.dealWith(e)
			for s, t in e.getContent():
				print(layout.format(s, t))
			visit.push([db[p] for p in e.parents])
		print('\x1b[m')

	except BrokenPipeError: pass

	return 0

	try:

		print()
		heads, db = loadDB()
		print()
		for e in db.values(): print(e)
		print()
		visit = Visit(heads)
		while visit:
			e = visit.pop()
			print('\x1b[31m| \x1b[m{} \x1b[32m{}'.format(e.getSymbol(), e.text))
			visit.push([db[p] for p in e.parents])
		print('\x1b[m')

		heads, db = reduceDB(heads, db, True)
		print()
		print('Reduced heads: {}'.format(heads))
		print('Reduced DB: {}'.format(db))
		print()

		visit = Visit(heads)
		while visit:
			e = visit.pop()
			# print('2nd Visit of {}'.format(e))
			for s, t in e.getContent():
				print('\x1b[31m| \x1b[m{} \x1b[32m{}'.format(s, t))
			visit.push([db[p] for p in e.parents])
		print('\x1b[m')

	except BrokenPipeError: pass

	return 0

