
test: test-simmetry test-order

SIMMETRY_ARGS=-m1 --grid no
test-simmetry:
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS)     | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -H  | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -V  | diff - simmetry-01.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -VH | diff - simmetry-01.ref

ORDER_ARGS=-m1 --grid straight -vv
test-order:
	cat m1-test-00.txt | $(NAME) $(ORDER_ARGS) | diff - order-00.ref
	cat m1-test-01.txt | $(NAME) $(ORDER_ARGS) | diff - order-01.ref
	cat m1-test-02.txt | $(NAME) $(ORDER_ARGS) | diff - order-02.ref
	cat m1-test-03.txt | $(NAME) $(ORDER_ARGS) #| diff - order-03.ref
	cat m1-test-03.txt | $(NAME) $(ORDER_ARGS) | diff - order-03.ref
	cat m1-test-04.txt | $(NAME) $(ORDER_ARGS) | diff - order-04.ref
	cat m1-test-05.txt | $(NAME) $(ORDER_ARGS) | diff - order-05.ref

