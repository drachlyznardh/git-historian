
class Node:
	def __init__(self, name, parents, text):
		self.name = name
		self.parents = parents if parents[0] else []
		self.text = text

	def __str__(self):
		return '({}) ({}) "{}"'.format(self.name, ', '.join(self.parents), self.text)

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

	return db

def deploy():

	try:

		print()
		db = loadDB()
		print()
		for e in db.values(): print(e)
		print()

	except BrokenPipeError: pass

	return 0

