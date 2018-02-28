import csv

# root path of INPUT and OUTPUT folders
DATA_PATH = "../"

#
# isValidJournal
#
# Runs given ISSN against a journal ranking.
# Extracts Quartile of journal.
# Checks if Quartile is valid (not contained in "invalid" array).
#
# parameters:
#     issn - issn to check
#
# return: true/false
#

def isValid(issn):

	# array which holds all invalid QX
	invalid = ["Q4"] # e.g. ["Q4", "Q3"]

	if issn != False:

		with open(DATA_PATH + "INPUT/journal-ranking.csv", "r", encoding="utf-8-sig") as journal_list:
			journals = csv.DictReader(journal_list)

			for num, journal in enumerate(journals):
				if journal.get("Issn"):
					if journal["SJR Best Quartile"] not in invalid:
						return True
					else:
						return False


#
# main function
#
# This file is not meant to be executed sole, but can be for debugging purpose.
#

if __name__ == '__main__':
	print("Q1 journal:", isValid("13446223"))
	print("Q4 journal:", isValid("08910618"))
