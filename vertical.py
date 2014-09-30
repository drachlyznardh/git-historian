# Vertical Order module for Git-Historian

class Order:
	def __init__ (self, first):
		self.stack = [[first]]

	def trim(self):
		while len(self.stack) > 0 and len(self.stack[0]) == 0:
			self.stack.pop(0)

	def get(self):
		self.trim()
		if len(self.stack) > 0 and len(self.stack[0]) > 0:
			return self.stack[0][0]
		return None

	def pop(self):
		self.trim()
		if len(self.stack) > 0 and len(self.stack[0]) > 0:
			return self.stack[0].pop(0)
		return None

	def push(self, value):
		if len(self.stack) > 0:
			self.stack[0].append(value)
		else:
			self.stack.append([value])
	
	def ppush(self, value):
		self.stack.insert(1, [value])

	def cpush(self, value):
		self.stack.insert(0, [value])

	def show(self):
		self.trim()
		message = ''
		for i in self.stack:
			if len(i):
				message += '\t[' + i[0][:7]
				for ii in i[1:]:
					message += ", " + ii[:7]
				message += ']\n'
		print "{\n%s}" % message

