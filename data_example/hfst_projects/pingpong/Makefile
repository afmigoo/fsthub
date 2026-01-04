.DEFAULT_GOAL := ping.hfstol
ping.hfstol: ping.fst
	cat $< | hfst-txt2fst | hfst-fst2fst --optimized-lookup-unweighted -o $@
	echo "ping" | hfst-lookup -q $@
