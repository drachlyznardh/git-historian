
test: test-simmetry

SIMMETRY_ARGS=-m1 --grid no
test-simmetry:
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS)     | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -H  | diff - simmetry-00.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -V  #| diff - simmetry-01.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -V  | diff - simmetry-01.ref
	cat m1-test-05.txt | $(NAME) $(SIMMETRY_ARGS) -VH | diff - simmetry-01.ref

