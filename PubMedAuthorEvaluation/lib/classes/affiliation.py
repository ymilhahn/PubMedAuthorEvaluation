from geotext import GeoText

import re

class affiliationEntry:

	def __init__(self, text):

		self.text = ""
		self.cities = []
		self.countries = []
		self.institutions = []

		if (text != None):
			self.text = text

			places = GeoText(text)

			# filter weird elements
			if "University" in places.cities:
				places.cities.remove("University")

			self.cities = list(set(places.cities))
			self.countries = list(set(places.countries))


	def getInstitutions(self):

		# remove dot, replace semicolons, split
		affParts = self.text.rstrip(".").replace(";",",").replace(", ",",").split(",")

		for part in affParts:

			#TODO: propper stop word filter

			equivalents = {
				"the ": "",
				"&": "and"
			}

			# replace equivalents
			equivalents = dict((re.escape(k), v) for k, v in equivalents.items())
			pattern = re.compile("|".join(equivalents.keys()))
			part = pattern.sub(lambda m: equivalents[re.escape(m.group(0))], part)

			part = part.strip()

			regexList = [
				"(.*Universität.*)",
				"(.*Institut.*)",
				"(.*Institute.*)",
				#"(.*Institut (of|for) .*)",
				#"(.*Institute (of|for) .*)",
				"(.+Hospital)",
				"(.+University)",
				"(.*University (School)? of .*)",
				"(.*School of .*)"
			]

			match = False
			for regex in regexList:
				match = re.search(regex, part)
				if match:
					institution = match.group(1)

					if institution not in self.institutions:
						self.institutions.append(institution)


		return self.institutions
