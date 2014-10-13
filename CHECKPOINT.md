CHECKPOINT for 0.0-a
====================

Obstacles were met. The design was revised. Now collecting a bunch of failed
attempts, since most of them contain improvements in debug messages, option
parsing and stuff.

# Including from branch:extreme

This file contains a TODO list and keeps track of progress.

 - Line booking does not always work as expected. I'll be rewriting that entire
   section, using agressive push by previous parents;

## Done

Here's the list of registered progress.

 - When branches cross-merge between fixed and dynamic columns, some are never
   assigned and get lost;

 - I witnessed some cases of arrows being completely overwritten by other
   arrows, or commits; column inheritance has to take the number of parents into
   consideration, and act accordingly;

   This is due to the ordering of commits: relative position can lead to arrows
   begin obscured by some other parts of the history. Layout of arrows must be
   mirrored.

 - My `less` does not support the `\U2b24` character, while `more` does. I guess
   I'll change that to something less obscure (?), like the `\2022` bullet;
 - I definitely must add at least the commit message to the output;
 - When multiple independet heads are present, some of them are not plotted at
   all;

### Vertical Padding

The day I'll have to display full messages, the graph will have to be padded in
order to span the number of lines required. That should be independent from the
single line for the target.

Layout is now separated in transition and padding. Computation and drawing are
also separated, so that each line can be computed once and invoked as many times
as needed.

--------------------------------------------------------------------------------

Nothing will be lost, until next release.
