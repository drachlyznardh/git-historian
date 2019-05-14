
if __name__ == '__main__':

	import sys
	from .githistorian import tell_the_story

	sys.exit(tell_the_story(sys.argv[1:]))

