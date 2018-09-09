#! /usr/bin/python3
import argparse
from collections import OrderedDict
import string
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

def getWordFrequency(words):
    wordDict = OrderedDict()
    for word in words:
        if word not in wordDict:
            wordDict[word] = 1
        else:
            wordDict[word] += 1
    return wordDict

def getLemmatizedTokens(tokens):
    stopwordsList = stopwords.words('english')
    wordnetLemmatizer = WordNetLemmatizer()
    lemmatizedTokens = list()
    for token in tokens:
        if token.startswith("CF:D") or token.startswith("CF:T"):
            pass
        elif token.isdigit():
            continue
        elif token in string.punctuation:
            continue
        elif token in stopwordsList:
            continue
        else:
            if(wordnet.synsets(token)):
                token = wordnetLemmatizer.lemmatize(token, pos = wordnet.synsets(token)[0].pos())
            token = token.lower()

        lemmatizedTokens.append(token)
    return lemmatizedTokens

def openFile(filename, mode):                                                             
    """Opens file 'filename' in mode 'mode' and checks errors"""                          
    try:                                                                                  
        f = open(filename, mode)                                                          
    except IOError as e:                                                                  
        print(e)                                                                          
    else:                                                                                                                                 
        return f

def main():
    parser = argparse.ArgumentParser(description = "Basic Text Processing")
    parser.add_argument("input_file", help = "File which contains one token per line")
    args = parser.parse_args()
    
    fd_r = openFile(args.input_file, "r")
    if(fd_r == None):
        return
    fd_w = openFile("output.txt", "w")
    if(fd_w == None):
        return

    tokens = list()
    for token in fd_r:
        tokens.append(token)

    tokens = getLemmatizedTokens(list(map((lambda t: t.replace("\n", "").strip()), tokens)))
    tokens = getWordFrequency(tokens)
    
    for word in tokens:
        fd_w.write(word + " " + str(tokens[word]) + "\n")
        fd_w.flush()

    fd_w.close()
    fd_r.close()
    
if __name__ == '__main__':
    main()
