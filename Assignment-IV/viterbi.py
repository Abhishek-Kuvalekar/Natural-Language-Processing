#!/usr/bin/python3

import argparse
import os.path
import pickle
import re
import nltk
from sklearn.metrics import precision_recall_fscore_support as score

def getStatistics(finalTagSequence, finalExpectedTagSequence):
    uniqueTags = list()
    floatFormat = "{:.2f}"
    
    for tag in finalTagSequence:
        if tag not in uniqueTags:
            uniqueTags.append(tag)
    precision, recall, fscore, support = score(finalExpectedTagSequence, finalTagSequence)
    
    fd_w = openFile("statistics.txt", "w")
    fd_w.write('{:5} {:10} {:10} {:10}'.format("Tag", "Precision", "Recall", "F-Measure"))
    fd_w.write("\n")
    
    for (t, p, r, f) in zip(uniqueTags, precision, recall, fscore):
        fd_w.write('{:5} {:10} {:10} {:10}'.format(str(t), str(floatFormat.format(p)), str(floatFormat.format(r)), str(floatFormat.format(f))))
        fd_w.write("\n")
    
    fd_w.close()


def getExpectedTagSequence(words):
    tagTuples = nltk.pos_tag(words)
    tagSequence = list()
    for (word, tag) in tagTuples:
        tagSequence.append(tag)
    return tagSequence

def calculateEmissionProbability(word, tag, tagCount, emissionCount):
    if tag in emissionCount:
        if word in emissionCount[tag]:
            return (emissionCount[tag][word] / tagCount[tag])
        else:
            return 0.000001
    else:
        return 0.000001

def calculateTransitionProbability(previousTag, currentTag, tagCount, transitionCount):
    if previousTag in transitionCount:
        if currentTag in transitionCount[previousTag]:
            return (transitionCount[previousTag][currentTag] / tagCount[previousTag])
        else:
            return 0.000001
    else:
        return 0.000001

def getWords(line): 
    words = list()
    for word in line.split():
        w = re.match(r"""\w+""", word)
        if w != None:
            w = w.group()
            words.append(w)
        w = re.search(r"""[!"#$%&'()*+,-./:;<=>?@\[\\\]^_`{\|}~]""", word)
        if w != None:
            w = w.group()
            words.append(w)
    return words

def viterbi(line, tagCount, emissionCount, transitionCount):
    pathProbability = list()
    backpointers = list()
    tags = [tag for tag in tagCount]
    numberOfTags = len(tags)
    words = getWords(line)
    numberOfWords = len(words)
    for i in range(0, numberOfTags):
        pathProbability.append([-1] * numberOfWords)
        backpointers.append([-1] * numberOfWords)

    for i in range(0, numberOfTags):
        pathProbability[i][0] = calculateTransitionProbability("START", tags[i], tagCount, transitionCount) * calculateEmissionProbability(words[0], tags[i], tagCount, emissionCount)
        backpointers[i][0] = -1

    for t in range(1, numberOfWords):
        for s in range(numberOfTags):
            maxProbability = -1
            maxTempProbability = -1
            argmax = -1
            for p in range(numberOfTags):
                probability = pathProbability[p][t - 1] * calculateTransitionProbability(tags[p], tags[s], tagCount, transitionCount) * calculateEmissionProbability(words[t], tags[s], tagCount, emissionCount)
                tempProbability = pathProbability[p][t - 1] * calculateTransitionProbability(tags[p], tags[s], tagCount, transitionCount)
                if probability > maxProbability:
                    maxProbability = probability
                if tempProbability > maxTempProbability:
                    maxTempProbability = tempProbability
                    argmax = p
            
            pathProbability[s][t] = maxProbability
            backpointers[s][t] = argmax
    
    maxProbability = -1
    argmax = -1
    for p in range(numberOfTags):
        probability = pathProbability[p][-1] * calculateTransitionProbability(tags[p], "END", tagCount, transitionCount)
        if probability > maxProbability:
            maxProbability = probability
            argmax = p
    
    finalTags = [tags[argmax]]
    count = numberOfWords - 1
    for i in range(numberOfWords - 1):
        num = backpointers[argmax][count]
        argmax = num
        count -= 1
        finalTags.insert(0, tags[argmax])

    return finalTags

def loadTrainedModel(filename):
    fd_r = openFile(filename, "rb")
    return pickle.load(fd_r)

def openFile(filename, mode):
    try:
        fd = open(filename, mode)
    except IOError as e:
        print(e)
        raise SystemExit
    return fd

def trainModel(trainingFile):
    #Dictionaries storing counts for tags, emissions and transitions
    tagCount = dict()
    emissionCount = dict()
    transitionCount = dict()
    tagCount["START"] = 0
    tagCount["END"] = 0

    fd_r = openFile(trainingFile, "r")
    for line in fd_r:
        tagCount["START"] += 1
        tagCount["END"] += 1
        previousTag = "START"
        taggedWords = line.split()
        for taggedWord in taggedWords:
            (word, tag) = taggedWord.rsplit("_", 1)
            
            if tag not in tagCount:
                tagCount[tag] = 1
            else:
                tagCount[tag] += 1

            if tag not in emissionCount:
                emissionCount[tag] = dict()
            if word not in emissionCount[tag]:
                emissionCount[tag][word] = 1
            else:
                emissionCount[tag][word] += 1

            if previousTag not in transitionCount:
                transitionCount[previousTag] = dict()
            if tag not in transitionCount[previousTag]:
                transitionCount[previousTag][tag] = 1
            else:
                transitionCount[previousTag][tag] += 1
            previousTag = tag

        finalWord, finalTag = taggedWords[-1].rsplit("_", 1)
        if finalTag not in transitionCount:
            transitionCount[finalTag] = dict()
        if "END" not in transitionCount[finalTag]:
            transitionCount[finalTag]["END"] = 1
        else:
            transitionCount[finalTag]["END"] += 1
    
    fd_r.close()
    
    fd_w = openFile("count_tags.pickle", "wb")
    pickle.dump(tagCount, fd_w, -1)
    fd_w.close()

    fd_w = openFile("count_emission.pickle", "wb")
    pickle.dump(emissionCount, fd_w, -1)
    fd_w.close()

    fd_w = openFile("count_transition.pickle", "wb")
    pickle.dump(transitionCount, fd_w, -1)
    fd_w.close()


def main():
    #Argument Parsing
    parser = argparse.ArgumentParser(description = "A simple POS Tagger.")
    parser.add_argument("training_file", help = "A file containing training data.")
    parser.add_argument("test_file", help = "A file containing test data.")
    args = parser.parse_args()
    
    #If model is previously trained then use that data otherwise train a model and save it for future use
    if (not os.path.isfile("count_tags.pickle")) or (not os.path.isfile("count_emission.pickle")) or (not os.path.isfile("count_transition.pickle")):
        trainModel(args.training_file)
    
    tagCount = loadTrainedModel("count_tags.pickle")
    emissionCount = loadTrainedModel("count_emission.pickle")
    transitionCount = loadTrainedModel("count_transition.pickle")
    
    fd_r = openFile(args.test_file, "r")
    fd_w = openFile("output.txt", "w")
    finalTagSequence = list()
    finalExpectedTagSequence = list()
    for line in fd_r:
        tagSequence = viterbi(line, tagCount, emissionCount, transitionCount)
        words = getWords(line)
        finalTagSequence += tagSequence
        finalExpectedTagSequence += getExpectedTagSequence(words)
        for (word, tag) in zip(words, tagSequence):
            fd_w.write(word + "_" + tag)
            if (word, tag) == (words[-1], tagSequence[-1]):
                fd_w.write("\n")
            else:
                fd_w.write(" ")
    fd_r.close()
    fd_w.close()
   
    getStatistics(finalTagSequence, finalExpectedTagSequence)

if __name__ == '__main__':
    main()
