from bs4 import BeautifulSoup as bsp
import requests

import stringComparison

def scrapeAmazon(itemName):
    # Build the URL to scrape from. The target page is the page returned when searching for the item from the amazon home page
    # The URL for these searches is https://www.amazon.com/s?k={item name}+{other words of item name}

    # Add the item name to the end of the base url with all of its spaces replaced with '+' characters
    targetURL = "https://www.amazon.com/s?k" + itemName.replace(' ', '+')
    
    # Get the HTML page corresponding to the URL
    try:
        targetPage =  requests.get(targetURL)
    except requests.exceptions.RequestException  as errh: 
        print(f"ERROR: Could not reach {targetURL}. Root Cause: {errh}")

    # Find all of the item elements by targeting all elements of the "a-section" class
    searchItems = bsp.find_all("div", {"class": "a-section"})

    # Order the items by the similarity between its name and the user given search parameter
    # This is done by finding treating the names as sets of there words and finding the jaccard similarity
    orderItems = []
    for item in searchItems:
        # Get the "h2" tag children of the item
        h2Children = item.findChildren("h2" , recursive=False)
        # Get the first "span" child of the first found "h2" tag
        spanChild = h2Children[0].findChildren("span", recursive=False)[0]

        # Get the text from the found "span" element
        itemName = spanChild.text

        
