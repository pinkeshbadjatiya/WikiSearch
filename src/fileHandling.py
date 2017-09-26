#This function does all the file Handling required for creating the index.

import sys
import bz2
import heapq
import os
import operator
from collections import defaultdict
# import threading
import pdb
from config import *

#
# class writeParallel(threading.Thread):
#     """
#         Multi Threading , write multiple field files simultaneously
#     """
#     def __init__(self, field, data, offset, countFinalFile,pathOfFolder):
#         threading.Thread.__init__(self)
#         self.data=data
#         self.field=field
#         self.count=countFinalFile
#         self.offset=offset
#         self.pathOfFolder=pathOfFolder
#
#     def run(self):
#         filename= self.pathOfFolder+'/'+self.field+str(self.count)
#         with bz2.BZ2File(filename+'.bz2', 'wb', compresslevel=7) as f:
#             f.write('\n'.join(self.data))
#         with open(filename+'.txt', 'wb') as f:
#             f.write('\n'.join(self.data))
#         filename= self.pathOfFolder+'/o'+self.field+str(self.count)+'.txt'
#         with open(filename, 'wb') as f:
#             f.write('\n'.join(self.offset))


def writeSingle(field, data, offset, countFinalFile, pathOfFolder):
    filename = pathOfFolder + '/' + field + str(countFinalFile)
    if COMPRESS_INDEX:
      write_type = bz2.BZ2File(filename+'.bz2', 'wb', compresslevel=7)
    else:
      write_type = open(filename+'.txt', 'wb')

    with write_type as f:
        f.write('\n'.join(data) + "\n")
    filename = pathOfFolder + '/o' + field + str(countFinalFile) + '.txt'
    with open(filename, 'wb') as f:
        f.write('\n'.join(offset) + "\n")



def get_appropriate_score_type(score):
    if SCORE_TYPE_TYPE == int:
	return SCORE_TYPE_TYPE(float(score))
    if SCORE_TYPE_TYPE == float:
        return SCORE_TYPE_TYPE(score)

def writeFinalIndex(data, countFinalFile, pathOfFolder,offsetSize):
    """
        Write index after merging
    """
    title, text, info, category, externalLink = defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict)
    print "Merging file:", countFinalFile
    uniqueWords, offset = [], []

    min_score_value = str(SCORE_TYPE_TYPE(0))

    for key in sorted(data):
        listOfDoc = data[key]
        temp=[]
        flag=0
        for i in range(0, len(listOfDoc), 6):
           word = listOfDoc
           docid = word[i]
           try:
               if word[i+1] != min_score_value:
                   title[key][docid]=get_appropriate_score_type(word[i+1])
                   flag=1
               if word[i+2] != min_score_value:
                   text[key][docid]=get_appropriate_score_type(word[i+2])
                   flag=1
               if word[i+3] != min_score_value:
                   info[key][docid]=get_appropriate_score_type(word[i+3])
                   flag=1
               if word[i+4] != min_score_value:
                   category[key][docid]=get_appropriate_score_type(word[i+4])
                   flag=1
               if word[i+5] != min_score_value:
                   externalLink[key][docid]=get_appropriate_score_type(word[i+5])
                   flag=1
           except Exception as e:
	       print e
               pdb.set_trace()
        if flag==1:
            string = key+' '+str(countFinalFile)+' '+str(len(listOfDoc)/6)
            uniqueWords.append(string)
            offset.append(str(offsetSize))
            offsetSize=offsetSize+len(string)+1

    titleData, textData, infoData, categoryData, externalLinkData = [], [], [], [], []
    titleOffset, textOffset, infoOffset, categoryOffset, externalLinkOffset = [], [], [], [], []

    previousTitle, previousText, previousInfo, previousCategory, previousExternalLink = 0, 0, 0, 0, 0

    for key in sorted(data.keys()):                                                                     #create field wise Index

        if key in title:
            string=key+' '
            sortedField = title[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += doc + ' ' + str(title[key][doc]) + ' '
            titleOffset.append(str(previousTitle)+' '+str(len(sortedField)))
            previousTitle += len(string)+1
            # pdb.set_trace()
            titleData.append(string)

        if key in text:
            string=key+' '
            sortedField = text[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += doc + ' ' + str(text[key][doc]) + ' '
            textOffset.append(str(previousText)+' '+str(len(sortedField)))
            previousText += len(string)+1
            # pdb.set_trace()
            textData.append(string)

        if key in info:
            string=key+' '
            sortedField=info[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += doc + ' ' + str(info[key][doc]) + ' '
            infoOffset.append(str(previousInfo) + ' ' + str(len(sortedField)))
            previousInfo += len(string)+1
            infoData.append(string)

        if key in category:
            string=key+' '
            sortedField=category[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += (doc + ' ' + str(category[key][doc]) + ' ')
            categoryOffset.append(str(previousCategory)+' '+str(len(sortedField)))
            previousCategory += len(string)+1
            categoryData.append(string)

        if key in externalLink:
            string=key+' '
            sortedField=externalLink[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string+=doc+' '+str(externalLink[key][doc])+' '
            externalLinkOffset.append(str(previousExternalLink)+' '+str(len(sortedField)))
            previousExternalLink+=len(string)+1
            externalLinkData.append(string)

    writeSingle('t', titleData, titleOffset, countFinalFile,pathOfFolder)
    writeSingle('b', textData, textOffset, countFinalFile,pathOfFolder)
    writeSingle('i', infoData, infoOffset, countFinalFile,pathOfFolder)
    writeSingle('c', categoryData, categoryOffset, countFinalFile,pathOfFolder)
    writeSingle('e', externalLinkData, externalLinkOffset, countFinalFile,pathOfFolder)

    try:
	# Change file of size > 30.48 Mb
        if os.path.getsize(pathOfFolder+'/b'+str(countFinalFile)+('.txt.bz2' if COMPRESS_INDEX else '.txt')) > 30485760:
            countFinalFile+=1
    except:
        pass

    with open(pathOfFolder+"/vocabularyList.txt","ab") as f:
      f.write('\n'.join(uniqueWords) + "\n")

    with open(pathOfFolder+"/offset.txt","ab") as f:
      f.write('\n'.join(offset) + "\n")

    return countFinalFile, offsetSize



def writeIntoFile(pathOfFolder, index, dict_Id, countFile, titleOffset):
    """
        Write partial index to file
    """
    data=[]                                                                             #write the primary index
    previousTitleOffset = titleOffset

    # Iterating index over key essentially DOES NOT sort the index based on 'word'
    for key in sorted(index.keys()):
        string = key.encode('utf-8') + ' ' + ' '.join(index[key])
        data.append(string)

    # Compress if required and then write into file
    filename = pathOfFolder + '/index' + str(countFile) + ('.txt.bz2' if COMPRESS_INDEX else '.txt')
    write_type = bz2.BZ2File(filename, 'wb', compresslevel=9) if COMPRESS_INDEX else open(filename, 'wb')
    with write_type as f:
        f.write('\n'.join(data))


    data=[]
    dataOffset=[]
    for key in sorted(dict_Id.keys()):
        data.append(str(key) + ' ' + dict_Id[key])
        dataOffset.append(str(previousTitleOffset))
        previousTitleOffset += len(str(key) + ' ' + dict_Id[key])

    with open(pathOfFolder + '/title.txt','ab') as f:
        f.write('\n'.join(data) + '\n')

    '''filename=pathOfFolder+'/titleoffset.txt'
    with open(filename,'ab') as f:
        f.write('\n'.join(dataOffset))'''

    return  previousTitleOffset


def mergeFiles(pathOfFolder, countFile):
    """
        Merge multiple partial indexes using HEAP merge.
    """
    listOfWords, indexFile, topOfFile = {}, {}, {}
    flag = [0]*countFile
    data = defaultdict(list)
    heap = []
    countFinalFile, offsetSize = 0, 0
    for i in xrange(countFile):
        fileName = pathOfFolder + '/index' + str(i) + ('.txt.bz2' if COMPRESS_INDEX else '.txt')
        indexFile[i] = bz2.BZ2File(fileName, 'rb') if COMPRESS_INDEX else open(fileName, 'rb')
        flag[i] = 1
        topOfFile[i] = indexFile[i].readline().strip()
        listOfWords[i] = topOfFile[i].split()
        if listOfWords[i][0] not in heap:
            heapq.heappush(heap, listOfWords[i][0])

    count=0
    while any(flag)==1:
        temp = heapq.heappop(heap)
        count += 1
	#print "."
        for i in xrange(countFile):
            if flag[i]:
                if listOfWords[i][0] == temp:
                    data[temp].extend(listOfWords[i][1:])
                    topOfFile[i] = indexFile[i].readline().strip()
                    if topOfFile[i] == '':
                            flag[i] = 0
                            indexFile[i].close()
			    print "\tRemoved:", str(i)
                            os.remove(pathOfFolder + '/index' + str(i) + ('.txt.bz2' if COMPRESS_INDEX else '.txt'))
                    else:
                        listOfWords[i] = topOfFile[i].split()
                        if listOfWords[i][0] not in heap:
                            heapq.heappush(heap, listOfWords[i][0])

	if not count%5000:
	    print "Done Words:", count
        if count > 0 and count%20000==0:
            oldCountFile = countFinalFile
            countFinalFile, offsetSize = writeFinalIndex(data, countFinalFile, pathOfFolder, offsetSize)
            if oldCountFile !=  countFinalFile:
                data = defaultdict(list)
    countFinalFile, offsetSize = writeFinalIndex(data, countFinalFile, pathOfFolder, offsetSize)
