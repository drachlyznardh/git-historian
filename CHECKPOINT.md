CHECKPOINT for 0.0-a
====================

This file contains a TODO list and keeps track of progress.

 - I witnessed some cases of arrows being completely overwritten by other
   arrows, or commits; column inheritance has to take the number of parents into
   consideration, and act accordingly;
 - When branches cross-merge between fixed and dynamic columns, some are never
   assigned and get lost;
 - I definitely must add at least the commit message to the output;

## FOCUS: Independent heads

When multiple independet heads are present, some of them are not plotted at all;

## Done

Here's the list of registered progress.

 - My `less` does not support the `\U2b24` character, while `more` does. I guess
   I'll change that to something less obscure (?), like the `\2022` bullet;

### Vertical Padding

The day I'll have to display full messages, the graph will have to be padded in
order to span the number of lines required. That should be independent from the
single line for the target.

Layout is now separated in transition and padding. Computation and drawing are
also separated, so that each line can be computed once and invoked as many times
as needed.

