from lxml import html

import requests
import datetime

from fake_useragent import UserAgent

class fulltextScrapperEntry:

	def __init__(self):

		self.headers = {'User-Agent': UserAgent().random}


	def scrap(self, sourceList):

		#TODO: handle elsevier locator site
		#http://linkinghub.elsevier.com/retrieve/pii/S0750765884800799

		# get first Europe_PMC html (non-pdf) source
		source = next((x for x in sourceList if x.get("site") == "Europe_PMC" and x.get("documentStyle") != "pdf"), None)
		# othwerwise select any non-pdf source
		if source == None: source = next(x for x in sourceList if x.get("documentStyle") != "pdf")

		result = None

		if source != None:

			try:
				result = getattr(self, source["site"])(source["url"])
			except AttributeError:
				#print("Using default method for: " + source["site"])
				try:
					result = getattr(self, "StandardMethod")(source["url"])
				except AttributeError:
					print("ERROR: No method specified for this fulltext source: " + source["site"] + "-" + source["url"])

			with open("fullTextStatus.txt", "a") as statusfile:

				if result != None and (not len(result["authors"]) or not len(result["affiliations"])):
					statusfile.write('{:%Y-%m-%d %H:%M:%S}: '.format(datetime.datetime.now()))
					statusfile.write("\t\t" + source["url"] + "\n")

					if not len(result["authors"]):
						statusfile.write("\t\t" + "No authors found." + "\n")
					if not len(result["affiliations"]):
						statusfile.write("\t\t" + "No affiliations found." + "\n")

					statusfile.write("\n")

		return result


	### LIST OF SERVICES ###

	def StandardMethod(self, url):

		authors = []
		affiliations = []

		try:
			response = requests.get(url, headers = self.headers, timeout=12)
		except:
			print("CONNECTION ERROR: " + url)
			return None

		# check if response is OK
		if response.status_code == 200:
			tree = html.fromstring(response.content)

			queries_authors = [
				'//span[@class="author-name"]/text()', 							# ScienceDirect
				'//a[contains(@class, "authorName")]/text()', 					# ScienceDirect
				'//span[contains(@class, "author-name")]/text()', 				# ScienceDirect
				'//div[contains(@class, "contrib-group")]/a/text()', 			# Europe_PMC
				'//div[contains(@class, "authors__list")]/descendant::*/text()',# SpringerLink
				'//section[contains(@class, "authors")]/div[1]/p[1]/a',			# PHYSICAL REVIEW A/LETTER
				'//*[@id="main-content"]/header/div/div[1]/ul/li/h3',			# Electrophoresis
				'//div[contains(@class, "meta-authors")]/span[1]/span/a',		# JAMA Network, shown authors
				'//div[contains(@class, "meta-authors")]/span[2]/span',			# JAMA Network, hidden et.al. authors
				'//ol[@class="contributor-list"]/li/span',						# Science
				'//a[@id="openAuthor_"]',										# JSR Surgical Research
				'//div[@class="authors"]/div/span/span/a',						# sage journals
			]

			for query in queries_authors:
				result = tree.xpath(query)
				if len(result):
					authors.append(result)
					#NOTE: break after found? begter not, we currently have two xpath sometimes

			#TODO: remove trailing comma!
			# or simpley take stuff infront of first comma?
			# see: Joachim E. Fischer, MD, MSc, http://jamanetwork.com/journals/jamapediatrics/fullarticle/203971

			# flatten and remove empty elements
			authors = [item for sublist in authors for item in sublist if item.strip()]

			for author in authors:
				author = author.split(",")[0]

			queries_affiliations = [
				'//*[contains(@class, "affiliation")]/text()', 						# ScienceDirect
				'//ul[contains(@class, "affiliation")]/descendant::*/text()', 		# ScienceDirect
				'//div[contains(@class, "fm-authors-info")]/descendant::*/text()', 	# Europe_PMC
				'//span[contains(@class, "authors__name")]/text()', 				# SpringerLink
				'//section[contains(@class, "authors")]/div[1]/ul/li',				# PHYSICAL REVIEW A/LETTER
				'//div[@class="authorInfo"]',										# JAMA Network
				'//ol[@class="affiliation-list"]/li/span',							# Science
				'//div[@class="affiliation"]',										# JSR Surgical Research
				'//div[@class="artice-info-affiliation"]'							# sage journals

			]

			for query in queries_affiliations:
				result = tree.xpath(query)
				if len(result): affiliations.append(result)

			# flatten and remove empty elements
			affiliations = [item for sublist in affiliations for item in sublist if item.strip()]

		return {"authors": authors, "affiliations": affiliations}


#
# main function
#
# This file is not meant to be executed sole, but can be for debugging purpose.
#

if __name__ == "__main__":

	fulltextScrapper = fulltextScrapperEntry()

	#print(fulltextScrapper.scrap([{"site": "ScienceDirect", "url": "http://www.sciencedirect.com/science/article/pii/S0042682284711470"}]))
	print(fulltextScrapper.scrap([{"site": "ScienceDirect", "url": "http://dx.doi.org/10.1016/S0021-9673(00)00551-3"}]))
