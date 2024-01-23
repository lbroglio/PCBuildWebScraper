from enum import Enum
from bs4 import BeautifulSoup
import requests

from resources import * 


# Enums holding the different websites/sources that this script scrapes
class  Sources(Enum):
    AMAZON = 0,
    EBAY = 1,
    MICROCENTER = 2

#Enum to hold the possible conditions an ebay item can have
class EbayCondtions(Enum):
    NEW = 8,
    OPEN_BOX = 7,
    CERTIFIED_REFURBISHED = 6,
    EXCELLENT_REFURBISHED = 5,
    VERY_GOOD_REFURBISHED = 4,
    GOOD_REFURBISHED = 3,
    SELLER_REFURBISHED = 2,
    USED = 1,
    FOR_PARTS = 0,
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

class FoundItem:
    # Make a new FoundItem
    # Name = The name of the item/ the title of the listing from its source
    # Similarity = The similarity of this item to the user given search term. Found by calculating the Jaccard similarity
    # Source = The website/marketplace this item  was found on
    # linkTo = A link to this item
    # Condition = The listed condition of the item if applicable (depends on listing source). Defaults to None
    def __init__(self, name, similarity, source, linkTo, condition = None):
        self.name = name
        self.similarity = similarity
        self.source = source
        self.linkTo = linkTo
        self.condition = condition
    def __str__(self):
        return (f"(Name: {self.name}, Weight: {self.similarity})")
    # Object for comparing two FoundItems based on their similarity  value
    class ItemComparator:
        def compare(self, a,  b):
            if a.similarity > b.similarity:
                return 1
            elif a.similarity < b.similarity:
                return -1
            else:
                return 0
 



# Check Amazon results for the item
def scrapeAmazon(searchFor, numPages):
    # Setup list to store found items and a comparator for ordering them
    orderedItems = []
    comp = FoundItem.ItemComparator()

    # Scrape a number of pages equal to the num pages parameter
    for i in range(numPages):
        # Build the URL to scrape from. The target page is the page returned when searching for the item from the amazon home page
        # The URL for these searches is https://www.amazon.com/s?k={item name}+{other words of item name}&page={the page number}

        # Add the item name to the end of the base url with all of its spaces replaced with '+' characters
        targetURL = "https://www.amazon.com/s?k=" + searchFor.replace(' ', '+') + "&page=" + str(i+1)
        # Set header for the requests
        headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip', 
            'DNT' : '1', # Do Not Track Request Header 
            'Connection' : 'close'
        }
        # Get the HTML page corresponding to the URL
        try:
            targetPage =  requests.get(targetURL, headers=headers)
        except requests.exceptions.RequestException  as errh: 
            print(f"ERROR: Could not reach {targetURL}. Root Cause: {errh}")
        bspPage = BeautifulSoup(targetPage.text, features="html.parser")

        # Find all of the item elements by targeting all elements of the "a-section" class
        searchItems = bspPage.find_all("div", {"class": "s-result-item"})
        
        # Add the items to a list of ordered items with their similarity to the search parameter as the weight
        # This is done by finding treating the names as sets of there words and finding the jaccard similarity
        for item in searchItems:
            # If the condition of this item is less than the user specified condition disregard it
            if "AdHolder" in item["class"] or "a-section" in item["class"]:
                continue

            # Get the header which holds the name of and link to this item
            try:
                itemHeader = item.findChildren("h2", {"class", "s-line-clamp-2"}, recursive=True)[0]
            # If this item doesn't have a header continue because it is not a desired listing
            except IndexError:
                continue

            # Get the anchor and span which holds the link and name respectively
            itemAnchor = itemHeader.findChildren("a", recursive=False)[0]
            itemSpan = itemHeader.findChildren("span", recursive=True)[0]

            # Get the link to and name of this item from the anchor
            itemName = itemSpan.text
            itemLink = itemAnchor["href"]

            # Get the Jaccard similarity between this items name and the User's search term
            jSim = findJaccardSimilarity(itemName, searchFor)

            # Create a FoundItem object and add it to the list
            itemObj = FoundItem(itemName, jSim, Sources.AMAZON, itemLink)
            orderedItems = insertIntoSorted(itemObj, orderedItems, comp)

    return orderedItems


# Check Ebay Results for the item 
# Setting minCondition to new will block preowned items; otherwise it will be the lowest condition preowned items 
# need to have to be included. By default set to the lowest so all are allowed
def scrapeEbay(searchFor, numPages, minCondition= EbayCondtions.FOR_PARTS):
    # Setup list to store found items and a comparator for ordering them
    orderedItems = []
    comp = FoundItem.ItemComparator()

    # Scrape a number of pages equal to the num pages parameter
    for i in range(numPages):
        # Build the URL to scrape from. The target page is the page returned when searching for the item from the amazon home page
        # The URL for these searches is https://www.ebay.com/sch/i.html?&_nkw={item name}+{other words of item name}&_pgn={the page number}

        # Add the item name to the end of the base url with all of its spaces replaced with '+' characters
        targetURL = "https://www.ebay.com/sch/i.html?_nkw=" + searchFor.replace(' ', '+') + "&_pgn=" + str(i+1)
        # Set header for the requests
        headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip', 
            'DNT' : '1', # Do Not Track Request Header 
            'Connection' : 'close'
        }
        # Get the HTML page corresponding to the URL
        try:
            targetPage =  requests.get(targetURL, headers=headers)
        except requests.exceptions.RequestException  as errh: 
            print(f"ERROR: Could not reach {targetURL}. Root Cause: {errh}")
        bspPage = BeautifulSoup(targetPage.text, features="html.parser")
        # Find all of the item elements by targeting all elements of the "a-section" class
        searchItems = bspPage.find_all("div", {"class": "s-item__wrapper"})

        # Add the items to a list of ordered items with their similarity to the search parameter as the weight
        # This is done by finding treating the names as sets of there words and finding the jaccard similarity
        for item in searchItems:

            # Get the name of this item
            # Get the div which holds the title
            titleDiv = item.findChildren("div", {"class", "s-item__title"}, recursive=True)[0]
            # Get the span to the title is attached to and get the inner html from it
            itemName = titleDiv.findChildren("span", recursive=False)[0].text  

            # Check the name to see if this is a dummy item found at the top of pages
            # if it is skip it
            if itemName == "Shop on eBay":
                continue

            # Get the anchor containing the link to this item
            itemAnchor = item.findChildren("a", {"class", "s-item__link"}, recursive=True)[0]
            # Get the link to this item from the anchor
            itemLink = itemAnchor["href"]

            # Scrape this items page to check its condition
            try:
                itemPage =  requests.get(itemLink, headers=headers)
            except requests.exceptions.RequestException  as errh: 
                print(f"ERROR: Could not reach {targetURL}. Root Cause: {errh}")
                continue
            itemPageBsp = BeautifulSoup(itemPage.text, features="html.parser")

            #Find the div which holds the items condition on this page
            condDiv = itemPageBsp.find_all("div", {"class": "x-item-condition-text"})[0]
            # Get the span holding the text from this div's children and read the text from it
            condition = condDiv.findChildren("span", {"class": "ux-textspans"}, recursive=True)[0].text

            # Convert the listed condition into an enumc
            condition = condition.upper()
            if "FOR PARTS" in condition:
                conditionE = EbayCondtions.FOR_PARTS
            else:
                conditionE = EbayCondtions[condition.strip().replace(' ', '_').replace('-','_')]

            # Compare the item's condition to the user given limit and discard it if it is too low
            if conditionE < minCondition:
                continue

            # Get the Jaccard similarity between this items name and the User's search term
            jSim = findJaccardSimilarity(itemName, searchFor)

            # Create a FoundItem object and add it to the list
            itemObj = FoundItem(itemName, jSim, Sources.EBAY, itemLink, condition= conditionE)
            orderedItems = insertIntoSorted(itemObj, orderedItems, comp)

    return orderedItems


# Check the Microcenter website for Results for the item 
def scrapeMicrocenter(searchFor, numPages):
    # Setup list to store found items and a comparator for ordering them
    orderedItems = []
    comp = FoundItem.ItemComparator()

    # Scrape a number of pages equal to the num pages parameter
    for i in range(numPages):
        # Build the URL to scrape from. The target page is the page returned when searching for the item from the microcenter home page
        # The URL for these searches is https://www.microcenter.com/search/search_results.aspx?Ntt={keyword}+{more_words}&page={page number}

        # Add the item name to the end of the base url with all of its spaces replaced with '+' characters
        targetURL = "https://www.microcenter.com/search/search_results.aspx?Ntt=" + searchFor.replace(' ', '+') + "&page=" + str(i)
        # Set header for the requests
        headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip', 
            'DNT' : '1', # Do Not Track Request Header 
            'Connection' : 'close'
        }
        # Get the HTML page corresponding to the URL
        try:
            targetPage =  requests.get(targetURL, headers=headers)
        except requests.exceptions.RequestException  as errh: 
            print(f"ERROR: Could not reach {targetURL}. Root Cause: {errh}")
        bspPage = BeautifulSoup(targetPage.text, features="html.parser")
        # Find all of the item elements by targeting all elements of the "a-section" class
        searchItems = bspPage.find_all("li", {"class": "product_wrapper"})

         # Add the items to a list of ordered items with their similarity to the search parameter as the weight
        # This is done by finding treating the names as sets of there words and finding the jaccard similarity
        for item in searchItems:
            # Get the item description div 
            itemDes = item.findChildren("div", {"class", "pDescription"}, recursive=True)[0]

            # Get the name of this item
            # Get the anchor element which holds the title and link to this item
            titleAnchor = itemDes.findChildren("a", {"class", "productClickItemV2"}, recursive=True)[0]
  
            # Get the title from the anchor 
            itemName = titleAnchor.text

            # Get the link to this item from the anchor
            itemLink = titleAnchor["href"]

            # Get the Jaccard similarity between this items name and the User's search term
            jSim = findJaccardSimilarity(itemName, searchFor)

            # Create a FoundItem object and add it to the list
            itemObj = FoundItem(itemName, jSim, Sources.MICROCENTER, itemLink)
            orderedItems = insertIntoSorted(itemObj, orderedItems, comp)

    return orderedItems



if __name__ == "__main__":
    exit(0)