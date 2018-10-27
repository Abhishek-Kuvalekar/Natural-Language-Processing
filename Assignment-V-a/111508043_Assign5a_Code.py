#! /usr/bin/python3

import argparse
import nltk
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import re

def writeStatistics(tagCount, tagContext):
    uniqueTags = ["PERSON", "LOCATION", "ORGANIZATION", "DATE", "TIME", "MONEY", "PERCENT"]
    floatFormat = "{:.5f}"
    lineFormat = "{:15} {:15}"
    
    totalCount = 0
    for tag in tagCount:
        totalCount += tagCount[tag]
    
    for tag in uniqueTags:
        tagCount[tag] = tagCount.get(tag, 0) / totalCount

    fd_w = openFile("Stat_NER_111508043.txt", "w")
    fd_w.write(lineFormat.format("TAG", "PROBABILITY"))
    fd_w.write("\n")

    for tag in uniqueTags:
        fd_w.write(lineFormat.format(str(tag), str(floatFormat.format(tagCount.get(tag, 0.00000)))))
        fd_w.write("\n")
    fd_w.close()

    lineFormat = "{:15} {:15} {:15} {:15} {:15} {:15} {:15} {:15}"
    for tag in uniqueTags:
        fd_w = openFile("Pattern_" + tag + "_111508043.txt", "w")
        fd_w.write(lineFormat.format("W(i - 2)", "T(i - 2)", "W(i - 1)", "T(i - 1)", "W(i + 1)", "T(i + 1)", "W(i + 2)", "T(i + 2)"))
        fd_w.write("\n")
        
        if tag in tagContext:
            for l in tagContext[tag]:
                fd_w.write(lineFormat.format(l[0], l[1], l[2], l[3], l[4], l[5], l[6],l[7]))
                fd_w.write("\n")
        fd_w.close()

def getExpectedTags(line):
    tags = list()
    tokens = word_tokenize(line)

    for token in tokens:
        try:
            (word, tag) = token.split("_")
        except ValueError as e:
            (word, tag) = (token, "O")
        except Exception as e:
            print(e)
            raise SystemExit
        tags.append(tag)
    return tags

def recognizeEntities(line):
    try:
        tagger = StanfordNERTagger("Stanford-NER/english.muc.7class.distsim.crf.ser.gz", "Stanford-NER/stanford-ner.jar", encoding = "utf-8")
    except LookupError as e:
        print(e)
        raise SystemExit

    tokens = word_tokenize(line)
    taggedTokens = tagger.tag(tokens)
    return taggedTokens

def openFile(filename, mode):
    try:
        fd = open(filename, mode)
    except IOError as e:
        print(e)
        raise SystemExit
    return fd

def main():
    # Command Line Argument Parsing
    parser = argparse.ArgumentParser(description = "A simple implementation Named Entity Recognizer using Stanford NER.")
    parser.add_argument("test_file", help = "File containing test data.")
    args = parser.parse_args()

    fd_r = openFile(args.test_file, "r")
    fd_w = openFile("NER_labelled_Corpus_111508043.txt", "w")
    
    tagCount = dict()
    tagContext = dict()
    for line in fd_r:
        tags = recognizeEntities(line)
        for (index,  (word, tag)) in enumerate(tags):
            fd_w.write(word)
            if tag != "O":
                fd_w.write("_" + tag)
                
                if tag not in tagCount:
                    tagCount[tag] = 1
                else:
                    tagCount[tag] += 1

                if tag not in tagContext:
                    tagContext[tag] = list()

                size = len(tags)
                if 1 < index < (size - 2):
                    tagContext[tag].append([tags[index - 2][0], nltk.pos_tag([tags[index - 2][0]])[0][1], tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1],tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1],tags[index + 2][0], nltk.pos_tag([tags[index + 2][0]])[0][1]])
                elif index == 0:
                    if index < (size - 2):
                        tagContext[tag].append(["*", "*", "*", "START",tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1],tags[index + 2][0], nltk.pos_tag([tags[index + 2][0]])[0][1]])
                    elif index == (size - 2):
                        tagContext[tag].append(["*", "*", "*", "START",tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1],"*", "END"])
                    else:
                        tagContext[tag].append(["*", "*", "*", "START","*", "END","*", "*"])
                elif index == 1:
                    if index < (size - 2):
                        tagContext[tag].append(["*", "START", tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1], tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1], tags[index + 2][0], nltk.pos_tag([tags[index + 2][0]])[0][1]])
                    elif index == (size - 2):
                        tagContext[tag].append(["*", "START", tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1], tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1],"*", "END"])
                    else:
                        tagContext[tag].append(["*", "START", tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1], "*", "END", "*", "*"])
                elif index == (size - 2):
                    if index > 1:
                        tagContext[tag].append([tags[index - 2][0], nltk.pos_tag([tags[index - 2][0]])[0][1], tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1],tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1],"*", "END"])
                    elif index == 1:
                        tagContext[tag].append(["*", "START", tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1],tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1],"*", "END"])
                    else:    
                        tagContext[tag].append(["*", "*", "*", "START",tags[index + 1][0], nltk.pos_tag([tags[index + 1][0]])[0][1],"*", "END"])
                elif index == (size - 1):
                    if index > 1:
                        tagContext[tag].append([tags[index - 2][0], nltk.pos_tag([tags[index - 2][0]])[0][1], tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1], "*", "END","*", "*"])
                    elif index == 1:
                        tagContext[tag].append(["*", "START", tags[index - 1][0], nltk.pos_tag([tags[index - 1][0]])[0][1], "*", "END","*", "*"])
                    else:    
                        tagContext[tag].append(["*", "*", "*", "START", "*", "END","*", "*"])

            if (word, tag) != tags[-1]:
                fd_w.write(" ")
            else:
                fd_w.write("\n")
    fd_w.close()
    fd_r.close()

    writeStatistics(tagCount, tagContext)
    

if __name__ == '__main__':
    main()
