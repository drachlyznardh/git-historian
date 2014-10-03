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
