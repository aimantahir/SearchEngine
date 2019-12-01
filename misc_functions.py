"""
Describes all of the general functions used throughout the eniter project
"""

import json
import nltk
import os

# Importing for data serialization
import pickle

from config import *

# Importing the stemmig libraries
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

#
# This function will be used to parse each document of the datatset and converting it into tokens
#
def filter_and_tokenize_file(file):
    text = ""
    path = os.path.join(DATA_PATH,file)
    with open(path,"r",encoding='utf8') as f:
        data = json.loads(f.read())
        text += " " + data["text"]

    # Creating lemmatizing objects
    lemmatizer = WordNetLemmatizer()
    ps = PorterStemmer()

    # Creating tokens and excluding punctuations
    tokens = nltk.regexp_tokenize(text,r'\w+')

    # Stemming tokens and discarding numbers along with tokens of single words
    filtered_tokens = [ps.stem(lemmatizer.lemmatize(token.lower())) for token in tokens if not(len(token) <= 1) and not(token.isdigit())]

    return filtered_tokens

#
# The following function generates the DocIDs for all of files in the dataset
#
def generateDocIDs():
    # Retrieving the DocID file if ti already exists
    try:
        docIndex = readDocIDs()
    except (FileNotFoundError, IOError):
        docIndex = dict()


    for (_,_,files) in os.walk(DATA_PATH):
        for file in files:
            path = os.path.join(DATA_PATH,file)
            # Assigning the docIDs only to those documents which have not been indexed
            if docIndex.get(path) == None:
                docIndex[path] = str(len(docIndex))


    # Writing to the index file
    with open(DOC_INDEX_PATH,"w+",encoding='utf-8') as documentIndexFile:
        json.dump(docIndex,documentIndexFile)   

    # Returning the index
    return docIndex          

#
# Function to read the document index
#
def readDocIDs():
    with open(DOC_INDEX_PATH,"r",encoding='utf-8') as documentIndexFile:
        docIndex = json.load(documentIndexFile)

    return docIndex

#
# This function takes all hte barrels generated form the forward index and adds them to the already existing barrels or
# create new ones for them based on if they already exist in the Data Barrels
#
def generateBarrels(immediateBarrels):
    for key,value in immediateBarrels.items():
        forwardBarrel = dict()
        try:
            with open(os.path.join(BARREL_PATH,"barrel{}.json".format(key)) ,"r",encoding='utf-8') as forwardBarrelFile:
                forwardBarrel = json.load(forwardBarrelFile)
        except (FileNotFoundError, IOError):
            pass
        
        forwardBarrel.update(value)
        with open(os.path.join(BARREL_PATH,"barrel{}.json".format(key)) ,"w+",encoding='utf-8') as forwardBarrelFile:
            forwardBarrel = json.dump(forwardBarrel,forwardBarrelFile)


#
# This function generates the pickle file which stores the list storing whether or not a certian docID has been indexed or not
# It acesses the docIDs from the docIDs file 
#
def generateIsIndexed(indexedDocs):
    try:
        indexedDocs.append(readIsIndexed())
    except (FileNotFoundError, IOError):
        pass

    
    with open(IS_INDEXED_PATH,"wb+") as isIndexedFile:
        pickle.dump(indexedDocs,isIndexedFile)     
          

#
# Reading the file using pickle 
#
def readIsIndexed():
    with open(IS_INDEXED_PATH,"rb") as isIndexedFile:
        isIndexed = pickle.load(isIndexedFile)
    return isIndexed
        
#
# This function takes all hte barrels generated form the inverted index and adds them to the already existing barrels or
# create new ones for them based on if they already exist in the Data
#
def generateInvertedBarrels(immediateInvertedBarrels):
    for key,value in immediateInvertedBarrels.items():
        invertedBarrel = dict()
        
        invertedBarrel.update(value)
        with open(os.path.join(INVERTED_BARREL_PATH,"barrel{}Inverted.json".format(key)) ,"w+",encoding='utf-8') as invertedBarrelFile:
            json.dump(invertedBarrel,invertedBarrelFile)
