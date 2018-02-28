from unidecode import unidecode

import re

def getAuthors(publication):

	authors = []
	investigators = []

	if publication.get("authorList") != None:
		if publication.get("authorList").get("author") != None:

			authors = publication.get("authorList").get("author")

	if publication.get("investigatorList") != None:
		if publication.get("investigatorList").get("investigator") != None:
			investigators = publication.get("investigatorList").get("investigator")

	mergedlist = list(authors + investigators)

	# no investigatorList? -> return normal list
	return mergedlist


def uniform(string):

	#TODO: sub \b[a-z]{1,2}\b|\b[a-z]

	string = unidecode(string)
	append = ""

	if (string.count(" ") >= 2 and string.endswith("Jr")):
		string = string[:-3]
		append = " Jr"

	string = string.lower()
	string = re.sub(r"\b([a-z]{1,2})\b|\b([a-z])", lambda m: m.group().upper(), string)

	return string + append


#
# main function
#
# This file is not meant to be executed sole, but can be for debugging purpose.
#

if __name__ == "__main__":
	print(uniform("birgit c. schlick-steiner"))
	print(uniform("schlick-steiner bc"))
	print(uniform("florian m. steiner"))
