#
# hIndex
#
# Calculate hIndex via citations
#
# parameters:
#     citations - array of citations. e.g. [25, 12, 0, 13, 10]
#
# return: hIndex
#

def hIndex(citations):

	n = len(citations)
	citeCount = [0] * (n+1)

	for c in citations:
		if c >= n:
			citeCount[n] += 1
		else:
			citeCount[c] += 1

	i = n-1

	while i >= 0:
		citeCount[i] += citeCount[i+1]
		if citeCount[i+1] >= i+1:
			return i+1
		i -= 1

	return 0


#
# gIndex
#
# Calculate gIndex via citations
#
# parameters:
#     citations - array of citations. e.g. [25, 12, 0, 13, 10]
#
# return: gIndex
#
# Copyright: Guido Governatori, http://www.governatori.net/gindex.rb
#

def gIndex(citations):

	gindex = 0
	hindex = 0
	citation_count = 0

	for c in citations:

		gindex += 1
		citation_count = citation_count + c

		#if hindex == 0 and c < gindex:
		#	hindex = gindex - 1

		if citation_count < (gindex * gindex):
			gindex = gindex - 1
			break # found gindex, end loop

	return gindex
