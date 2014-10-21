# Headhunter module for Git-Historian

from subprocess import check_output
from subprocess import CalledProcessError
import re
import sys
import json

class HeadHunter:

	def __init__ (self, debug):

		self.head = []
		self.debug = debug

		self.name = []
		self.cname= []

	def hunt (self, args):

		self.load_configfile('.git-historian')
		self.load_args(args)

		print '(%s)' % ', '.join(self.name)

		return self.head

	def load_configfile (self, target_file):

		try: f = open(target_file, 'r')
		except IOError as e: return

		self.cname = json.load(f)

	def load_args (self, args):

		if len(args) == 0:
			self.name.extend(self.cname)
			return

		self.name.extend(args)
