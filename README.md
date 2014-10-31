git-historian
=============

Alternative layout for git log --graph, inspired by
[this GIST thread](https://gist.github.com/datagrok/4221767).

Concept
-------

The long-term goal of this project is to provide an alternative layout for `git
log --graph`; the short-term goal is to display the history of a Git repo using
straight lines to represent long-lived branches. The user can specify how
branches are ordered, thus having specific branches on specific columns.

Proof of existence
------------------

This whole project exists only to prove that a different, more readable layout
for the graph of a repo is possible, and that I could actually write it. It is
now fairly functional, but vastly slower than invoking Git itself and it is a
standalone application.

Implementation
--------------

It is a Python script, which queries the Git repo for all its history (commit
relations) and crunches it to build a graph, then it spreads the commits on a
grid and dumps it all on the terminal.

### Vertical spread

Each line can contain but a single commit. No commit can be displayed before its
child(ren), and no commit can displayed after its parent(s); commit with no
relation at all (heads with completely independent chunks of history) appear in
order, as specified.

### Horizontal spread

Heads appear in order, as specified, or in alphabetical order by default.
Commits in the same branch appear in the same column as long as there is no
overlapping with arrows.

Relationship between commit may be:

 - implied, when parent and child are directly one over the other, in the same
   column and in two consecutive rows;
 - highlighted with a vertical line, when parent and cihld are directly one over
   the other, but with one or more row in between them;
 - highlighted with an arrow, which moves horizontally (left or right) from the
   parent until it reaches the child's column, bends at a right angle and moves
   up until it reaches the child

### Display

Each commit is displayed as a white bullet character '⬤' (\u2022). Arrows take
the color of their destination column and are drawn with unicode box chars.

As each merge commit receives all its incoming arrows from the bottom, there is
no indication of the original order of parents. You cannot infere which parent
was merged into which, as the relative row and column of each parent depends on
the whole layout.

At the end of its row, each commit is resented with its equivalent `git show -s
--pretty='<format>' ` output. You can specify the format string with options `-p,
--pretty`, otherwise my own default will be used instead.

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
