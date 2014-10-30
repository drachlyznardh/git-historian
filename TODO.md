# TODO

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
