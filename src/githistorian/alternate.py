
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

def nodeFromLine(line):
	hashes, text = line.split('#', 1)
	hashes = hashes.split(' ')
	return Node(hashes[0], hashes[1:], text)

def loadDB():
	import sys

	db = {}

	while True:
		line = sys.stdin.readline().strip()
		if not line: break
		print(line)

		node = nodeFromLine(line)
		db[node.name] = node

	for e in db.values():
		for p in e.parents:
			db[p].children.append(e.name)

	return db

def deploy():

	try:

		print()
		db = loadDB()
		print()
		for e in db.values(): print(e)
		print()
		for e in db.values(): print('\x1b[31m| \x1b[m{} \x1b[32m{}'.format(e.getSymbol(), e.text))
		print('\x1b[m')

	except BrokenPipeError: pass

	return 0

