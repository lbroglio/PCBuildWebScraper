from webScraper import *
from operator import attrgetter

import heapq

# Read in the keywords and prices from the user to use to search for the different parts of the build
def getInput():
    # Create a dictionary to store the keywords collect from the user
    keywordDict = {}
    # Create a dictionary to store the maximum prices collected from the user
    priceDict = {}

    # Get the inputs for the indivudal parts
    keywordDict["cpu"] = input("Enter the search term to be used when looking for the CPU: ")
    priceDict["cpu"] = input("Enter the maximum price for the CPU or leave blank for unlimited: ")
    if priceDict["cpu"] == "":
        priceDict["cpu"] = float('inf')

    keywordDict["gpu"] = input("Enter the search term to be used when looking for the GPU: ")
    priceDict["gpu"] = input("Enter the maximum price for the GPU or leave blank for unlimited: ")
    if priceDict["gpu"] == "":
        priceDict["gpu"] = float('inf')

    keywordDict["ram"] = input("Enter the search term to be used when looking for the RAM: ")
    priceDict["ram"] = input("Enter the maximum price for the RAM or leave blank for unlimited: ")
    if priceDict["ram"] == "":
        priceDict["ram"] = float('inf')

    keywordDict["motherboard"] = input("Enter the search term to be used when looking for the motherboard: ")
    priceDict["motherboard"] = input("Enter the maximum price for the motherboard or leave blank for unlimited: ")
    if priceDict["motherboard"] == "":
        priceDict["motherboard"] = float('inf')
    
    keywordDict["storage"] = input("Enter the search term to be used when looking for the storage or leave blank to exclude storage: ")
    if keywordDict["storage"] == "":
        keywordDict["storage"] = None
    priceDict["storage"] = input("Enter the maximum price for the storage or leave blank for unlimited: ")
    if priceDict["storage"] == "":
        priceDict["storage"] = float('inf')

    # Return the two dicts as a tuple with the keyword dict in index 0
    return keywordDict, priceDict


# Check all of the sites for the parts given by the user
def searchForParts(keywordDict):
    # Dict which will store the lists of found results associated with a string name of the part that list holds 
    resultsDict = {}

    # Go through every keyword given by the user
    for key in keywordDict:
        # Get the search term for the current part from the dict
        searchTerm = keywordDict[key]

        # Skip this term if it is None as this is the signal for the user choosing to skip the term
        if searchTerm is None:
            continue
    
        
        # Get the results for this term from every source
        amazonResults = scrapeAmazon(searchTerm, 3)
        ebayResults = scrapeEbay(searchTerm, 3)
        microcenterResults = scrapeMicrocenter(searchTerm, 3)

        # Combine the results into one list and add them to the storage dict
        results = list(heapq.merge(amazonResults,  ebayResults, microcenterResults, key=attrgetter('similarity'), reverse=True))
        resultsDict[key] = results
    
    return resultsDict


parts = searchForParts(getInput()[0])
for key in parts:
    print(f"{key}: {parts[key][0]}")