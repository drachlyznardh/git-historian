
class Node:
	def __init__(self, name, parents, text):
		self.name = name
		self.parents = parents if parents[0] else []
		self.children = []
		self.text = text

	def __str__(self):
		return '({}) P({}) C({}) "{}"'.format(self.name, ', '.join(self.parents), ', '.join(self.children), self.text)

	def getSymbol(self):
		if not self.parents: return '┷' # U+2537 Bottom root
		if not self.children: return '┯' # U+252f Top head
		return '•' # U+2022 Not a top

class Visit:
	def __init__(self, arg=None):
		self.order = arg if arg else []
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
	hashes, text = line.split('#', 1)
	hashes = hashes.split(' ')
	return Node(hashes[0], hashes[1:], text)

def loadDB():
	import sys

	db, head = {}, None

	while True:
		line = sys.stdin.readline().strip()
		if not line: break
		print(line)

		node = nodeFromLine(line)
		if not head: head = node
		db[node.name] = node

	for e in db.values():
		for p in e.parents:
			db[p].children.append(e.name)

	return head, db

def deploy():

	try:

		print()
		head, db = loadDB()
		print()
		for e in db.values(): print(e)
		print()
		visit = Visit([head])
		while visit:
			e = visit.pop()
			print('\x1b[31m| \x1b[m{} \x1b[32m{}'.format(e.getSymbol(), e.text))
			visit.push([db[p] for p in e.parents])
		print('\x1b[m')

	except BrokenPipeError: pass

	return 0

