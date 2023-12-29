
# Calculate and return the Jaccard similarity value between two strings 
# For the purpose of this function the tokens of the strings are any values seperated by spaces
def findJaccardSimilarity(str1, str2):
    # Convert by strings to sets
    s1 = set(str1.split())
    s2 = set(str2.split())

    # Calculate the cardinality of the union of the sets (Calculate the length of the two sets combined)
    unionLen = len(s1.union(s2))

    # Calculate the cardinality of the intersection of two sets (Length of the intersection)
    intersectionLen = len(s1.intersection(s2))
    
    # If the intersection length is 0 return a zero similarity
    if intersectionLen == 0:
        return 0

    # Divide the values to find the Jaccard similarity and then return  it 
    return unionLen / intersectionLen



# Insert a given value into its correct position in a given sorted list by making a copy of the list with inserting the  
# the value as its copied.
# Given list should bne sorted in descending order
def insertIntoSorted(toInsert, list, comparator):
    # Create a new list
    listCopy = []
    # Tracks if the target item has been added to the new list
    targetInserted = False

    # Copy the list
    for item in list:
        if not targetInserted and comparator.compare(toInsert, item) >= 0:
            targetInserted = True
            listCopy.append(toInsert)
            listCopy.append(item)
        else:
            listCopy.append(item)

    # If the given item wasn't added during the copying add it now
    if not targetInserted:
        listCopy.append(toInsert)

    return listCopy

if __name__ == "__main__":
    exit(0)