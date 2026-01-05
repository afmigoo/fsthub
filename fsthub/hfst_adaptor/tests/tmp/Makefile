.DEFAULT_GOAL := ping.hfstol
ping.hfstol: ping.fst
	cat $< | hfst-txt2fst | hfst-fst2fst --optimized-lookup-unweighted -o $@_nometa
	hfst-edit-metadata \
						--add="foo=bar" \
						--add="Author=Jane Doe" \
						--add="Year=2000" \
						$@_nometa -o $@
	echo "ping" | hfst-lookup -q $@
