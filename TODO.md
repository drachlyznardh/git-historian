# TODO

- invoke `git rev-list` instead of `git log`; allow all the options to pass to
  the request;
- use right-to-left canonical order for row assignment;
- implement own binary search, to avoid the insert-search-delete process;
- include padding and mirroring options for graph layout;

# DONE

- each node should find itself already assigned by it first child, unless it is
  a head; each node should then invoke its parent and assign their column; the
  order of invocation should be reverse vertical, from lower to upper; this
  makes it necessary that each node knows it relative row; I could use a
  monotonic value;
- simpler everything; working, but simple;
- defaulting to HEAD when no argument is given;
- detect and show layout errors whenever an arrow is overwritten by a commit,
  should be a big [30;41mX;
