# !/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

## AutoMailReply

## Author: Zachery Schiller
## Email: zacheryschiller@gmail.com

import email
import numpy
import scipy
from gensim import corpora, models, similarities
keywordList = []

################ Email ################

## Open up an email and read it matching it's fields
def readEmail(filename):
    if filename == None:
    	print "No filename!"
        return None
    message = email.Parser.Parser().parse(open(filename, 'r'))
    #print 'To: %s' % message ['to']
    #print 'From: %s' % message['from']
    #print 'Subject: %s' % message['subject']
    parts = message.get_payload()
    msg = parts[0].get_payload()
    msg = msg + ' ' + message['from']
    msg = msg + ' ' + message['subject']
    #print parts[1].get_payload()
    return msg

## Format the txt from an email to be used in the comparison
def formatEmail(txt):
    commonWordList = set('''for a of the and to in it 
                        his her him has you me hers 
                        their there < > --'''.split())
    punctuationList = set('? ! . , & %'.split())
    doc = []
    for word in txt.lower().split():
        if word[-1] in punctuationList:
            if word[:-1] not in commonWordList:
                doc.append(word[:-1])
        elif word not in commonWordList:
            doc.append(word)
    return doc

## Setup archive by pulling in emails and adding questions
## and results to archive
def setupArchive(emails):
    arch = []
    for item in emails:
        msg = readEmail(item)
        msg = formatEmail(msg)
        print msg
        arch.append(msg)
    return arch

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

## Split .mbox into individual files
## Careful as this does make a lot of files...
def splitEmails(filename):
    fin = open(filename, 'r')
    data = fin.readlines()
    count = 0
    f = False
    for line in data:
        if f == False:
            name = 'email'+str(count)+'.txt'
            fout = open(name, 'w')
            f = True
        fout.write(line)
        if (line[:5] == "From "):
            count = count+1
            fout.close()
            f = False
    fin.close()
    return "Created " + str(count) + " files from emails."


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


################ Intelligence ################

## Takes in archive of old email questions and the new message
## then compares them. The old email questions are returned with
## a percentage of how close theypatch the new message
def checkSimilarity(texts, doc):
    # Part of this method was taken and then modified from the tutorial
    # on the gensim python page http://radimrehurek.com/gensim/tutorial.html
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)

    vec_bow = dictionary.doc2bow(doc)
    vec_lsi = lsi[vec_bow]

    index = similarities.MatrixSimilarity(lsi[corpus])
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    return sims

################ Main ################

## Main function that runs
def main():
    loadKeywords()
    archive = setupArchive(["testEmail1.txt", "testEmail2.txt", "testEmail3.txt", "testEmail4.txt"])
    msg2 = ['nwea', 'testing', 'not', 'password']
    result = checkSimilarity(archive,msg2)
    print result
    best = result[0][0]
    print best
    #print keywordList
    #print ("Keywords Matched: %s" % checkKeywords(msg))
    #print (addKeyword("password"))

################ Run Program ################

main()
