#! /usr/bin/python3
import re
import argparse
import string

class Normalizer:
    irregular_verbs = ["beaten","become","begun","bet","blown","broken","brought","built","burst","bought","caught","chosen","come","cost","cut","dealt","done","drawn","drunk","driven","eaten","fallen","fed","felt","fought","found","flown","forgotten","frozen","got","gotten","given","gone","grown","hung","had","heard","hidden","hit","held","hurt","kept","known","laid","led","left","lent","let","lain","lit","lost","made","meant","met","paid","put","read","ridden","rung","risen","run","said","seen","sold","sent","set","shaken","stolen","shone","shot","shown","shut","sung","sunk","sat","slept","slid","spoken","spent","sprung","stood","stuck","sworn","swept","swum","swung","taken","taught","torn","told","thought","thrown","understood","woken","worn","woven","won","written","burnt","dreamt","learnt","smelt","spelt","gone"]

    def __init__(self):
        pass
    
    def resolveClitic(self, currentToken, nextToken = None):
        word, abbr = currentToken.split("'")
        abbr = abbr.lower()
        if("m" == abbr):
            return [word, "am"]
        elif("re" == abbr):
            return [word, "are"]
        elif("ve" == abbr):
            return [word, "have"]
        elif("ll" == abbr):
            if word.lower() in ["i", "we"]:
                return [word, "shall"]
            else:
                return [word, "will"]
        elif("d" == abbr):
            if (nextToken.lower()[-2:] in ["ed", "en", "un", "ht", "wn"]) or (nextToken.lower() in Normalizer.irregular_verbs):
                return [word, "had"]
            else:
                if word.lower() in ["i", "we"]:
                    return [word, "should"]
                else:
                    return [word, "would"]
        elif("s" == abbr):
            if nextToken.lower()[-3:] == "ing":
                return [word, "is"]
            elif (nextToken.lower()[-2:] in ["ed", "en", "un", "ht", "wn"]) or (nextToken.lower() in Normalizer.irregular_verbs):
                return [word, "has"]
            else:
                return [word, "'s"]
        elif("t" == abbr):
            if word.lower() == "can":
                return [word, "not"]
            else:
                return [word[:-1], "not"]
        else:
            return [currentToken]
    
    def resolveHyphenatedWord(self, currentToken):
        word1, word2 = currentToken.split("-")
        if word2.istitle():
            return [word1, "-", word2]
        else:
            return [word1, "-" + word2]

    def normalizeTweetTokens(self, tokens):
        normalizedTokens = list()
        tok_length = len(tokens)
        for i in range(0, tok_length):
            if(tokens[i][0] == "#"):
                normalizedTokens.append(tokens[i])
            elif(tokens[i][0] == "@"):
                normalizedTokens.append(tokens[i])
            elif("'" in tokens[i]):
                if(i != (tok_length - 1)):
                    normalizedTokens.extend(self.resolveClitic(tokens[i], nextToken = tokens[i + 1]))
                else:
                    normalizedTokens.extend(self.resolveClitic(tokens[i]))
            elif("-" in tokens[i]):
                normalizedTokens.extend(self.resolveHyphenatedWord(tokens[i]))
            elif(" " in tokens[i]):
                normalizedTokens.append(tokens[i].replace(" ", ""))
            else:
                normalizedTokens.append(tokens[i])
        return normalizedTokens

class Tokenizer:
    tokenSpecification = [
            ("URL", r"""(?:http[s]?://|ftp://|http[s]?://www\.|www\.|ftp://www\.)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"""),
            ("EMAIL", r"""(?:\w+[.-_#$%^&*!]\w+[@](?:(?:\w+[.])+\w+))"""),
            ("USERNAME", r"""@\w+[!"#$%&'()*+,-./:;<=>?@\[\\\]^_`{\|}~]*\w*"""),
            ("HASHTAG", r"""#[^\s]+"""),
            ("HYPHENATED_WORD", r"""\w+[-]\w+"""),
            ("CLITIC", r"""\w+'[\w]{1,2}"""),
            ("ABBREVIATION", r"""(?:[A-Z][a-z]*[.]\s*)+"""),
            ("WORD", r"""\b\w+\b"""),
            ("PUNCTUATION", r"""[!"#$%&'()*+,-./:;<=>?@\[\\\]^_`{\|}~]""")
    ]

    def __init__(self):
        self._loadEmojis()
        pass
    
    def _loadEmojis(self):
        fd_r = openFile("data/emojis.txt", "r")
        self.emojis = list()
        if(fd_r == None):
            return
        for emoji in fd_r:
            emoji = re.escape(emoji.strip())
            self.emojis.append(emoji)
        emoji_regex = r'|'.join('%s' % emoji for emoji in self.emojis)
        Tokenizer.tokenSpecification.insert(-2, ("EMOJI", emoji_regex))

    def tokenizeTweet(self, line):
        regex = '|'.join('%s' % pattern for (keyword, pattern) in Tokenizer.tokenSpecification)
        p = re.compile(regex, re.UNICODE)
        normalizer = Normalizer()
        return normalizer.normalizeTweetTokens(p.findall(line))

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
    tokenizer = Tokenizer()
    tweets = list()
    tokensList = list()
    for line in fd_r:
        tweets.append(line)
        tokensList.append(tokenizer.tokenizeTweet(line.strip()))

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
