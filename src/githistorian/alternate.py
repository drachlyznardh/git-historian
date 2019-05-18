
def deploy():

	try:

		import sys
		while True:
			line = sys.stdin.readline()
			if not line: break
			print(line)

	except BrokenPipeError: pass
	return 0

