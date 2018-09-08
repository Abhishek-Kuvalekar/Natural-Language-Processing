#! /usr/bin/python3
import re
import argparse
import string

class Normalizer:
    irregular_verbs = ["beaten","become","begun","bet","blown","broken","brought","built","burst","bought","caught","chosen","come","cost","cut","dealt","done","drawn","drunk","driven","eaten","fallen","fed","felt","fought","found","flown","forgotten","frozen","got","gotten","given","gone","grown","hung","had","heard","hidden","hit","held","hurt","kept","known","laid","led","left","lent","let","lain","lit","lost","made","meant","met","paid","put","read","ridden","rung","risen","run","said","seen","sold","sent","set","shaken","stolen","shone","shot","shown","shut","sung","sunk","sat","slept","slid","spoken","spent","sprung","stood","stuck","sworn","swept","swum","swung","taken","taught","torn","told","thought","thrown","understood","woken","worn","woven","won","written","burnt","dreamt","learnt","smelt","spelt","gone"]

    def __init__(self):
        """Constructor"""
        pass
    
    def resolveClitic(self, currentToken, nextToken = None):
        """Resolves clitics depending on the current and next token"""
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
            if word.lower() == "let":
                return [word, "us"]
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
        """Resolves Hyphenated words"""
        word1, word2 = currentToken.split("-")
        if word2.istitle():
            return [word1, "-", word2]
        else:
            return [word1, "-" + word2]

    def resolveDate(self, currentToken):
        """Resolves Date and converts it into a standard canonical format CF:D:yyyy-mm-dd"""
        resolvedDate = "CF:D:"
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        dd_mmm_yyyy = re.compile(r"""(?:(?:(?:(?:[012]?[0-9]|3[01])(?:st|nd|rd|th)?)?)?\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:(?:(?:\s*[012]?[0-9]|3[01])(?:st|nd|rd|th)?)?)?(?:[,']\s*(?:[1-9][0-9])?[0-9]{2})?)""")
        mmm_yyyy = re.compile(r"""(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:[,']\s*(?:[1-9][0-9])?[0-9]{2})""")
        dd_mm_yyyy = re.compile(r"""(?:[012]?[0-9]|3[01])[/.\|](?:0?[1-9]|1[012])[/.\|](?:[1-9][0-9])?[0-9]{2}""")
        yyyy_mm_dd = re.compile(r"""(?:[1-9][0-9])?[0-9]{2}[/.\|](?:0?[1-9]|1[012])[/.\|](?:[012]?[0-9]|3[01])""")
        mm_dd_yyyy = re.compile(r"""(?:0?[1-9]|1[012])[/.\|](?:[012]?[0-9]|3[01])[/.\|](?:[1-9][0-9])?[0-9]{2}""")
        day_re = re.compile(r"""(?:(?:(?:3[01])|(?:[12]0)|(?:[012]?[1-9]))(?:st|nd|rd|th)?)""")
        month_re = re.compile(r"""[a-zA-Z]{3,9}""")
        year_re = re.compile(r"""\d{2,5}$""")
        split_re = re.compile(r"""[/.\|,' ]+""")
        try:
            #Formats like Jul'2018
            if(mmm_yyyy.match(currentToken)):
                toks = split_re.split(currentToken)
                (date, month, year) = (None, toks[0], toks[1])
                for i in range(0, 12):
                    if(month == None):
                        break
                    if(month in months[i]):
                        month = i + 1
                        if(month < 10):
                            month = "0" + str(month)
                        else:
                            month = str(month)
                        break
            #Formats like 23 Apr, 2018/23rd Apr, 2018/Apr 23, 2018/Apr 23rd, 2018
            elif(dd_mmm_yyyy.match(currentToken)):
                toks = split_re.split(currentToken)
                (date, month, year) = (None, None, None)
                toks = [tok for tok in toks if tok != ""]
                for i in range(0, len(toks)):
                    if(i == 2):
                        year = toks[i]
                    else:
                        if(month == None):
                            month = month_re.match(toks[i])
                            if(month != None):
                                month = month.group()
                        if(date == None):
                            date = day_re.match(toks[i])
                            if(date != None):
                                date = date.group()[0:2] 
                for i in range(0, 12):
                    if(month == None):
                        break
                    if(month in months[i]):
                        month = i + 1
                        if(month < 10):
                            month = "0" + str(month)
                        else:
                            month = str(month)
                        break
            #Formats like mm/dd/yyyy or mm/dd/yy
            elif(mm_dd_yyyy.match(currentToken)):
                month, date, year = split_re.split(currentToken)
            #Formats like dd/mm/yyyy or dd/mm/yy
            elif(dd_mm_yyyy.match(currentToken)):
                date, month, year = split_re.split(currentToken)
            #Formats like yyyy/mm/dd
            elif(yyyy_mm_dd.match(currentToken)):
                year, month, date = split_re.split(currentToken)
            
            #Resolves year
            if(year == None):
                resolvedDate += "????" + "-"
            else:
                resolvedDate += str(year) + "-"
            
            #Resolves month
            if(month != None):
                resolvedDate += str(month) + "-"
            
            #Resolved date
            if(date != None):
                resolvedDate += str(date)
            else:
                resolvedDate = resolvedDate[0:-1]
                
            return resolvedDate
        except:
            return currentToken

    def resolveTime(self, currentToken):
        """Resolves time and converts it into a canonical format CF:T:time:timezone"""
        resolvedTime = "CF:T:"
        zone_string = r"""|""".join(Tokenizer.timezones)
        timezone_re = re.compile(zone_string)
        am_re = re.compile(r"""[Aa][mM]""")
        pm_re = re.compile(r"""[Pp][mM]""")
        oclock_re = re.compile(r"""o'clock|O'Clock|O'CLOCK""")
        time_re = re.compile(r"""(?:2[0-4]|[01]?[0-9])(?:[.:]?[0-5][0-9])?""")
        split_re = re.compile(r"""[.:]""")

        time = time_re.search(currentToken).group()
        oclock, am, pm, timezone = None, None, None, None
        oclock = oclock_re.search(currentToken)
        
        #Check if o'clock/am/pm is present
        if(oclock == None):
            am = am_re.search(currentToken)
            if(am == None):
                pm = pm_re.search(currentToken)
                if(pm != None):
                    pm = pm.group()
            else:
                am = am.group()
        else:
            oclock = oclock.group()

        #Check if timezone is present    
        timezone = timezone_re.search(currentToken)
        if(timezone != None):
            timezone = timezone.group()

        try:
            hour, minute = split_re.split(time)
        except:
            hour = split_re.split(time)[0]
            minute = None
        
        #Convert 12 hour format to 24 hour format if it is PM
        if(pm != None):
            if(int(hour) < 12):
                hour = str(int(hour) + 12)
        
        #Resolve time        
        resolvedTime += str(hour) 
        if(minute != None) and (minute != "00"):
            resolvedTime += str(minute)
        else:
            resolvedTime += "00"

        #Resolve timezone if present
        if(timezone != None):
            resolvedTime += ":" + timezone
        return resolvedTime

    def normalizeTweetTokens(self, tokens):
        """Tweet Normalization"""
        normalizedTokens = list()
        tok_length = len(tokens)
        for i in range(0, tok_length):
            if(tokens[i][0] == "#"):                                                                        #Hashtag
                normalizedTokens.append(tokens[i])
            elif(tokens[i][0] == "@"):                                                                      #User Reference
                normalizedTokens.append(tokens[i])
            elif(re.match(Tokenizer.tokenSpecification[4][1], tokens[i]) != None):                          #Date
                normalizedTokens.append(self.resolveDate(tokens[i].strip()))
            elif(re.match(Tokenizer.tokenSpecification[5][1], tokens[i]) != None):                          #Time
                normalizedTokens.append(self.resolveTime(tokens[i].strip()))
            elif("'" in tokens[i]):                                                                         #Clitic
                if(i != (tok_length - 1)):
                    normalizedTokens.extend(self.resolveClitic(tokens[i], nextToken = tokens[i + 1]))
                else:
                    normalizedTokens.extend(self.resolveClitic(tokens[i]))
            elif("-" in tokens[i]):                                                                         #Hyphenated Word
                normalizedTokens.extend(self.resolveHyphenatedWord(tokens[i]))
            elif(" " in tokens[i]):                                                                         #Any other token
                normalizedTokens.append(tokens[i].replace(" ", ""))
            else:                                                                                           #Exceptions        
                normalizedTokens.append(tokens[i])
        return normalizedTokens

class Tokenizer:
    tokenSpecification = [
            ("URL", r"""(?:http[s]?://|ftp://|http[s]?://www\.|www\.|ftp://www\.)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"""),
            ("EMAIL", r"""(?:\w+(?:[.\-_#$%^&*!]\w+)?[@](?:(?:\w+[.])+\w+))"""),
            ("USERNAME", r"""@\w+[!"#$%&'()*+,-./:;<=>?@\[\\\]^_`{\|}~]*\w*"""),
            ("HASHTAG", r"""#[^\s]+"""),
            ("DATE", r"""(?:[012]?[0-9]|3[01])[/.\|](?:0?[1-9]|1[012])[/.\|](?:[1-9][0-9])?[0-9]{2}|(?:[1-9][0-9])?[0-9]{2}[/.\|](?:0?[1-9]|1[012])[/.\|](?:[012]?[0-9]|3[01])|(?:0?[1-9]|1[012])[/.\|](?:[012]?[0-9]|3[01])[/.\|](?:[1-9][0-9])?[0-9]{2}|(?:(?:(?:(?:[012]?[0-9]|3[01])(?:st|nd|rd|th)?)?)?\s*(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:(?:(?:\s*[012]?[0-9]|3[01])(?:st|nd|rd|th)?)?)?(?:[,']\s*(?:[1-9][0-9])?[0-9]{2})?)"""),
            ("TIME", r"""(?:2[0-4]|[01]?[0-9])(?:[.:]?[0-5][0-9])?\s*(?:(?:[APap][Mm])|(?:o'clock|O'Clock|O'CLOCK))?"""),
            ("HYPHENATED_WORD", r"""\w+[-]\w+"""),
            ("CLITIC", r"""\w+'[\w]{1,2}"""),
            ("ABBREVIATION", r"""(?:[A-Z][a-z]*[.]\s*)+"""),
            ("WORD", r"""\b\w+\b"""),
            ("PUNCTUATION", r"""[!"#$%&'()*+,-./:;<=>?@\[\\\]^_`{\|}~]""")
    ]
    timezones = []

    def __init__(self):
        """Constructor"""
        self._loadEmojis()
        self._loadTimeZones()
        Tokenizer.timezones.extend(self.timezones)
        pass
    
    def _loadEmojis(self):
        """Loads emojis stored in data/emojis.txt into a list and create a regex"""
        fd_r = openFile("data/emojis.txt", "r")
        self.emojis = list()
        if(fd_r == None):
            return
        for emoji in fd_r:
            emoji = re.escape(emoji.strip())
            self.emojis.append(emoji)
        emoji_regex = r'|'.join('%s' % emoji for emoji in self.emojis)
        Tokenizer.tokenSpecification.insert(-2, ("EMOJI", emoji_regex))

    def _loadTimeZones(self):
        """Loads timezones stored in data/timezones.txt into a list and create a regex"""
        fd_r = openFile("data/timezones.txt", "r")
        self.timezones = list()
        if(fd_r == None):
            return
        for timezone in fd_r:
            timezone = re.escape(timezone.strip())
            self.timezones.append(timezone)
        timezone_regex = r'|'.join('%s' % timezone for timezone in self.timezones)
        time_regex = Tokenizer.tokenSpecification[5][1]
        time_regex = r"""(?:(?:""" +  timezone_regex + r""")\s*)?""" + time_regex + r"""(?:\s*(?:""" + timezone_regex + r"""))?"""
        Tokenizer.tokenSpecification.pop(5)
        Tokenizer.tokenSpecification.insert(5, ("TIME", time_regex))

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
    fd_w_bigram = openFile("bigram-output.txt", "w")
    fd_w_trigram = openFile("trigram-output.txt", "w")
    fd_w_4_gram = openFile("4-gram-output.txt", "w")
    fd_w_5_gram = openFile("5-gram-output.txt", "w")
    if (fd_w_bigram == None) or (fd_w_trigram == None) or (fd_w_4_gram == None) or (fd_w_5_gram == None) :
        return
    for (tweet, tokens) in zip(tweets, tokensList):
        tokensLength = len(tokens)
        hasLooped = False
        for i in range(0, tokensLength - 1):
            fd_w_bigram.write(tokens[i] + " " + tokens[i + 1] + "\n")
            hasLooped = True
        if not hasLooped:
            fd_w_bigram.write(tokens[0] + "\n")
        fd_w_bigram.write("\n")

        hasLooped = False
        for i in range(0, tokensLength - 2):
            fd_w_trigram.write(tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2] + "\n")
            hasLooped = True
        if not hasLooped:
            for token in tokens:
                fd_w_trigram.write(token)
                if not token == tokens[tokensLength - 1]:
                    fd_w_trigram.write(" ")
            fd_w_trigram.write("\n")
        fd_w_trigram.write("\n")
        
        hasLooped = False
        for i in range(0, tokensLength - 3):
            fd_w_4_gram.write(tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2] + " " + tokens[i + 3] + "\n")
            hasLooped = True
        if not hasLooped:
            for token in tokens:
                fd_w_4_gram.write(token)
                if not token == tokens[tokensLength - 1]:
                    fd_w_4_gram.write(" ")
            fd_w_4_gram.write("\n")
        fd_w_4_gram.write("\n")
        
        hasLooped = False
        for i in range(0, tokensLength - 4):
            fd_w_5_gram.write(tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2] + " " + tokens[i + 3] + " " + tokens[i + 4] + "\n")
            hasLooped = True
        if not hasLooped:
            for token in tokens:
                fd_w_5_gram.write(token)
                if not token == tokens[tokensLength - 1]:
                    fd_w_5_gram.write(" ")
            fd_w_5_gram.write("\n")
        fd_w_5_gram.write("\n")

    fd_r.close()
    fd_w_bigram.close()
    fd_w_trigram.close()
    fd_w_4_gram.close()
    fd_w_5_gram.close()

if __name__ == '__main__':
    main()
