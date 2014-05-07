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
archive = []

################ Message Class ################

## Class for each email message. Contains information
## pertaining to the message including the question and
## response, file location, keywords, etc.
class Message:
    messageCount = 0

    def __init__(self, fileLocation):
        Message.messageCount += 1
        self.fileLocation = fileLocation
        print "creating",str(Message.messageCount)
        self.plainText,self.sender,self.subject = readEmail(self.fileLocation)
        self.keywords = formatEmail(self.plainText)
        addToArchive(self.keywords)

    def getCount(self): 
        return Message.messageCount

    def getSender(self):
        return self.sender
    
    def getSubject(self):
        return self.subject

    def getFileLocation(self): 
        return self.FileLocation

    def getPlainText(self): 
        return self.plainText

    def getCount(self): 
        return self.messageCount

    def getKeywords(self): 
        return self.keywords

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
    if (isinstance(parts, basestring)):
        return parts,message['from'],message['subject']
    msg = parts[0].get_payload()
    while not(isinstance(msg, basestring)):
        msg = msg[0].get_payload()
    #print "-------------------------------------------------------"
    #print msg
    return msg,message['from'],message['subject']


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
def addToArchive(msgKeywords):
    global archive    
    archive.append(msgKeywords)

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
def splitEmails(filename, locToSave):
    fin = open(filename, 'r')
    data = fin.readlines()
    listEmails = []

    start = True
    for line in data:
        if start == True:
            name = locToSave+'email0.txt'
            listEmails.append(name)
            fout = open(name, 'w')
            count = 0
            start = False
        elif (line[:5] == "From "):
            count = count+1
            fout.close()
            name = locToSave+'email'+str(count)+'.txt'
            listEmails.append(name)
            fout = open(name, 'w')
        fout.write(line)

    fout.close()
    fin.close()
    print "Created " + str(count) + " files from emails."
    return listEmails


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
    global keywordList
    for i in range(len(keywordList)):
        if newKeyword == keywordList[i][0]:
            return False
    fout = open("keywords.txt",'w')
    for i in range(len(keywordList)):
	l = str(keywordList[i][0])+','+str(keywordList[i][1])+'\n'
        fout.write(l)
    fout.close()
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
def checkSimilarity(dictionary,corpus,lsi, doc):
    # Part of this method was taken and then modified from the tutorial
    # on the gensim python page http://radimrehurek.com/gensim/tutorial.html
    vec_bow = dictionary.doc2bow(doc)
    vec_lsi = lsi[vec_bow]

    index = similarities.MatrixSimilarity(lsi[corpus])
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    return sims

## Builds the dictionary corpus to be searched through when comparing messages
def buildDictionary(texts):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)
    return dictionary, corpus, lsi

    
## Get initial information from the user
def getInfo():
    print "This program will tell you which emails are similar to one another."
    mbox = 'i'
    while (mbox == 'i'):
        mbox = raw_input("Do you have a .mbox archive of your email to use? i=more info (y/n/i): ")
        if mbox == 'y':
            fileLoc = raw_input(("Please enter the location and name of your .mbox file (ex: /users/you/Downlods/myEmails.mbox): "))
            locToSave =  raw_input("Please enter the location that you would like to save these emails (ex: /users/you/Documents/myEmails/): ")
            cont = raw_input("Are you sure you want to use your .mbox? This will split the archive into individual email files. Careful as this does make a lot of files... (y/n): ")
            if cont == 'y':
                listEmails = splitEmails(fileLoc,locToSave)
                return listEmails
        elif mbox == 'i':
            print "You can export your email from most common email clients, including gmail, to an archived .mbox file. This program can read that to build your archive to search through!"
        
    numEmails = raw_input("Please input the number of emails you have: ")
    fileLoc = raw_input("Please enter the location of the emails you would like to add to the archive database: ")
    fileNames = raw_input("Please enter the name of the files (ex: if files are testEmail1.txt, testEmail2.txt, please enter testEmail.txt): ")   
    dot = fileNames.index('.')
    listEmails = []
    for i in range(int(numEmails)):
        print "checking " + str(i)
        name = fileNames[:dot] + str(i)
        listEmails.append(fileLoc+fileNames[:dot]+str(i)+fileNames[dot:])
    return listEmails

################ Main ################

## Main function that runs
def main():
    allMail = getInfo()
    #allMail = ["testEmail1.txt", "testEmail2.txt", "testEmail3.txt", "testEmail4.txt"]
    arrayMessages = []
    for mail in allMail:
        arrayMessages.append(Message(mail))

    #print archive
    #loadKeywords()
    
    #arch = addToArchive(allMail)
    newMessage = ['nwea', 'testing', 'not', 'password']
    dictionary, corpus, lsi = buildDictionary(archive)
    result = checkSimilarity(dictionary,corpus,lsi,newMessage)
    print arrayMessages[result[0][0]].getPlainText()
    #best = []
    #for i in range(len(result)):
    #    if result[i][1] > 0.990:
    #        best.append(archive[result[i][0]])
    #print "Best results are: " + str(best)
    #best = result[0][0]
    #print keywordList
    #print ("Keywords Matched: %s" % checkKeywords(msg))
    #print (addKeyword("password"))

################ Run Program ################

main()
