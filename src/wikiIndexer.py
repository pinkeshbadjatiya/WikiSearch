# This module takes as input the xml file and returns the posting list for the same.
# The index file generated is used by search.py for querying

import xml.sax.handler                                                  #modules
from textProcessing import processText,processTitle
from fileHandling import writeIntoFile, mergeFiles
from collections import defaultdict
import sys
import timeit
import pdb
from config import *

index = defaultdict(list)
count = 0       # Counts the number of pages that are processed, i.e. whose index is created
countFile = 0   # Counts the number of index files that are written on disk but not yet merged with the global index
dict_Id={}
offset = 0

OUTPUT_FOLDER = ""

class WikiHandler(xml.sax.handler.ContentHandler):
  """
      SAX Parser
  """

  flag = 0

  def createIndex(self, title, text, infoBox, category, externalLink):    #add tokens generated to index
    """
        Creates a index of a single Wikipedia page provided:
            dict of {word: freq} of [title, text, infoBox, category, externalLink]
    """
    global index, dict_Id, countFile, offset, count, OUTPUT_FOLDER

    vocabularyList = list(set(title.keys() + text.keys() + infoBox.keys() + category.keys() + externalLink.keys()))
    t, b, i, c, e = float(len(title)), float(len(text)), float(len(infoBox)), float(len(category)), float(len(externalLink))

    for key in vocabularyList:
      string = str(count) + ' '
      for (contentType, contentLen) in [(title, t), (text, b), (infoBox, i), (category, c), (externalLink, e)]:
        try:
          if SCORE_TYPE == "freq":
            string += str(int(contentType[key])) + ' '
          elif SCORE_TYPE == "freq_ratio":
            string += str(round(contentType[key]/contentLen, 3)) + ' '
          else:
            print "ERROR: Unknown scoring type"
        except ZeroDivisionError:
          string += str(SCORE_TYPE_TYPE(0)) + ' '
      index[key].append(string)

    count += 1
    if count % WRITE_PAGES_TO_FILE == 0:
      print "Pages Processed: %d | Writing the partial index to disk ..." % (count)
      offset = writeIntoFile(OUTPUT_FOLDER, index, dict_Id, countFile, offset)
      index = defaultdict(list)
      dict_Id = {}
      countFile += 1

  def __init__(self):
    """
        Initialization
    """
    self.inTitle, self.inId, self.inText = 0, 0, 0

  def startElement(self, name, attributes):                           #Start Tag
    if name == "id" and WikiHandler.flag==0:                          #Start Tag: Id
      self.bufferId = ""
      self.inId = 1
      WikiHandler.flag=1
    elif name == "title":                                             #Start Tag: Title
      self.bufferTitle = ""
      self.inTitle = 1
    elif name =="text":                                               #Start Tag:Body Text
      self.bufferText = ""
      self.inText = 1

  def characters(self, data):                                         #Read Text
    global count, dict_Id
    if self.inId and WikiHandler.flag==1:                             #Read Text: Id
        self.bufferId += data
    elif self.inTitle:                                                #Read Text: Title
        self.bufferTitle += data
        dict_Id[count] = data.encode('utf-8')
    elif self.inText:                                                 #Read Text: Body Text
        self.bufferText += data

  def endElement(self, name):                                         #End Tag
    if name == "title":                                               #End Tag: Title
      WikiHandler.titleWords = processTitle(self.bufferTitle)           #Parse Title
      self.inTitle = 0
    elif name == "text":                                              #End Tag: Body Text
      WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords = processText(self.bufferText)
      WikiHandler.createIndex(self, WikiHandler.titleWords, WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords)
      self.inText = 0
    elif name == "id":                                                #End Tag: Id
      self.inId = 0
    elif name == "page":                                              #End Tag: Page
      WikiHandler.flag=0


def main():
    global offset, countFile, OUTPUT_FOLDER
    if len(sys.argv)!= 3:
        print "Usage :: python wikiIndexer.py sample.xml ./output"
        sys.exit(0)
    OUTPUT_FOLDER = sys.argv[2]

    # SAX Parser
    parser = xml.sax.make_parser()
    handler = WikiHandler()
    parser.setContentHandler(handler)
    parser.parse(sys.argv[1])
    with open(OUTPUT_FOLDER + '/numberOfFiles.txt','wb') as f:
      f.write(str(count))

    offset = writeIntoFile(OUTPUT_FOLDER, index, dict_Id, countFile, offset)
    # pdb.set_trace()
    countFile+=1
    #countFile = 3529
    mergeFiles(OUTPUT_FOLDER, countFile)

    titleOffset=[]
    with open(OUTPUT_FOLDER + '/title.txt','rb') as f:
      titleOffset.append('0')
      for line in f:
        titleOffset.append(str(int(titleOffset[-1]) + len(line)))
    titleOffset = titleOffset[:-1]

    with open(OUTPUT_FOLDER + '/titleoffset.txt','wb') as f:
      f.write('\n'.join(titleOffset))

if __name__ == "__main__":

    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    print stop - start
