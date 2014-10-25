# TODO

- each node should find itself already assigned by it first child, unless it is
  a head; each node should then invoke its parent and assign their column; the
  order of invocation should be reverse vertical, from lower to upper; this
  makes it necessary that each node knows it relative row; I could use a
  monotonic value;

- simpler everything; working, but simple;
- *Virtual nodes*, which could act as placeholders; plus, it could be somehow
  useful to have an artificial global head node and a global sink; not sure how
  to deal with multiple disconnected histories (should I even bother?);
- *Layers*: brothers could live inside the same layer, and so could cousins; it
  may be easier to align them by layer than by actual vertical order;

# DONE

- defaulting to HEAD when no argument is given;
- detect and show layout errors whenever an arrow is overwritten by a commit,
  should be a big [30;41mX;
