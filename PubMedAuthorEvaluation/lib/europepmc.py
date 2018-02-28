import json, requests

#TODO: as class
#TODO: move build query strings here

#
# search
#
# Searches PubMed Database (via EuropePMC) for a certain query.
# Adds restrictions to only Med or PMC articles.
#
# parameters:
#     query - the user specified query
#     resulttype - idlist/lite/core
#
# return: json formated API results
#

def search(query, resulttype):
	url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search'

	params = dict(
		query = query + ' (SRC:med OR SRC:pmc) (PUB_TYPE:"Journal Article" OR PUB_TYPE:"article-commentary" OR PUB_TYPE:"research-article" OR PUB_TYPE:"protocol" OR PUB_TYPE:"rapid-communication" OR PUB_TYPE:"product-review")',
		pageSize = '1000',
		format = 'json',
		sort = 'CITED desc',
		resulttype = resulttype
	)

	response = requests.get(url = url, params = params)

	# check if response is OK
	if response.status_code == 200:
		json_data = json.loads(response.text)
		if "hitCount" in json_data:
			return json_data

	# else retry via recursion
	print("retry search...")
	return search(query, resulttype)


#
# main function
#
# This file is not meant to be executed sole, but can be for debugging purpose.
#

if __name__ == '__main__':

	papers = search('(AUTH:"John")')["resultList"]["result"]

	for i, paper in enumerate(papers):

		print(paper["pmid"])

		print(paper["citedByCount"])

		#print("{:d}) {:s} - {:d} citations".format(i+1, paper["MedlineCitation"]["Article"]["ArticleTitle"], cite_count))
