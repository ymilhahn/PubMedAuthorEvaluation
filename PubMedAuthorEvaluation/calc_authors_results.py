import os
import sys
import csv

import numpy
from scipy import stats

import lib.paper as paper
import lib.topics as topics
import lib.metrics as metrics

from lib.uprint import *

# root path of INPUT and OUTPUT folders
DATA_PATH = "../"

def excelFloat(value):
	value = round(value, 3)
	# 23.8 -> 23.800
	# padding right, min. 3 numbers
	value = "{:.3f}".format(value)
	# . to ,
	value = value.replace('.', ',')

	return value

class PublicationEvaluationCategory:

	def __init__(self):
		self.publication_count = 0
		self.lead_count = 0
		self.supervisor_count = 0
		self.citations = []
		self.coauthors = {
			"all": [], "mean": 0, "std": 0, "median": 0, "mode": 0
		}
		self.latest_publication = "0000-00-00"

	#
	# addToCategory
	#
	# Function is called FOR EACH PUBLICATION.
	# The value of the category the publication belongs to gets modified each time.
	# Use this function in a loop to treat all publications.
	#
	# parameters:
	#     self - the category where the publication should be added
	#     publication - the publications where the information comes from
	#
	# return: void
	#
	def addToCategory(self, publication):
		# increase count by one more paper in this category
		self.publication_count += 1

		# append amount of citations to "citations" array
		self.citations.append(int(publication["Citations"]))

		# increase correct count regarding author position value
		if publication["Author Position"] == "first": self.lead_count += 1
		elif publication["Author Position"] == "last": self.supervisor_count += 1

		# compare currently latest and new date, save latest/newest date
		self.latest_publication = paper.checkLatestDate(self.latest_publication, publication["Date"])

		# append amount of co-author count to "coauthors" array
		self.coauthors["all"].append(int(publication["Co-Author count"]))

		return

	#
	# coauthorCalculations
	#
	# Does statistical calculations for co-authors
	#
	# parameters:
	#     self - the category which the calculations are for
	#
	# return: void
	#
	def coauthorCalculations(self):

		coauthors = self.coauthors["all"]

		# update coauthor values after new entry has been added
		if len(coauthors) > 0:
			self.coauthors["mean"] = excelFloat(numpy.mean(coauthors))
			self.coauthors["std"] = excelFloat(numpy.std(coauthors))
			self.coauthors["median"] = excelFloat(numpy.median(coauthors))
			self.coauthors["mode"] = excelFloat(stats.mode(coauthors)[0][0])

		return

#
# getAuthorsPubs
#
# Gets author list for specified topic_pubs.
# Loops through author list and loads files with publication infos.
# Adds each publications info to a general object.
# Does seperation of all valid and topic-only publications.
# After all information has been collected and counted,
# starts some statistical calculations on data.
#
# parameters:
#     topic_short - topic to work with
#
# return: void
#
def getAuthorsResults(topic_short, name_or_orcid):

	authors_list = topics.getAuthors(topic_short)

	calc_authors_results_csv = open(DATA_PATH + "OUTPUT/calc_authors_results_" + topic_short + "_" + name_or_orcid + ".csv", "w+", encoding="latin1")
	authors_writer = csv.writer(calc_authors_results_csv, delimiter=";", lineterminator="\n")

	# write column headings
	authors_writer.writerow([
		"AktID",
		"Name",
		"ORCID",
		"All Publications",

		### valid ###
		"### Valid -->",

		"V: Publications (Q1-Q3)",
		"V: Cites",

		"V: Lead Author",
		"V: Supervisor",
		"V: Latest Pub.",

		"V: Co-authors: mean",
		"V: Co-authors: std",
		"V: Co-authors: median",
		"V: Co-authors: mode",

		"V: h-index",
		"V: g-index",

		### topic ###
		"### Topic -->",

		"T: Publications",
		"T: Cites",

		"T: Lead Author",
		"T: Supervisor",
		"T: Latest Pub.",

		"T: Co-authors: mean",
		"T: Co-authors: std",
		"T: Co-authors: median",
		"T: Co-authors: mode",

		"T: h-index",
		"T: g-index"
	])

	authors_list_csv = open(DATA_PATH + "INPUT/" + authors_list, "r", encoding="latin1")
	authors = csv.DictReader(authors_list_csv, delimiter=";")

	# loop: for each author in our list
	for author in authors:

		uprint("\n\n" + author["AktID"].zfill(3) + ":", author["Name"])

		authors_dir = DATA_PATH + "OUTPUT/authors_" + topic_short + "/" + name_or_orcid + "/"
		author_file = authors_dir + author["AktID"] + "_" + author["Name"].replace(" ", "-") + "_publications.csv"

		#check if document of this author exists...
		if os.path.isfile(author_file):

			# create a new document for this author
			author_reader_csv = open(author_file, "r", encoding="latin1")
			author_reader = csv.DictReader(author_reader_csv, delimiter=";")

			### START INITIALIZING VALUES ###
			# set empty values as starting point for later operations

			publication_count = 0
			invalid_publication_count = 0

			valid_pubs = PublicationEvaluationCategory()
			topic_pubs = PublicationEvaluationCategory()

			### END INITIALIZING VALUES ###


			# loop: for each publication of this author
			for publication in author_reader:

				publication_count += 1

				# counting all publication types

				# invalid publication
				if publication["Title"] == "<invalid>":
					invalid_publication_count += 1

				# publication is marked as "active" (see first column in author file)
				# the "active" value can be used to exclude certain publications from this calculation
				elif publication["Active"] != "0":
					# do calculations for all "valid" publications
					valid_pubs.addToCategory(publication)

					# if publication is related to our topic of interest
					if len(publication["Topic"]):
						# add publication to category for calculation
						topic_pubs.addToCategory(publication)
				else:
					continue

			# do statistical calculation for Co-authors
			topic_pubs.coauthorCalculations()
			valid_pubs.coauthorCalculations()

			print("  valid: {:d} publications with {:d} citations.".format(valid_pubs.publication_count, sum(valid_pubs.citations)))
			print("  topic: {:d} publications with {:d} citations.".format(topic_pubs.publication_count, sum(topic_pubs.citations)))

			# write data for this author into ONE line
			# so each author has one line at the end
			authors_writer.writerow([
				author["AktID"],
				author["Name"],
				author["ORCID"],

				"{} ({} invalid)".format(publication_count, invalid_publication_count),

				### valid ###
				"", # empty column

				valid_pubs.publication_count,
				sum(valid_pubs.citations),

				valid_pubs.lead_count,
				valid_pubs.supervisor_count,
				valid_pubs.latest_publication,

				valid_pubs.coauthors["mean"],
				valid_pubs.coauthors["std"],
				valid_pubs.coauthors["median"],
				valid_pubs.coauthors["mode"],

				metrics.hIndex(valid_pubs.citations),
				metrics.gIndex(valid_pubs.citations),

				### topic ###
				"", # empty column

				topic_pubs.publication_count,
				sum(topic_pubs.citations),

				topic_pubs.lead_count,
				topic_pubs.supervisor_count,
				topic_pubs.latest_publication,

				topic_pubs.coauthors["mean"],
				topic_pubs.coauthors["std"],
				topic_pubs.coauthors["median"],
				topic_pubs.coauthors["mode"],

				metrics.hIndex(topic_pubs.citations),
				metrics.gIndex(topic_pubs.citations)
			])
	authors_list_csv.close()
	calc_authors_results_csv.close()


#
# main function
#

if __name__ == "__main__":

	topic_short = ""
	name_or_orcid = ""

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
			print("\nPlease specify if you searched the authors by name or ORCID.")
			name_or_orcid = input("name or orcid? ")
			if name_or_orcid in ["name", "orcid"]:
				break  # stops the loop

	if topic_short != "":
		# check if topic is valid
		if topics.getAuthors(topic_short) != False:
			getAuthorsResults(topic_short, name_or_orcid)
		else:
			print("Topic not found!\nView and edit " + DATA_PATH + "INPUT/topics.csv for possible values.")
