#!/usr/bin/python3

from nltk.corpus import wordnet as wn
from nltk import word_tokenize

def findOverlap(sense1, sense2):
    gloss1 = set(word_tokenize(sense1.definition()))
    gloss2 = set(word_tokenize(sense2.definition()))
    ss = len(gloss1.intersection(gloss2))
    total = len(gloss1) + len(gloss2) - ss
    return (float(ss)/total)

def findSimilarity(word1, word2, overlp = True):
    sense1 = wn.synsets(word1)
    sense2 = wn.synsets(word2)
    d = 0.0
    ss = 0.0
    flag = False
    for i in sense1:
        for j in sense2:
            if overlp:
                d = findOverlap(i, j)
            else:
                d = i.path_similarity(j)
            if d == None:
                continue
            if d > ss:
                ss = d
                a, b = i, j
                flag = True
    if flag:
        return ss, a.definition(), b.definition()
    else:
        return ss, None, None

def main():
    a = input("Enter first word : ").strip(" ")
    b = input("Enter second word : ").strip(" ")
    ps, sense1, sense2 = findSimilarity(a.lower(), b.lower(), overlp = False)
    
    if sense1 and sense2:
        print("\nPath Based Similarity:\nSense of " + a + " : " + sense1 + "\nSense of " + b + " : " + sense2 + "\nSemantic Similarity : "+ str(ps))
    else:
        print("\nPath Based Similarity = 0.0")
    
    os, sen1, sen2 = findSimilarity(a.lower(), b.lower())
    if sen1 and sen2:
        print("\nOverlap Based Similarity:\nSense of " + a + " : " + sen1 + "\nSense of " + b + " : " + sen2 + "\nSemantic Similarity : "+ str(os))
    else:
        print("\nOverlap Based Similarity = 0.0")

if __name__ == "__main__":  
    main()
