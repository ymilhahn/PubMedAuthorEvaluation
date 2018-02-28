import csv

# root path of INPUT and OUTPUT folders
DATA_PATH = "../"

def openTopicCSV():
	t_list = open(DATA_PATH + "INPUT/topics.csv", "r", encoding="latin1")
	topics = csv.DictReader(t_list, delimiter=";")

	return topics

#
# getSearchString
#
# Get pubmed search string for a certain topic in topic.csv
#
# parameters:
#     topic_short - abbreviation of topic name
#
# return: search string
#

def getSearchString(topic_short):

	topics = openTopicCSV()

	for t in topics:
		if t["short"] == topic_short:
			return t["search string"]
	return False


#
# getAuthors
#
# Get actors list file name in topic.csv
#
# parameters:
#     topic_short - abbreviation of topic name
#
# return: actors list file name
#

def getAuthors(topic_short):

	topics = openTopicCSV()

	for t in topics:
		if t["short"] == topic_short:
			return t["actors list file"]
	return False
