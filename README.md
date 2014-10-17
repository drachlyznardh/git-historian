git-historian
=============

Alternative layout for git log --graph, inspired by
[this GIST thread](https://gist.github.com/datagrok/4221767).

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
grid and dumps it all on the terminal.

### Vertical spread

Each line can contain but a single commit. No commit can be displayed before its
child(ren), and no commit can displayed after its parent(s); commit with no
relation at all (heads with completely independent history) should appear in
order.

### Horizontal spread

Branches should occupy the same column, as long as they are but a sequence of
commits. Heads should appear in order, as specified by cmdline args or
alphabetically, unless they are related.

As rules of thumb, it should work more or less like this:

 - lone parents belong to the same line as their child;
 - parents of a same commit, as also children of a same commit, must belong each
   to a different column;
 - no commit can belong to the column of another active branch

This is computed while walking the graph, starting from the first head and
moving down or up following a commit's parents and children, in a sort of
leftmost-first visit. Each visited commit takes the first available column,
which could contain one of the commit's parents or children, but no arrows.

### Display

Each commit is displayed as a bullet character '⬤' (\u2022).

Fork and merge relations are displayed with arrows, which move on horizontal
straight lines until they reach the target column, then bend by 90 degrees and
move straight up until they touch the target commit. Each arrow gets it color
from its destination column and keeps it until the end.

All arrows start from the father and point towards the child. The parent order
is not preserved, so you cannot longer assume that the leftmost arrows comes
from the first parent, as you can do with the usual `git log --graph` layout.

Closer arrows (those with less horizontal gap from the respective target) take
precedence over other arrows. This affects the color, not the direction.

At the end of its row, each commit is resented with its `git show --pretty`
output.

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

First of all, **Options**: everything is currently hard coded.

**Display options**: the layout could be mirrored both vertically and horizontally,
the charset could be different (for those terminals / fonts without full unicode
support), colors could be optional, there could be more colors (with fade and
bold modes, or with full 256 color if supported), user-defined display message
for commits (the `--pretty="<format>"` option), map-only display mode could
ignore any non-merge / non-fork commit…

**Efficency**: there are no intermediate steps in the layout computation, no
checkpoints, no nothing. Even with no change in the repo, each invocation must
read the whole history, rebuild the graph and recompute the column for each
commit. I am not sure how I could keep the graph in memory (or on file) and add
a single commit (or arrow) to it without starting from scratch.

**Standalone**: there is no integration with Git, for a number of reasons.

 - Git integration is hard. I have been using Git for years, but I have no
   experience with its source, its internal structure and its community. I took
   a look at the graph's sourcecode and then I ran away;
 - I don't know what I want, nor what people would like; the GIST thread I
   mentioned as inspiration gave me some ideas, but many more details need to be
   established before the project “gets serious”;
 - the resulting layout takes a very wide space to display, much more than the
   default Git graph; this whole project may be nearly-unusable on repos with
   very long histories, or with a great deal of open branches;
