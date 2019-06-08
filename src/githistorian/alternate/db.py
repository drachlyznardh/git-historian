
# Loads a graph from given lines
def loadDB(lines, logger: int):

	# Build nodes from from given lines
	def nodesFromLines(lines, logger: int):

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

		node = None
		for line in lines:
			if not line: return

			# Lines starting with # mark new nodes
			if line[0] is '#':
				empty, hashes, text = line.strip().split('#', 2)
				hashes = hashes.split(' ')
				node = SingleNode(hashes[0], hashes[1:], text)
				logger.log('nodeFromLine({}, {}\x1b[m)', node, line.strip())
				yield node
				continue

			# Lines not starting with # are a continuation of previous nodes.
			# Line is appended to its description
			node.text.append(line.strip())
			logger.log('nodeFromLine({}, {}\x1b[m)', node, line.strip())

	# Build nodes from input lines
	db = {e.name: e for e in nodesFromLines(lines, logger)}

	# Bind children to their parent
	for e in db.values():
		for p in e.parents:
			db[p].children.append(e.name)

	# Nodes with no children are heads, return them along with the graph
	return [e for e in db.values() if len(e.children) == 0], db

# Reduce graph by collapsing chains of nodes into supernodes
def reduceDB(visitClass, heads, sdb, logger):

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

		# Given a layout line, dump the whole chain node-by-node, line-by-line.
		# Each node has a symbol for its first line and another for the
		# following lines. The first and last node in the chain may also be a
		# head or a root with dedicated symbols
		def dump(self, orientation, layout, logger):
			def _dump(layoutFirst, layoutFollowing, symbols, content, logger):
				# logger.log('Layout first {}', layout[0])
				first = layoutFirst.format('\x1b[m' + symbols[0], content[0])
				if len(content) == 1: return first
				# logger.log('Layout following {}', layout[1])
				return first + '\n' + '\n'.join([layoutFollowing.format(symbols[1], line) for line in content[1:]])

			if len(self.content) == 1:
				return _dump(layout[0], layout[1], orientation.HEAD if not self.children else orientation.ROOT if not self.parents else orientation.NODE, self.content[0], logger)

			return '\n'.join(
					[_dump(layout[0], layout[1], orientation.HEAD if not self.children else orientation.NODE, self.content[0], logger)] +
					[_dump(layout[2], layout[1], orientation.NODE, e, logger) for e in self.content[1:-1]] +
					[_dump(layout[2], layout[1], orientation.ROOT if not self.parents else orientation.NODE, self.content[-1], logger)]
				)

	# All heads are converted to MultiNodes are recorded in the new graph
	bigHeads = [MultiNode(e) for e in heads]
	mdb = {e.topName:e for e in bigHeads}

	visit = visitClass(heads, sdb, logger -2)
	while visit:
		e = visit.pop()
		if e in mdb: continue # This node may be a head from the initialization list
		logger.log('testing {}', e)

		# If this node belongs to a chain, absorb it
		if len(e.children) == 1 and len(mdb[e.children[0]].parents) == 1:
			oldKey, ref = mdb[e.children[0]].absorb(e)
			mdb[e.name] = ref
			logger.log('{} was absorbed by {}', e.name, mdb[e.children[0]])
			if oldKey: del mdb[oldKey]

		# Otherwise, create new dedicated node
		elif e.name not in mdb:
			s = MultiNode(e)
			mdb[e.name] = s
			logger.log('{} was promoted', e.name)

		else: logger.log('{} was preserved', e.name)

		# Pushing all parent to the visit, they will be filtered automatically
		visit.push([sdb[p] for p in e.parents])

	return bigHeads, mdb

# A bi-directional graph of simple nodes is loaded from the input lines, then
# it is reduced to a simpler graph where all straight chains of nodes are
# collected into multi-nodes
def loadAndReduceDB(visitClass, lines, logger):
	heads, db = loadDB(lines, logger)
	return reduceDB(visitClass, heads, db, logger)

