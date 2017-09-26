# WikiSearch
A simple search engine built in python capable of building optimised positional index for the Wikipedia dump &amp; perform field queries
This repository consists of the mini project done as part of the course Information Retrieval and Extraction - Monsoon 2016. The course was instructed by [Dr. Vasudeva Varma](http://faculty.iiit.ac.in/~vv/Home.html). 

## INSTRUCTIONS
- Install Python 2.6 or above
- Install the pip dependencies using `pip install -r requirements.txt`

## Problem Statement
The mini project involves building a search engine on the Wikipedia Data Dump without using any external index. For this project we use the data dump ofof size ~64 GB. The search results return in real time. Multi word and multi field search on Wikipedia Corpus is implemented.

## Search Engine Specifications

### Parsing
SAX Parser is used to parse the XML Corpus without loading the entire corpus in memory. This helps parse the corpus with minimum memory. After parsing the following morphological operations are performed to obtain clean vocalulary.

* `Stemming`: Using an externalFor stemming, a python library PyStemmer is used.
* `Casefolding`: Casefolding is easily done.
* `Tokenisation`: Tokenisation is done using regular expressions.
* `Stop Word Removal`: Stop words are removed by referring a stop word list.
* `Stemming`: This converts all the words into its root words. Python library PyStemmer is used.
* `Lemmetization (optional)`: This removes all the morphological transformations from the word and provides its raw form. NLTK lemmetizer is used for this purpose.

The index, consisting of stemmed words and posting list is build for the corpus after performing the above operations. Similar operations are performed for all the other fields. We assign new docIds to each instance of the Wikipedia page which helps in reducing the size as the document_id while storing, thereby reducing the index size. Since the size of the corpus will not fit into the main memory thus several index files are generated. We generate the following files:

* `vocabularyList.txt` : This file contains the merged vocabulary obtained from Wikipedia dump. Its sorted by word and each lineis of the following format:  
	- `barack 21 25706` - Here 1st token denotes the name of the word, 2nd token denotes the file number that stores more information about the word, while the 3rd token denotes the document_frequency or count of the number of documents that have at least one occurance of the word.  
* `title.txt`: It stores the title of the Wikipedia document. Each line in the file is of the following format:  
	- `76 International Atomic Time` - Here, the 1st token denotes the `doc_id` of the Wikipedia page in the whole corpus. It will be later used by the seach tool to map the `doc_id` to `doc_name`.

* `titleoffset.txt`: This file denotes the offsets that would be used to obtain the title of a particular `doc_id` using Binary search on the offsets. Offsets essentially provides the seek values to be used while reading the file to directly read a particular line. Each of the line in the offset denotes the seek value that must be used to read that line directly in the `title.txt` file.



### The Global Index: Merging the partial indexes to obtain a sorted big index.
Next, these index files are merged using **K-Way Merge** along with creating field based index files.
For example, index0.txt, index1.txt, index2.txt are generated. These files may contain the same word. Hence, K Way Merge is applied and field based files are generated along with their respective offsets. These field based files are generated using multi-threading. This helps in doing multiple I/O simultaneously. Along with this the vocabulary file is also generated.

Along with these I have also stored the offsets of each of the field files. This reduces the search time to O(logm * logn) where m is the number of words in the vocabulary file and m is the number of words in the largest field file.

The src folder contains the following files:

###Main Functions:

* wikiIndexer.py
This function takes as input the corpus and creates the entire index in field separated manner. Along with the field files, it also creates the offsets for the same. It also creates a map for the title and the document id along with its offset. Apart from this it also creates the vocabulary List

In order to run this code run the following:
**python wikiIndexer.py ./sampleText ./outputFolderPath**

* search.py
This function takes as input the query and returns the top ten results from the Wikipedia corpus.

In order to run this code run the following:
**python search.py ./outputFolderPath**

###Helper Functions:

* textProcessing.py 
This helper function does all the preprocessing. It acts as helper for search.py, wikiIndexer.py

* fileHandler.py
This function does all the file preprocessing. It acts as helper for wikiIndexer.py
