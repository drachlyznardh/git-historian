
test: test-simmetry test-order test-x

SIMMETRY_ARGS=-m1 --grid no
test-simmetry:
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS)     | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -H  | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -V  | diff - simmetry-01.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -VH | diff - simmetry-01.ref

ORDER_ARGS=-m1 --grid straight --visit reserve-pre,children-aware
test-order:
	cat m1-test-00.txt | $(NAME) $(ORDER_ARGS) | diff - order-00.ref
	cat m1-test-01.txt | $(NAME) $(ORDER_ARGS) | diff - order-01.ref
	cat m1-test-02.txt | $(NAME) $(ORDER_ARGS) | diff - order-02.ref
	cat m1-test-03.txt | $(NAME) $(ORDER_ARGS) | diff - order-03.ref
	cat m1-test-04.txt | $(NAME) $(ORDER_ARGS) | diff - order-04.ref
	cat m1-test-05.txt | $(NAME) $(ORDER_ARGS) | diff - order-05.ref
	cat m1-test-05.txt | $(NAME) $(ORDER_ARGS)     | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(ORDER_ARGS) -H  | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(ORDER_ARGS) -V  | diff - simmetry-01.ref
	cat m1-test-05.txt | $(NAME) $(ORDER_ARGS) -VH | diff - simmetry-01.ref

DUMB_ARGS=-m1 --grid dumb --visit reserve-pre,children-aware -w1 # --highlight
test-x:
	cat m1-test-00.txt | $(NAME) $(DUMB_ARGS) | diff - stairs-00.ref
	cat m1-test-01.txt | $(NAME) $(DUMB_ARGS) | diff - stairs-01.ref
	cat m1-test-02.txt | $(NAME) $(DUMB_ARGS) | diff - stairs-02.ref
	cat m1-test-03.txt | $(NAME) $(DUMB_ARGS) | diff - stairs-03.ref
	cat m1-test-04.txt | $(NAME) $(DUMB_ARGS) | diff - stairs-04.ref
	cat m1-test-05.txt | $(NAME) $(DUMB_ARGS) | diff - stairs-05.ref

