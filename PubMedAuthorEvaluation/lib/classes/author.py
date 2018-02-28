from pprint import pprint
from copy import deepcopy
from unidecode import unidecode

from lib.helpers import *
from lib.classes.affiliation import *
from lib.classes.fulltextscrapper import *

fulltextScrapper = fulltextScrapperEntry()

confidence = {
	"values": {
		"matchedInitials": 0.2,
		"matchedForname": 0.8,
		"mismatchedForname": -1,

		"matchedFulltextInitials": 0.2,
		"matchedFulltextName": 1,
		"mismatchedFulltextName": -1,

		"matchedCoauthors": 0.1,
		"matchedLocations": 0.2,
		"matchedInstitutions": 0.5
	},
	"tresholds": {
		"coauthors_neg": 0,
		"coauthors_pos": 0.5,
		"locations": 0.5,
		"institutions": 0.5
	}
}

class authorEntry:

	def __init__(self):
		self.name = {
			"first": "",
			"middle": "",
			"last": "",
			"fornames": "",
			"initials": ""
		}
		self.abbreviations = {
			"include": [],
			"exclude": []
		}
		self.publications = {}
		self.locations = {}
		self.institutions = {}
		self.coauthors = {
			#"Moon S": ["pmid1", "pmid2", "pmid3"],
		}


	def createNameVaraiations(self):

		fornames = [self.name["first"]]

		#TODO: HANDLE MIDDLE NAME the same way!

		# transform "Hans-Dieter" to ...
		if "-" in self.name["first"]:
			spf = self.name["first"].split("-")
			fornames.append(uniform(spf[0] + " " + spf[1])) 			# "Hans Dieter"
			fornames.append(uniform(spf[0][0] + " " + spf[1])) 			# "H Dieter"
			fornames.append(uniform(spf[0][0] + ". " + spf[1])) 		# "H. Dieter"
			fornames.append(uniform(spf[0] + " " + spf[1][0])) 			# "Hans D"
			fornames.append(uniform(spf[0] + " " + spf[1][0]) + ".") 	# "Hans D."

			fornames.append(uniform(spf[0][0] + "-" + spf[1])) 			# "H-Dieter"
			fornames.append(uniform(spf[0][0] + ".-" + spf[1])) 		# "H.-Dieter"
			fornames.append(uniform(spf[0] + "-" + spf[1][0])) 			# "Hans-D"
			fornames.append(uniform(spf[0] + "-" + spf[1][0]) + ".") 	# "Hans-D."


		# if " " in coauthor.get("firstName") and len(self.name["middle"]) > 0:
		# 	fornames.append(self.name["first"] + " " + self.name["middle"])
		# 	fornames.append(self.name["first"] + " " + self.name["middle"][0])

		self.name["fornames"] = list(fornames)


		initials = []

		# transform "Hans-Dieter" to ...
		if "-" in self.name["first"]:
			spf = self.name["first"].split("-")
			initials.append(uniform(spf[0][0] + spf[1][0])) 				# "HD"
			initials.append(uniform(spf[0][0] + " " + spf[1][0])) 			# "H D"
			initials.append(uniform(spf[0][0] + ". " + spf[1][0]) + ".") 	# "H. D."

			initials.append(uniform(spf[0][0] + "." + spf[1][0]))	 		# "H.D"
			initials.append(uniform(spf[0][0] + "." + spf[1][0]) + ".") 	# "H.D."

			initials.append(uniform(spf[0][0] + "-" + spf[1][0])) 			# "H-D"
			initials.append(uniform(spf[0][0] + ".-" + spf[1][0]) + ".") 	# "H.-D."
			initials.append(uniform(spf[0][0] + ". -" + spf[1][0]) + ".") 	# "H. -D."
		else:
			initials.append(self.name["first"][0])

		if len(self.name["middle"]) > 0:
			initials.append(self.name["first"][0] + self.name["middle"][0])

		self.name["initials"] = list(initials)

		return

	def addPublication(self, publication):

		if publication.get("id") in self.publications:
			self.publications[publication.get("id")]["data"] = publication
		else:
			self.publications[publication.get("id")] = {"confidence": 0, "data": publication}
		#else:
			#print(publication.get("id") + " already in list")

		return


	def addCoauthorInfo(self, coauthor, publication):

		if (coauthor.get("fullName") != None):

			name = uniform(coauthor.get("fullName"))

			if name not in self.coauthors:
				self.coauthors[name] = []

			if publication.get("id") not in self.coauthors[name]:
				self.coauthors[name].append(publication.get("id"))

		return


	def addLocationInfo(self, publication):

		for coauthor in getAuthors(publication):

			lastNameFits, abbreviationFits = self.abbreviationFits(coauthor.get("fullName"))

			if lastNameFits and abbreviationFits:

				affiliationString = coauthor.get("affiliation") or publication.get("affiliation")
				affiliation = affiliationEntry(affiliationString)

				# prevent malformated affiliations
				if len(affiliation.cities) >= 1 and len(affiliation.cities) <= 2:

					city = affiliation.cities[0]

					if city not in self.locations:
						self.locations[city] = []

					if publication.get("id") not in self.locations[city]:
						self.locations[city].append(publication.get("id"))


	def addInstitutionInfo(self, publication):

		for coauthor in getAuthors(publication):

			lastNameFits, abbreviationFits = self.abbreviationFits(coauthor.get("fullName"))

			if lastNameFits and abbreviationFits:

				affiliationString = coauthor.get("affiliation") or publication.get("affiliation")
				affiliation = affiliationEntry(affiliationString)

				institutions = affiliation.getInstitutions()

				# prevent malformated affiliations
				if len(institutions) > 0:

					for institution in institutions:

						if institution not in self.institutions:
							self.institutions[institution] = []

						if publication.get("id") not in self.institutions[institution]:
							self.institutions[institution].append(publication.get("id"))


	def addOwnAbbreviation(self):

		if len(self.publications) > 1: #NOTE: necessary?

			# sort coauthors by amount of coauthorships
			for coauthor in self.coauthors:
				lastNameFits, initialsFit = self.abbreviationFits(coauthor)

				if lastNameFits and initialsFit:

					name = uniform(coauthor)

					if name not in self.abbreviations["include"]:
						self.abbreviations["include"].append(name)

		#max(self.coauthors, key=lambda k: len(self.coauthors[k]))
		return


	def getSimilarAbbreviations(self):

		#TODO: ask user if author has published under synonyms (if firstname first char fits)

		for coauthor in sorted(self.coauthors, key=lambda k: len(self.coauthors[k]), reverse=True):
			lastNameFits, initialsFit = self.abbreviationFits(coauthor)
			if lastNameFits and not initialsFit:

				#TODO: excluded still gets some uppercase abbr.
				name = uniform(coauthor)

				if name not in self.abbreviations["include"] and name not in self.abbreviations["exclude"]:
					self.abbreviations["exclude"].append(name)

		return self.abbreviations["exclude"]


	def addInformations(self, publications):

		for publication in publications:
			self.addPublication(publication)

			for coauthor in getAuthors(publication):
				self.addCoauthorInfo(coauthor, publication)

			self.addLocationInfo(publication)
			self.addInstitutionInfo(publication)

		self.addOwnAbbreviation()


	def abbreviationFits(self, abbreviation):

		if abbreviation == None: return False, False

		lastNameFits = False
		initialsFit = False

		# not starting with last name? not our man!
		if not uniform(abbreviation).startswith(self.name["last"]):
			return False, False

		if len(abbreviation.split(self.name["last"])) < 2:
			return False, False

		last = abbreviation.split(" ")[0]

		if ("-" in last):
			# handle "Schlick-Steiner"
			first = abbreviation.split(last)[1].strip()
		else:
			initials = abbreviation.split(self.name["last"])[1].strip()
			lastName = abbreviation.split(initials)[0].strip()

		# compare first part to last name
		lastNameFits = uniform(lastName) == self.name["last"]

		if len(initials):
			for curInitials in self.name["initials"]:
				if initials == curInitials:
					initialsFit = initials
					break

		return lastNameFits, initialsFit


	def coauthorNameFits(self, coauthor):

		lastNameFits = False
		fornamesFit = False
		namesNotNone = coauthor.get("lastName") != None and coauthor.get("firstName") != None

		#TODO: use initials if firstName is not usefull (too short or not present)
		if namesNotNone and len(coauthor.get("firstName")) > 1:

			# lastName
			lastNameFits = uniform(coauthor.get("lastName")) == self.name["last"]

			for forname in self.name["fornames"]:
				if forname == uniform(coauthor.get("firstName")):
					fornamesFit = forname
					break

		return lastNameFits, fornamesFit


	def matchName(self):

		# integrate into addPublication?
		for pubid in self.publications:
			if (self.publications[pubid]["confidence"] != 1):
				publication = self.publications[pubid]["data"]
				#confidence = 0

				#TODO: fix multiple authors with same last name

				for coauthor in getAuthors(publication):

					lastNameFits, initialsFit = self.abbreviationFits(coauthor.get("fullName"))
					lastNameFits, fornamesFit = self.coauthorNameFits(coauthor)

					if lastNameFits:

						hasRealFirstName = len(coauthor.get("firstName").replace(" ", "").replace(".", "").replace("-", "")) > 2

						if hasRealFirstName:
							if initialsFit:
								self.publications[pubid].setdefault("matchedInitials", []).append(initialsFit)
								#TODO: mismatchedInitials???

							if fornamesFit:
								self.publications[pubid].setdefault("matchedForname", []).append(fornamesFit)
							else:
								self.publications[pubid].setdefault("mismatchedForname", []).append(coauthor)
							# if firstName is given but does not fit?
							 #and initialsFit:
								#print("EXCLUDED: " + pubid)


								# name = uniform(coauthor)
								# if name not in self.abbreviations["exclude"]:


	def matchFulltextName(self):

		# integrate into addPublication?
		for pubid in self.publications:
			#if (self.publications[pubid]["confidence"] != 1):
			publication = self.publications[pubid]["data"]

			if publication.get("fullTextUrlList") != None and publication.get("fullTextUrlList").get("fullTextUrl") != None:
				#print(publication.get("fullTextUrlList").get("fullTextUrl"))
				fullTextInfo = fulltextScrapper.scrap(publication.get("fullTextUrlList").get("fullTextUrl"))

				if fullTextInfo != None:

					#TODO: fix multiple authors with same last name!!!!

					for fullName in fullTextInfo["authors"]:

						fullName = unidecode(fullName)

						last = fullName.split(" ")[-1]

						if ("-" in last):
							# handle "Schlick-Steiner"
							first = fullName.split(last)[0].strip()
						else:
							# get full name by spliting at firstname.
							# rest should be the lastname.
							first = fullName.split(self.name["last"])[0].strip()
							last = fullName.split(first)[1].strip()

						coauthor = {
							"firstName": first,
							"lastName": last
						}

						lastNameFits, fornamesFit = self.coauthorNameFits(coauthor)

						if lastNameFits:

							hasRealFirstName = len(first.replace(" ", "").replace(".", "").replace("-", "")) > 2

							if hasRealFirstName:
								if fornamesFit:
									self.publications[pubid].setdefault("matchedFulltextName", []).append(fornamesFit)
								else:
									self.publications[pubid].setdefault("mismatchedFulltextName", []).append(coauthor)

							else:
								lastNameFits, initialsFit = self.abbreviationFits(last + " " + first)

								if initialsFit:
									self.publications[pubid].setdefault("matchedFulltextInitials", []).append(initialsFit)


	def matchCoauthors(self):

		for pubid in self.publications:

			for coauthor in getAuthors(self.publications[pubid]["data"]):

				if coauthor.get("fullName") != None:

					name = uniform(coauthor.get("fullName"))

					if name in self.coauthors and name not in self.abbreviations["include"] and name not in self.abbreviations["exclude"]:

						if len(self.coauthors[name]) > 1: # has more than this publication?
							self.publications[pubid].setdefault("matchedCoauthors", []).append(name)


	def confidenceCoauthors(self, pubid):

		#TODO: use this function for coauthors, locations and institutions

		confidence_coauthors = 0
		for name in self.publications[pubid]["matchedCoauthors"]:
			for otherPubID in self.coauthors[name]:
				if pubid == otherPubID: continue

				if self.publications[otherPubID]["confidence"] < confidence["tresholds"]["coauthors_neg"]:
					confidence_coauthors -= 0.1
				if self.publications[otherPubID]["confidence"] > confidence["tresholds"]["coauthors_pos"]:
					confidence_coauthors += 0.1

		return round(confidence_coauthors, 1)


	def matchLocations(self):

		for pubid in self.publications:

			publication = self.publications[pubid]["data"]

			for coauthor in getAuthors(publication):

				lastNameFits, abbreviationFits = self.abbreviationFits(coauthor.get("fullName"))

				if lastNameFits and abbreviationFits:

					affiliationString = coauthor.get("affiliation") or publication.get("affiliation")
					affiliation = affiliationEntry(affiliationString)

					# prevent malformated affiliations
					if len(affiliation.cities) >= 1 and len(affiliation.cities) <= 2:
						city = affiliation.cities[0]

						# check if associated publications are not inconfident

						locations = deepcopy(self.locations[city])

						for locPubId in locations:
							if self.publications[locPubId]["confidence"] < confidence["tresholds"]["locations"]:
								locations.remove(locPubId)

						if city in self.locations and len(locations) >= 2:
							self.publications[pubid].setdefault("matchedLocations", []).append(city)


	def matchInstitutions(self):

		#TODO: don't do iterate on all confidence functions but instead one loop for all

		for pubid in self.publications:

			publication = self.publications[pubid]["data"]

			for coauthor in getAuthors(publication):

				lastNameFits, abbreviationFits = self.abbreviationFits(coauthor.get("fullName"))

				if lastNameFits and abbreviationFits:

					affiliationString = coauthor.get("affiliation") or publication.get("affiliation")
					affiliation = affiliationEntry(affiliationString)

					institutions = affiliation.getInstitutions()

					# prevent malformated affiliations
					if len(institutions) > 0:

						for institution in institutions:

							instPublications = deepcopy(self.institutions[institution])

							# check if associated publications are not inconfident
							for instPubId in instPublications:
								if self.publications[instPubId]["confidence"] < confidence["tresholds"]["institutions"]:
									instPublications.remove(instPubId)

							if institution in self.institutions and len(instPublications) >= 2:
								self.publications[pubid].setdefault("matchedInstitutions", []).append(institution)


	def calculateConfidenceValue(self):

		for pubid in self.publications:

			#TODO: if paper has negative conficene (< -0.5):
			# there should be something like mismatchedCoauthors
			# give -0.1 for each negative and +0.1 for each positive?

			confidence_overall = 0

			for type in confidence["values"]:

				if type in self.publications[pubid]:

					if type == "matchedCoauthors":
						confidence_overall += self.confidenceCoauthors(pubid)

					#elif type == "matchedLocations":
					#elif type == "matchedInstitutions":

					else:
						confidence_overall += confidence["values"][type] * len(self.publications[pubid][type])

			self.publications[pubid]["confidence"] = round(self.publications[pubid]["confidence"] + confidence_overall, 1)


	def buildIDQuery(self):

		IDlist = ""
		for i, id in enumerate(self.publications):
			if i != 0: IDlist += " OR "

			if "PMC" in id:
				IDlist += 'PMCID:"{}"'.format(id)
			else:
				IDlist += 'EXT_ID:"{}"'.format(id)

		query = '({})'.format(IDlist)

		return query


	def buildAUTHQuery(self, type):

		if type == "full":

			AUTHlist = ""
			name = self.name["first"]
			name += " " + self.name["last"]
			AUTHlist += 'AUTH:"{}" '.format(name)

			if self.name["middle"] != "":
				name = self.name["first"]
				name += " " + self.name["middle"]
				name += " " + self.name["last"]
				AUTHlist += 'OR AUTH:"{}"'.format(name)

			query = '({})'.format(AUTHlist)

		if type == "abbreviation":

			AUTHlistIN = ""
			AUTHlistEX = ""
			for i, abbr in enumerate(self.abbreviations["include"]):
				if i != 0: AUTHlistIN += " OR "
				AUTHlistIN += 'AUTH:"{}"'.format(abbr)

			for i, abbr in enumerate(self.abbreviations["exclude"]):
				#if i != 0: AUTHlistEX += " "
				AUTHlistEX += ' NOT AUTH:"{}"'.format(abbr)

			query = "(" + AUTHlistIN + " " + AUTHlistEX + ")"

		return query


	def debug(self):

		for key in self.abbreviations:
			print(key.ljust(20) + str(self.abbreviations[key]))

		for key in sorted(self.publications, key=lambda k: self.publications[k]["confidence"], reverse=True):
		#for key in self.publications:
			fulltext = "fulltext" if "fullTextUrlList" in self.publications[key]["data"] else ""
			print(key.ljust(14) + " [" + str(self.publications[key]["data"]["pubYear"]) + "]" + "\t" + str(self.publications[key]["confidence"]) + "\t" + fulltext)

			# for value in self.publications[key]:
			# 	print(key.ljust(8) + '\t%s: %s' % (value, self.publications[key][value]))

		# for key in self.institutions:
		#  	if (len(self.institutions[key]) >= 1):
		#  		print(key.ljust(10) + '\t%s' % (self.institutions[key]))

		# for key in self.coauthors:
		# 	if (len(self.coauthors[key]) >= 1):
		# 		print(key.ljust(10) + '\t%s' % (self.coauthors[key]))


	def debugFull(self):

		for pubid in self.publications:
			self.publications[pubid].pop("data", None)

		pprint (vars(self))
