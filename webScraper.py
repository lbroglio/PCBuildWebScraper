from enum import Enum
from bs4 import BeautifulSoup
import requests

from resources import * 


# Enums holding the different websites/sources that this script scrapes
class  Sources(Enum):
    AMAZON = 0,
    EBAY = 1,
    NEWEGG = 2


class FoundItem:
    # Make a new FoundItem
    # Name = The name of the item/ the title of the listing from its source
    # Similarity = The similarity of this item to the user given search term. Found by calculating the Jaccard similarity
    # Source = The website/marketplace this item  was found on
    # linkTo = A link to this item
    def __init__(self, name, similarity, source, linkTo):
        self.name = name
        self.similarity = similarity
        self.source = source
        self.linkTo = linkTo
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
            # If this item is from an ad, sponsored result, or is a header disregard it
            # Ads and sponsored results are disregarded to maximize the value of results and to only 
            # operate on elements with a similar structure
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
        
scrapeAmazon("intel i7", 5)
        
