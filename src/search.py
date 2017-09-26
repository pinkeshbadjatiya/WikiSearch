#This file enables search on Wikipedia corpus. It takes as input the query and returns the top ten links.

from textProcessing import cleanup_string
from collections import defaultdict
import threading, sys, bz2, re, math, pdb

from config import *
import time

offset = []

def ranking(results, documentFreq, numberOfFiles):
    """
        Rank the results obtained using the following heuristic:
            1. Compute the TF as TF=log(1+freq)
            2. Compute IDF as TDF=log(total_docs / (num_docs+1))
            3. Fetch the field weights as words in title have more importance over the words in body
            4. Compute the ranking score for a word as:
                    score_word = tf * idf * field_weight
            5. To compute the score of query, we do:
                    ranking_score = sum(score_word)
    """
    listOfDocuments, idf_of_word = defaultdict(float), defaultdict(float)

    # Compute the IDF for each word
    for word in documentFreq:
        idf_of_word[word] = math.log((float(numberOfFiles)/(float(documentFreq[word]) + 1)))

    for word in results:
        fieldWisePostingList = results[word]
        for field in fieldWisePostingList:
            if len(field) > 0:

                # Get posting list of a particular (word, field)
                postingList = fieldWisePostingList[field]

                # Champion lists ?
                postingList = postingList[:TOP_N_POSTINGS_FOR_EACH_WORD*2] if CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD else postingList

                # Weight the scores based on field weights
                factor = FIELD_WEIGHTS[field]

                for i in range(0, len(postingList), 2):
                    listOfDocuments[postingList[i]] += math.log(1+float(postingList[i+1])) * idf_of_word[word] * factor

    return listOfDocuments



def findFileNumber(low, high, offset, pathOfFolder, word, f):
    """
        Binary Search on the array of 'offset'.
    """
    #print low, high, f.name
    while low <= high:
        mid = (low+high)/2
        f.seek(offset[mid])
        testWord = f.readline().strip().split(' ')

    	#print low, mid, high, testWord[0], word

        if word == testWord[0]:
            #print "\tFound!", testWord[0]
            return testWord[1:], mid
        elif word > testWord[0]:
            low = mid+1
        else:
            high = mid-1
    return [], -1


def findFileNumber_forTitleSearch(low,high,offset,pathOfFolder,word,f):
    """
        Binary search for findind the title. Since the titles have integer documents-ids so we
        need to typecast to integer and then compare.
    """
    word = int(word)
    while low <= high:
        mid = (low+high)/2
        f.seek(offset[mid])
        testWord = f.readline().strip().split(' ')

        if word == int(testWord[0]):
            # print "\tFound!", testWord
            return testWord[1:], mid
        elif word > int(testWord[0]):
            low = mid+1
        else:
            high = mid-1
    return [], -1


def findFileList(fileName, fileNumber, field, pathOfFolder, word, fieldFile):
    """
        Find posting list.
            1. This first loads the offsets from the corresponding offset file.
            2. Then run a BinarySearch on the list of offsets to find the matching postings
    """
    fieldOffset, tempdf = [], []
    #print "Finding filelist for", fieldFile.name, word
    offsetFileName = pathOfFolder + '/o' + field + fileNumber + '.txt'
    with open(offsetFileName,'rb') as fieldOffsetFile:
        for line in fieldOffsetFile:
            offset, docfreq = line.strip().split(' ')
            fieldOffset.append(int(offset))
            tempdf.append(int(docfreq))
    fileList, mid = findFileNumber(0, len(fieldOffset), fieldOffset, pathOfFolder, word, fieldFile)
    return fileList, tempdf[mid]


def queryMultifield(queryWords, listOfFields, pathOfFolder, fVocabulary):
    """
        Multifield query:
    """
    fileList = defaultdict(dict)
    df = {}
    for i in range(len(queryWords)):
        word, key = queryWords[i], listOfFields[i]
        returnedList, mid= findFileNumber(0, len(offset), offset, sys.argv[1], word, fVocabulary)
        if len(returnedList) > 0:
            fileNumber = returnedList[0]
            fileName = pathOfFolder+'/'+key+str(fileNumber)+('.bz2' if COMPRESS_INDEX else ".txt")
            fieldFile = bz2.BZ2File(fileName,'rb') if COMPRESS_INDEX else open(fileName)
            returnedList, docfreq = findFileList(fileName,fileNumber,key,pathOfFolder,word,fieldFile)
            fileList[word][key], df[word] = returnedList, docfreq
    return fileList, df


#def querySimple(queryWords, pathOfFolder, fVocabulary):
#    """
#        Perform a simple query of a list of words in all the fields.
#    """
#    fileList = defaultdict(dict)
#    df = {}
#    listOfField = ['t', 'b', 'i', 'c', 'e']
#    for word in queryWords:
#        returnedList, _= findFileNumber(0, len(offset), offset, sys.argv[1], word, fVocabulary)
#        if len(returnedList) > 0:
#            fileNumber, df[word] = returnedList[0], returnedList[1]
#            for key in listOfField:
#                fileName = pathOfFolder+'/'+key+str(fileNumber[0])+('.bz2' if COMPRESS_INDEX else ".txt")
#                fieldFile = bz2.BZ2File(fileName,'rb') if COMPRESS_INDEX else open(fileName)
#                returnedList, _ = findFileList(fileName,fileNumber[0],key,pathOfFolder,word,fieldFile)
#                fileList[word][key] = returnedList
#    return fileList, df



def main():
    if len(sys.argv)!= 2:
        print "Usage :: python wikiIndexer.py pathOfFolder"
        sys.exit(0)

    # Read the offsets
    with open(sys.argv[1] + '/offset.txt', 'rb') as f:
        for line in f:
            offset.append(int(line.strip()))

    # Read the title offsets
    titleOffset = []
    with open(sys.argv[1]+'/titleoffset.txt','rb') as f:
        for line in f:
            titleOffset.append(int(line.strip()))

    while True:
        query = raw_input("Enter query:")
	if len(query.strip()) < 1:
	    sys.exit(0)
        fVocabulary = open(sys.argv[1] + '/vocabularyList.txt', 'r')
	start_time = time.time()

        queryWords = query.strip().split(' ')
        listOfFields, temp = [], []
        for word in queryWords:
            if re.search(r'[t|b|c|e|i]{1,}:', word):
                _fields = list(word.split(':')[0])
		_words = [word.split(':')[1]] * len(_fields)
            else:
		_fields = ['t', 'b', 'c', 'e', 'i']
		_words = [word] * len(_fields)

            listOfFields.extend(_fields)
            temp.extend(cleanup_string(" ".join(_words)))

	print "Fields:", listOfFields
	print "Words:", temp
        print "="*40
        results, documentFrequency = queryMultifield(temp, listOfFields, sys.argv[1], fVocabulary)

        with open(sys.argv[1]+'/numberOfFiles.txt','r') as f:
            numberOfFiles = int(f.read().strip())

        results = ranking(results, documentFrequency, numberOfFiles)
	end_time = time.time()
        if len(results)>0:
            top_n_docs = sorted(results, key=results.get, reverse=True)[:TOP_N_RESULTS]
            #pdb.set_trace()

	    # Get titles for Top N results only
            titleFile = open(sys.argv[1] + '/title.txt','rb')
            dict_Title = {}
            for docid in top_n_docs:                                                                  #find top ten links
                title, _ = findFileNumber_forTitleSearch(0, len(titleOffset), titleOffset, sys.argv[1], docid, titleFile)
                if not len(title):
                    print "Title Not Found:", docid, titleFile, len(titleOffset)
                dict_Title[docid] = ' '.join(title)

            # print results
            for rank, docid in enumerate(top_n_docs):
                print "\t",rank+1, ":", dict_Title[docid], "(Score:", results[docid], ")"
            print "="*40
	    print "QueryTime:", end_time - start_time, "seconds"
        else:
            print "Phrase Not Found"


if __name__ == "__main__":
    main()
