githistorian devel
==================

I'm trying to re-implement the thing from scratch, to make it simpler and
better, and possibly removing the dependency on bintrees (which was abandoned
and does not work on some platforms).

Invocation is already simpler as the package can be installed with pip and run
with
	$> githistorian

I know I want to support plenty of options in how you choose to display your
layout, so flipping it horizontally or vertically, even when commit messages
have multiple lines is a must.

Then I want you to be able to choose different grid behaviour. For this, I chose
to keep the same interface and try a few implementations of it, but I'm getting
stuck. I'm testing using input from files to run faster and consistent tests.

In the previous version, I remember having problems with straight chains of
multiple nodes, not knowning what was happening down the line form the top
element. I think I solved this by collapsing and reducing the graph to only
forking nodes, and each chain is essentially a multi-symbol, multi-line
super-commit which will belong to the same column no matter what.

Look-ups are still a problem, though… tests/m1-test-03.txt shows it, currently.
I know I want node 2 on the second row, but I cannot imagine a way to visit the
graph so that node 3 will be visited next. It is quite apparent that I cannot
just dump the graph line by line, even when reduced. I need a way to store rows
and columns independently, maybe…

I'm also thinking about writing down expected results given the input and the
specific combination of options, but that would a lot of work, especially if I
decide to change something down the line…

Maybe I should stick to the fundamentals are finalize a test-run for the
symmetry of the print and give a sincere attempt at simplifying the structure
once more, then tackle a different problem. I should be able to print a straight
line first.

