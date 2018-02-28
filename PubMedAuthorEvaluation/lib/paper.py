#
# getPubMedID
#

def getPubMedID(paper):
	if "pmid" in paper:
			return paper["pmid"]
	elif "pmcid" in paper:
			return paper["pmcid"]
	else:
		return False


#
# getPubMedHyperlink
#

def getPubMedHyperlink(paper):
		### PUB ID LINK ###
		if "pmid" in paper:
			return '=HYPERLINK("http://europepmc.org/abstract/MED/' + paper["pmid"] + '"; "' + paper["pmid"] + '")'
		elif "pmcid" in paper:
			return '=HYPERLINK("http://europepmc.org/abstract/PMC/' + paper["pmcid"] + '"; "' + paper["pmcid"] + '")'


#
# getISSN
#
# Extracts and formats the ISSN of a given paper.
#
# parameters:
#     paper - inpout paper
#
# return: ISSN/false
#

def getISSN(paper):

	if paper.get("journalInfo", False):

		if paper.get("journalInfo").get("journal").get("issn"):
			return paper["journalInfo"]["journal"]["issn"].replace("-", "")

		#ESSN is the electronic ISSN, which is also OK
		if paper.get("journalInfo").get("journal").get("essn"):
			return paper["journalInfo"]["journal"]["essn"].replace("-", "")

	return False


#
# rateAuthorshipConfidence
#
# Since the authors names are very inconsistent we can never
# be sure if all publications are from our selected author.
# But certain criteria can help to be more sure about that fact.
# Criterias:
#     is the firstname in the author entry of the pub?
#     is the institution named in the affiliation?
#     is the city named in the affiliation?
#
# parameters:
#     paper - paper to rate
#
# return: confidence :: integer
#

def rateAuthorshipConfidence(paper, searchedAuthor):

	confidence = 0

	### NAME MATCH ###

	if "authorList" in paper and "author" in paper["authorList"]:

		# create array with all authors
		authors = paper["authorList"]["author"]

		for author in authors:
			if "firstName" in author and "fullName" in author:

				# first word of firstName -> first name of current author in author list
				firstname_authorAtPosition = author["firstName"].split(" ", 1)[0]

				# first word of original name (OUR LIST) -> firstname of author we want to check for
				firstname_searchedAuthor = searchedAuthor["Name"].split(" ", 1)[0]

				# first word of fullName -> lastname of author at current position
				lastname_authorAtPosition = author["fullName"].split(" ", 1)[0]

				# last word of original name (OUR LIST) -> lastname of author we search position for
				lastname_searchedAuthor = searchedAuthor["Name"].rsplit(None, 1)[-1]

				# compare both firstnames
				if firstname_authorAtPosition == firstname_searchedAuthor and lastname_authorAtPosition == lastname_searchedAuthor:
					#print("NAMES MATCHED!")
					confidence += 0.4
					break # exit for loop

	### END: NAME MATCH ###

	### AFFILIATION MATCHES ###

	if "affiliation" in paper:
		#print(paper["affiliation"])

		if "InstitutionList" in searchedAuthor and len(searchedAuthor["InstitutionList"]) > 1:

			institutions = searchedAuthor["InstitutionList"].split(', ')

			for institution in institutions:
				if institution.lower() in paper["affiliation"].lower():
					#print("MATCHED INSTITUTION")
					confidence += 0.3
					break # exit for loop


		if "LocationList" in searchedAuthor and len(searchedAuthor["LocationList"]) > 1:

			locations = searchedAuthor["LocationList"].split(', ')

			for location in locations:
				if location.lower() in paper["affiliation"].lower():
					#print("MATCHED LOCATION")
					confidence += 0.2
					break # exit for loop

	### END: AFFILIATION MATCHES ###

	return round(confidence, 2)


#
# paperInTopic
#

def checkTopic(pub_id, papers_topic):
	for paper in papers_topic:

		if "pmid" in paper:
			#print(paper["pmid"] + " - " + pub_id)
			if paper["pmid"] == pub_id:
				return True
		elif "pmcid" in paper:
			#print(paper["pmcid"] + " - " + pub_id)
			if paper["pmcid"] == pub_id:
				return True

	return False


#
# getAuthorPosition
#
# Only 3 options are important to us: first/middle/last.
# Takes the author list from the publication.
# Extracts first and last author.
# If lastname matches it's one of those.
# Else author was only named in middle.
#
# parameters:
#     paper - paper with complete ordered author list
#     searchedAuthor - author to check position for
#
# return: "first"/"middle"/"last"
#

def getAuthorPosition(paper, searchedAuthor):

	if "authorList" in paper and "author" in paper["authorList"]:
		# create array with first and last author
		authors = [paper["authorList"]["author"][0], paper["authorList"]["author"][-1]]

		for pos, author in enumerate(authors):
			if "fullName" in author:

				# first word of fullName -> lastname of author at current position
				lastname_authorAtPosition = author["fullName"].split(" ", 1)[0]

				# last word of original name (OUR LIST) -> lastname of author we search position for
				lastname_searchedAuthor = searchedAuthor["Name"].rsplit(None, 1)[-1]

				# compare both lastnames
				if lastname_authorAtPosition == lastname_searchedAuthor:
					# use "pos" to determin which array element was checked
					if pos == 0: 	return "first"
					else: 			return "last"

	# not first nor last -> middle position
	return "middle"


#
# getCoauthorCount
#

def getCoauthorCount(paper):
	# get amount of co-authors. (-1 cause of current author)
	if "authorList" in paper:
		return len(paper["authorList"]["author"]) - 1
	else:
		return 0


#
# checkLatestDate
#
# Compare two given dates, return the latest/newest
#
# parameters:
#     current - the currently latest date
#     date - date to compare woth current
#
# return: latest date
#

from datetime import datetime as dt

def checkLatestDate(current, date):
	if current == "0000-00-00": return date

	cur = dt.strptime(current, "%Y-%m-%d")
	new = dt.strptime(date, "%Y-%m-%d")

	# compare and return
	return date if new > cur else current
