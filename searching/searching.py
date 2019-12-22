
from bidict import bidict

from config import *

from misc_functions import *

from lexicon.lexicon import *

from inverted_index.inverted_index import *

from forward_index.forward_index import *

from django import forms
from django.shortcuts import redirect

# Importing the stemmig libraries
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer


class Searching():
	# 
	# Defining a class for a searching
	#
	def __init__(self):
		# For this we will need the respective indices and the docIDs
		self.doc_ids = bidict(readDocIDs())
		self.lexicon = readLexicon()
		self.invertedBarrels = {}
		self.shortInvertedBarrels = {}
		self.ranks = readDomainRanks()
		

	# Getting the respective documents based on the docIDs send in
	def getResults(self,resultDocIDs,limit=15):
		documents = []
		for docID in resultDocIDs:
			path = self.doc_ids.inverse[str(docID)]
			try:
				with open(path, "r",encoding='utf-8') as fp:
					documents.append(json.load(fp))
			except FileNotFoundError:
				pass


			if len(documents) == limit:
				break

		return documents


	# Ranking a single word based on its positioning in the title and in the text
	# We are also incorporating the domain_rank of the specific document provided in the dataset itself
	def singleWordRank(self,hits,titleWeight=1.0,normalWeight=0.5):
		ranks = {}
		if hits.get("titleHits") != None:
			for docID, hitlist in hits.get("titleHits").items():
				if ranks.get(docID) == None:
					ranks[docID] = 0


				ranks[docID] += len(hitlist) * titleWeight


		if hits.get("hits") != None:
			for docID, hitlist in hits.get("hits").items():
				if ranks.get(docID) == None:
					ranks[docID] = 0
				ranks[docID] += len(hitlist) * normalWeight

		for docID in ranks:
			if ranks.get(docID) == None:
				ranks[docID] = 0
			ranks[docID] += self.ranks.get(docID)

		return ranks

	# Simply adding the rank of all the individual words and applying bias to each of them
	def multiWordRank(self,rankings,totalRank=0.7):
		ranks = {}
		for wordRanks in rankings:
			for docID, rank in wordRanks.items():
				if ranks.get(docID) == None:
					ranks[docID] = 0

				ranks[docID] += rank * totalRank
		return ranks

	# Getting the respective barrels and returning an exception in case nothing is found
	# If the wordIDs do not match, we raise an exception which is deal by the view itself
	def singleWordQuery(self,word):
		wordID = self.lexicon.get(word)
		if wordID == None:
			raise Exception
			

		
		barrelNum = int(wordID/BARRELS_CAPACITY)   


		if self.invertedBarrels.get(barrelNum) == None:
			try:
				self.invertedBarrels[barrelNum] = readInvertedBarrels(barrelNum)
			except Exception as e:
				print("Error in reading inverted barrels")


		if self.shortInvertedBarrels.get(barrelNum) == None:
			try:
				self.shortInvertedBarrels[barrelNum] = readInvertedBarrels(barrelNum,short=True)
			except Exception as e:
				print("Error in reading inverted barrels")

		# Getting all of the titleHits
		titleHits = self.shortInvertedBarrels.get(barrelNum).get(str(wordID))

		# Getting text hits
		hits = self.invertedBarrels.get(barrelNum).get(str(wordID))


		total_hits = {'titleHits':titleHits, 'hits':hits}

		return self.singleWordRank(total_hits)


	#
	# Splitting the multiple word query
	#
	def multiWordQuery(self,words):
		hits = []

		for word in words:
			hits.append(self.singleWordQuery(word))

		return self.multiWordRank(hits)

	# The main searching function that goes through the search results generated by the above functions
	def search(self,words):

		words = tokenizeString(words)
		tempResults = []
		result = []

		# Calling different functions based on the length of the query
		if len(words) == 1:
			ranked_results = self.singleWordQuery(words[0])
			tempResults = self.getResults(ranked_results.keys())
		elif len(words) > 1:
			ranked_results = self.multiWordQuery(words)
			tempResults = self.getResults(ranked_results.keys())
		else:
			raise Exception("Enter Valid Query")

		for tempResult in tempResults:
			doc = dict()
			doc["title"] = tempResult["title"]
			doc["text"] = tempResult["text"][0:400]
			doc["url"] = tempResult["url"]
			doc["author"] = tempResult["author"]
			result.append(doc)
		return result
