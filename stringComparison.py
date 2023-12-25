
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

    # Divide the values to find the Jaccard similarity and then return  it 
    return unionLen / intersectionLen


if __name__ == "__main__":
    exit(0)