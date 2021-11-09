default: test

test:
	env AWS=echo ./pre-run.sh
	env AWS=echo ./post-run.sh COMPILER STATUS OUTPUT_PATH 0
