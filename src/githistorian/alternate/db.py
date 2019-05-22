
# Loads a graph from given lines
def loadDB(lines, verbose: int):

	# Helper class representing a single commit
	class SingleNode:
		def __init__(self, name, parents, text):
			self.name = name
			self.parents = parents if parents[0] else []
			self.children = []
			self.text = [text]

		def __str__(self):
			return 'SingleNode ({}) P({}) C({}) "{}\x1b[m"'.format(
				self.name, ', '.join(self.parents), ', '.join(self.children), self.text)

	def nodesFromLines(lines, verbose: int):

		count, node = 0, None
		for line in lines:
			if not line: return

			count += 1
			if verbose > 0: print('nodeFromLine({}, {}\x1b[m)'.format(node, line.strip()))

			# Lines starting with # mark new nodes
			if line[0] is '#':
				empty, hashes, text = line.strip().split('#', 2)
				if empty and verbose > 0: print('Fragment {} preceding # is not empty as expected on line {}'.format(empty, count))
				hashes = hashes.split(' ')
				node = SingleNode(hashes[0], hashes[1:], text)
				yield node
				continue

			# Lines not starting with # are a continuation of previous nodes.
			# Line is appended to its description
			node.text.append(line.strip())

	# Build nodes from input lines
	db = {e.name: e for e in nodesFromLines(lines, verbose)}

	# Bind children to their parent
	for e in db.values():
		for p in e.parents:
			db[p].children.append(e.name)

	# Nodes with no children are heads, return them along with the graph
	return [e for e in db.values() if len(e.children) == 0], db

# Reduce graph by collapsing chains of nodes into supernodes
def reduceDB(visitClass, heads, sdb, verbose):

	# Helper class representing a straight chain of nodes
	class MultiNode:
		def __init__(self, node):
			self.topName = self.bottomName = node.name
			self.children = node.children
			self.parents = node.parents
			self.content = [node.text]

		def __str__(self):
			return 'MultiNode ({}) P({}) C({}) "{}\x1b[m"'.format(
				self.topName if self.topName == self.bottomName else '{}/{}'.format(self.topName, self.bottomName),
				', '.join(self.parents), ', '.join(self.children),
				'\x1b[m", "'.join([' \\n '.join(e) for e in self.content]) if len(self.content) > 1 else ''.join(self.content[0]))

		# Append a node at the end of the chain, updating boundaries
		def absorb(self, node):
			previousBottom = self.bottomName
			self.bottomName = node.name
			self.parents = node.parents
			self.content.append(node.text)

			# If the previous bottom node was not the only node in this chain,
			# it can be cleared from the keys. Returned along with a ref to
			# this chain for convenience
			return previousBottom if previousBottom != self.topName else None, self

		# Given a layout line, dump the whole chain node-by-node, line-by-line
		def dump(self, layout):
			def _dump(self, layout, symbols, content):
				first = layout[0].format('\x1b[m' + symbols[0], content[0])
				if len(content) == 1: return first
				return first + '\n' + '\n'.join([layout[1].format(symbols[1], line) for line in content[1:]])

			# U+252f 2502 2537 ' ' 2022 2502
			if len(self.content) == 1:
				return _dump(self, layout, ('┯', '│') if not self.children else ('┷', ' ') if not self.parents else ('•', '│'), self.content[0])

			# U+252f 2022 2022 U+2537 2022
			return '\n'.join(
					[_dump(self, layout, ('┯', '│') if not self.children else ('•', '│'), self.content[0])] +
					[_dump(self, layout, ('•', '│'), e) for e in self.content[1:-1]] +
					[_dump(self, layout, ('┷', ' ') if not self.parents else ('•', '│'), self.content[-1])]
				)

	# All heads are converted to MultiNodes are recorded in the new graph
	bigHeads = [MultiNode(e) for e in heads]
	mdb = {e.topName:e for e in bigHeads}

	visit = visitClass(heads)
	while visit:
		e = visit.pop()
		if e in mdb: continue
		if verbose > 0: print('testing {}'.format(e))

		# If this node belongs to a chain, absorb it
		if len(e.children) == 1 and len(mdb[e.children[0]].parents) == 1:
			oldKey, ref = mdb[e.children[0]].absorb(e)
			mdb[e.name] = ref
			if verbose > 0: print('{} was absorbed by {}'.format(e.name, mdb[e.children[0]]))
			if oldKey: del mdb[oldKey]

		# Otherwise, create new dedicated node
		elif e.name not in mdb:
			s = MultiNode(e)
			mdb[e.name] = s
			if verbose > 0: print('{} was promoted'.format(e.name))

		elif verbose > 0: print('{} was preserved'.format(e.name))

		visit.push([sdb[p] for p in e.parents])

	return bigHeads, mdb

def loadAndReduceDB(visitClass, lines, verbose):
	heads, db = loadDB(lines, verbose)
	return reduceDB(visitClass, heads, db, verbose)

