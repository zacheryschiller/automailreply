# !/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

## AutoMailReply

## Author: Zachery Schiller
## Email: zacheryschiller@gmail.com

import email
keywordList = []

################ Email ################

## Open up an email and read it matching it's fields
def readEmail(filename):
    if filename == None:
    	return 
    message = email.Parser.Parser().parse(open(filename, 'r'))
    print 'To: %s' % message ['to']
    print 'From: %s' % message['from']
    print 'Subject: %s' % message['subject']
    parts = message.get_payload()
    msg = parts[0].get_payload()
    print parts[1].get_payload()
    return msg

## Search through a message for keywords
## Pull in keywords from known keywords + look for new ones
def checkKeywords(msg):
    matchedKeywords = []
    msg = msg.split(' ')
    for i in range(len(msg)):
    	for j in range(len(keywordList)):
    	    if keywordList[j][0] == msg[i]:
    	        matchedKeywords.append(keywordList[j])
    return matchedKeywords

################ Keywords ################

## Load keywords from file
def loadKeywords():
    global keywordList
    fin = open("keywords.txt",'r')
    data = fin.readlines()
    keywordList = []
    for i in range(len(data)):
	line = data[i]
	line = line.split(',')
	keywordList.append([line[0],line[1][:-1]])
    fin.close()

## Add keyword to keyword file
## Takes in newKeyword and returns T/F if added
## Checks to ensure not adding a duplicate
def addKeyword(newKeyword):
    # Todo: fix with updated global keywordList
    fin = open("keywords.txt",'r+')
    data = fin.readlines()
    #print newKeyword in keywordList
    for i in range(len(data)):
	line = data[i]
	line = line.split(',')
	if (line[0] == newKeyword):
	    fin.close()
	    return False
    s = str(newKeyword)+",0\n"
    fin.write(s)
    fin.close()
    return True

## Remove keyword from keyword file
## Takes in keyword to remove and returns updated keyword list
def removeKeyword(remKeyword):
    # Todo: fix with updated global keywordList and remove
    fin = open("keywords.txt",'r')
    data = fin.readlines()
    for i in range(len(data)):
	line = data[i]
	line = line.split(',')
	if (line[0] == remKeyword):
	    data.pop[line]
	    #fin.close()
	    #fin = open("keywords.txt",'w')
	    #return True
    fin.close()

################ Main ################

## Main function that runs
def main():
    loadKeywords()
    msg = readEmail("testEmail1.txt")
    #print keywordList
    #print ("Keywords Matched: %s" % checkKeywords(msg))
    print (addKeyword("password"))

################ Run Program ################

main()
