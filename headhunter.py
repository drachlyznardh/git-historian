# Headhunter module for Git-Historian

from subprocess import check_output
from subprocess import CalledProcessError
import re
import sys

class HeadHunter:

	def __init__ (self, debug):

		self.head = []
		self.debug = debug

	def hunt (self, args):

		return self.head
