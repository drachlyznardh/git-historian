git-historian
=============

Alternative layout for git log --graph, inspired by
https://gist.github.com/datagrok/4221767

Concept
-------

The goal of this project is to display the history of a Git repo focusing on
long-lived parallel branches. In order to be more human-readable, branches are
displayed as vertical sequences of commits as long as there are no forks and no
merges, which can both cause a switch of tracks from column to column. Plus, as
a branch starts, it books its column, so that it can grow on a straight line
without the risk of being pushed right by other branches, as it happens normally
in Git.

There is also a static priority assignement which allows tagged commits to
appear in specific columns, so that commit of great importance can sink to the
left.

Proof of existence
------------------

This whole project exists only to prove that a different, more readable layout
for the graph of a repo is possible, and that I could actually write it. It is
incomplete, vastly inefficient and completely outside Git.

Implementation
--------------

It is a Python script, which queries the git repo for all its history (commit
relations) and crunches it to build a graph, then it spreads the commits on a
grid and dumps it.

### Vertical spread

Each line can contain but a single commit. No commit can be displayed before its
child(ren), and no commit can displayed after its parent(s); commit with no
relation at all (heads with completely independent history) should appear in
order.

This is computed by walking the graph iteratively. Each commit holds until all
its children are in order, and then it calls its parents.

### Horizontal spread

Branches should occupy the same column, as long as they are but a sequence of
commits. Plus, tagged commits which matches the criteria are moved to a specific
column.

As rules of thumb, it should work more or less like this:

 - commits with matching tags go to assigned column;
 - lone parents belong to the same line as their child;
 - parents of a same commit, as also children of a same commit, must belong each
   to a different column;
 - no commit can belong to the column of another active branch

This is computed in order, top-to-bottom, by tracking active branches and
available columns. Merge commits spread their parents on available columns, if
any; more columns are added whenever necessary. Commit with multiple children
collect the branches they close, which columns become available. Columns may
remain available indefinitely, but are never destroyed.

Many different small tweaks (and bugs, most probably) affect this behaviour and
the final layout. This is mostly due to personal taste, instead to rules; I did
what I did out of hope, to enhance readability.

### Display

Each commit is displayed as a white, very big bullet character '⬤' (\U2b24) is
its assigned column. Fork and merge relations are displayed with arrows, which
move on vertical straight lines until they reach the target row, then bend by 90
degrees and move horizontally until they touch the target commit. Each arrow
gets it color from its source's column and keeps it until the end.

All arrows start from the father and point towards the child. The parent order
is not preserved, so you cannot longer assume that the leftmost arrows comes
from the first parent, as you can do with the usual `git log --graph` layout.

Closer arrows (those with less horizontal gap from the respective target) take
precedence over other arrows.

At the end of its row, each commit is marked by its short hash (7 characters) in
white, padded by the whole graph's width, and by its refs, if any, in bold
green.

Testing
-------

For testing, I used a bunch of repos. First, this one; in addition, I built a
series of artificial repos with different histories, to check the behaviour with
octopus merges, crossing branches, multiple heads, multiple bases, a copy of the
git-flow sample image.

I tested it against some other projects of mine, and also against the Git repo
itself: I got 37k lines and 410 columns after a wait of ~3 minutes, but it
worked.

TODO
====

First of all, cmdline options: everything is currently hard coded.

**Display options**: the layout could be mirrored both vertically and horizontally,
the charset could be different (for those terminals / fonts without full unicode
support), colors could be optional, there could be more colors (with fade and
bold modes, or with full 256 color if supported), user-defined display message
for commits (the `--pretty="<format>"` option), map-only display mode could
ignore any non-merge / non-fork commit…
