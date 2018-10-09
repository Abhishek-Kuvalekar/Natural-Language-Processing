#! /usr/bin/python3

import argparse
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import re
from sklearn.metrics import precision_recall_fscore_support as score

def writeStatistics(precision, recall, fscore, fd_w):
    uniqueTags = ["PERSON", "LOCATION", "ORGANIZATION", "DATE", "TIME"]
    floatFormat = "{:.5f}"
    lineFormat = "{:15} {:15} {:15} {:15}"

    fd_w.write(lineFormat.format("TAG", "PRECISION", "RECALL", "F-MEASURE"))
    fd_w.write("\n")

    for (t, p, r, f) in zip(uniqueTags, precision, recall, fscore):
        fd_w.write(lineFormat.format(str(t), str(floatFormat.format(p)), str(floatFormat.format(r)), str(floatFormat.format(f))))
        fd_w.write("\n")

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
    parser.add_argument("manually_tagged_file", help = "Manually tagged file.")
    args = parser.parse_args()

    fd_r = openFile(args.test_file, "r")
    fd_w = openFile("output.txt", "w")
    predictedTags = list()
    for line in fd_r:
        tags = recognizeEntities(line)
        for (word, tag) in tags:
            predictedTags.append(tag)
            fd_w.write(word)
            if tag != "O":
                fd_w.write("_" + tag)
            if (word, tag) != tags[-1]:
                fd_w.write(" ")
            else:
                fd_w.write("\n")
    fd_w.close()
    fd_r.close()
    
    fd_r = openFile(args.manually_tagged_file, "r")
    expectedTags = list()
    for line in fd_r:
        expectedTags += getExpectedTags(line)
    
    (precision, recall, fscore, support) = score(expectedTags, predictedTags)
    fd_w = openFile("statistics.txt", "w")
    writeStatistics(precision, recall, fscore, fd_w)
    fd_w.close()

if __name__ == '__main__':
    main()
