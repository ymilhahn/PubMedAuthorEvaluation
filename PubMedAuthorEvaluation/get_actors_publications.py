import os
import sys
import csv

import lib.paper as paper
import lib.topics as topics
import lib.journal as journal
import lib.europepmc as europepmc

from lib.uprint import *

# root path of INPUT and OUTPUT folders
DATA_PATH = "../"

#
# getAuthorSearchString
#
def getAuthorSearchString(author):
	if "AUTH:" in author["PubMedSearch"]:
		# search string is complete, no need for concat
		return author["PubMedSearch"]
	else:
		# build search query string via author name
		return '(AUTH:"' + author["PubMedSearch"] + '")'

#
# getAuthorORCIDSearchString
#
def getAuthorORCIDSearchString(author):
	# build search query string via author ORCID
	return '(AUTHORID:"' + author["ORCID"] + '")'

#
# getAuthorsPublications
#
# Gets author list for specified topic.
# Loops through author list and fetches publications from PubMed.
# Checks validity of publication (journal quartile)
# Checks for each publication if it was released in topic.
# Writes publication information into a file for each author.
#
# parameters:
#     topic_short - topic to work with
#
# return: void
#
def getAuthorsPublications(topic_short, name_or_orcid, confidence):

	authors_list = topics.getAuthors(topic_short)
	topic_search_string = topics.getSearchString(topic_short)

	# check if topic was valid
	if authors_list == False or topic_search_string == False:
		print("Topic not found!")
		return False

	authors_list_csv = open(DATA_PATH + "INPUT/" + authors_list, "r", encoding="latin1")
	authors = csv.DictReader(authors_list_csv, delimiter=";")

	# for each author
	for author in authors:

		author_search_string = ""

		if name_or_orcid == "name":
			author_search_string = getAuthorSearchString(author)
			uprint("\n\n" + author["AktID"].zfill(3) + ":", author["Name"], "- PubMedSearch: " + author_search_string)
		elif name_or_orcid == "orcid":
			author_search_string = getAuthorORCIDSearchString(author)
			uprint("\n\n" + author["AktID"].zfill(3) + ":", author["Name"], "- ORCID: " + author_search_string)

		# if a PubMed name is given via author list
		if author_search_string:

			print("Searching for publications...\n")

			authors_dir = DATA_PATH + "OUTPUT/authors_" + topic_short + "/" + name_or_orcid + "/"
			os.makedirs(authors_dir, exist_ok = True)
			author_file = authors_dir + author["AktID"] + "_" + author["Name"].replace(" ", "-") + "_publications.csv"

			### create CSV writer ###
			author_writer_csv = open(author_file, "w+", encoding="latin1")
			author_writer = csv.writer(author_writer_csv, delimiter=";", lineterminator="\n")

			### write column headings ###
			author_writer.writerow(["Active", "Authorship Confidence", "ID (Link)", "Topic", "Title", "Citations", "Date", "Author Position", "Co-Author count"])

			### get papers from PubMed ###
			publications = europepmc.search(author_search_string, "core")["resultList"]["result"]
			publications_topic = europepmc.search(author_search_string + " " + topic_search_string, "idlist")["resultList"]["result"]

			# for each publication
			for i, publication in enumerate(publications):

				pub_id = paper.getPubMedID(publication)
				pub_issn = paper.getISSN(publication)

				if pub_id and journal.isValid(pub_issn):

					if confidence == "confidence":
						authorship_confidence = paper.rateAuthorshipConfidence(publication, author)
					else:
						authorship_confidence = 1

					pub_topic = topic_short if paper.checkTopic(pub_id, publications_topic) else ""

					### write to author file ###
					# write data for this publication into ONE line
					author_writer.writerow([
						### Active ###
						"1" if authorship_confidence > 0 else "0",

						### Authorship Confidence ###
						authorship_confidence,

						### ID (Link) ###
						paper.getPubMedHyperlink(publication),

						### Topic ###
						pub_topic,

						### Title ###
						'"{}"'.format(publication.get("title")).encode('utf-8').decode('latin-1'),

						### Citations ###
						publication.get("citedByCount"),

						### Date ###
						publication.get("journalInfo").get("printPublicationDate"),

						### Author Position ###
						paper.getAuthorPosition(publication, author),

						### Co-Author count ###
						paper.getCoauthorCount(publication)
					])

					uprint("{:s}{:d}) {:s} - {:d} citations".format(
						# put "->" if publication is in topic
						"->" if pub_topic == topic_short else "  ",
						i+1,
						publication.get("title"),
						publication.get("citedByCount")
					))

				else:
					author_writer.writerow([
						0, # Active
						0, # Authorship Confidence
						0, # ID
						"", # TOPIC
						"<invalid>" # Title
					])

					uprint("  publication invalid")

			author_writer_csv.close()

		else:
			print("No PubMed search string given!\n")

	authors_list_csv.close()

#
# main function
#

if __name__ == "__main__":

	topic_short = ""
	name_or_orcid = ""
	confidence = ""

	# check if topic was provied as parameter
	if len(sys.argv) > 1:
		topic_short = str(sys.argv[1])
	# otherwise ask for it
	else:
		print("\nPlease specify a topic via its abbreviation.\nView and edit " + DATA_PATH + "INPUT/topics.csv for possible values.")
		topic_short = input("Topic? ")

	if len(sys.argv) > 2:
		name_or_orcid = str(sys.argv[2])

	if name_or_orcid not in ["name", "orcid"]:
		while True:
			print("\nPlease specify if you want to search by the authors name or ORCID.")
			name_or_orcid = input("name or orcid? ")
			if name_or_orcid in ["name", "orcid"]:
				break  # stops the loop

	if len(sys.argv) > 3:
		confidence = str(sys.argv[3])

	if confidence not in ["confidence", "no-confidence"]:
		while True:
			print("\nPlease specify if you want to use the automatic author confidence rating.")
			confidence = input("confidence or no-confidence? ")
			if confidence in ["confidence", "no-confidence"]:
				break  # stops the loop

	if topic_short != "":
		# check if topic is valid
		if topics.getAuthors(topic_short) != False:
			getAuthorsPublications(topic_short, name_or_orcid, confidence)
		else:
			print("Topic not found!\nView and edit " + DATA_PATH + "INPUT/topics.csv for possible values.")
