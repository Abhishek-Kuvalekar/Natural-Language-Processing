#! /usr/bin/python3
import re
import argparse

def tokenizeTweet(line):
    return line.split()

def openFile(filename, mode):
    """Opens file 'filename' in mode 'mode' and checks errors"""
    try:
        f = open(filename, mode)
    except IOError as e:
        print(e)
    else:
        return f

def main():
    """Start of the program"""
    #Command Line Argument Parsing
    parser = argparse.ArgumentParser(description = "Tweet Tokenizer")
    parser.add_argument("file", help = "Name of the file which contains tweets")
    args = parser.parse_args()

    #Open file containing tweets
    fd_r = openFile(args.file, "r")
    if(fd_r == None):
        return
    
    #Read file line by line and store the tokens in a list
    tweets = list()
    tokensList = list()
    for line in fd_r:
        tweets.append(line)
        tokensList.append(tokenizeTweet(line))

    #Open output file and write tokens in a specified format
    fd_w = openFile("output.txt", "w")
    if(fd_w == None):
        return
    for (tweet, tokens) in zip(tweets, tokensList):
        #fd_w.write(str(tweet))                                  #Tweet
        print(str(tweet), end = "")                 #Tweet
        #fd_w.write(str(len(tokens)) + "\n")                     #Number of tokens in a tweet
        print(str(len(tokens)))                     #Number of tokens in a tweet
        for token in tokens:
            #fd_w.write(str(token) + "\n")                       #Tokens in a tweet
            print(str(token))                       #Tokens in a tweet


    fd_r.close()
    fd_w.close()

if __name__ == '__main__':
    main()
