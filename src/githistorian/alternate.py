
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

def loadDB(lines):

	class SingleNode:
		def __init__(self, name, parents, text):
			self.name = name
			self.parents = parents if parents[0] else []
			self.children = []
			self.text = text

		def __str__(self):
			return 'SingleNode ({}) P({}) C({}) "{}"'.format(
				self.name, ', '.join(self.parents), ', '.join(self.children), self.text)

	def nodeFromLine(line):
		hashes, text = line.strip().split('#', 1)
		hashes = hashes.split(' ')
		return SingleNode(hashes[0], hashes[1:], text)

	db = {e.name:e for e in [nodeFromLine(e) for e in lines]}
	for e in db.values():
		for p in e.parents:
			db[p].children.append(e.name)

	return [e for e in db.values() if len(e.children) == 0], db

def reduceDB(heads, sdb, verbose):

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

	class Column:
		def __init__(self):
			self.occupiedBy = None
			self.waitingFor = set()

		def assign(self, node):
			self.occupiedBy = node
			self.waitingFor = set(node.children)

		def wasSeen(self, name):
			if name in self.waitingFor: self.waitingFor.remove(name)

		def get(self, index, node):
			if node is self.occupiedBy: return '\x1b[m{} '
			return '\x1b[{}m| '.format(31 + index % 7)

	def __init__(self):
		self.columns = [self.Column()]

	def assign(self, node):

		print('Checking node {}'.format(node))

		dealtWith = False
		state = 0 # Looking
		for c in self.columns: # Look for column where node belongs
			print('Checking column {}/{}'.format(c.occupiedBy, c.waitingFor))
			if state == 0: # Looking for waiting
				if node.topName in c.waitingFor:
					c.assign(node)
					state = 1 # Closing others
					continue
			elif state == 1: # Closing others
				c.wasSeen(node.name)

		print('No column is waiting for {}'.format(node.topName))
		if not dealtWith: # Node does not belong in any columns
			for c in self.columns:
				if not c.occupiedBy:
					c.assign(node)
					dealtWith = True

		print('No column is free for {}'.format(node.topName))
		if not dealtWith: # There are no free columns
			c = self.Column()
			c.assign(node)
			self.columns.append(c)

	def dealWith(self, node):

		self.assign(node)
		return '{}{}'.format(''.join(c.get(i, node) for i, c in enumerate(self.columns)), '\x1b[32m{}\x1b[m')

def fromStdin():
	import sys
	return sys.stdin.readlines()

def deploy():

	try:

		heads, db = loadDB(fromStdin())
		heads, db = reduceDB(heads, db, True)

		visit = Visit(heads)
		grid = Grid()
		while visit:
			e = visit.pop()
			layout = grid.dealWith(e)
			for s, t in e.getContent(): print(layout.format(s, t))
			visit.push([db[p] for p in e.parents])

	except BrokenPipeError: pass

	return 0

