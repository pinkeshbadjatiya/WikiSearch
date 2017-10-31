# WikiSearch
A simple search engine built in python capable of building optimised positional index for the Wikipedia dump &amp; perform field queries
This repository consists of the mini project done as part of the course Information Retrieval and Extraction - Monsoon 2017. The course was instructed by [Dr. Vasudeva Varma](http://faculty.iiit.ac.in/~vv/Home.html). 

## Instructions
- Install Python 2.7. Does not support Python 3
 - Migration to Python 3 should be as easy as changing print statements.
- Install the pip dependencies using `pip install -r requirements.txt`
- Setup appropriate values in `config.py` mentioning the kind of values to store in the indexer. These values can have a major impact on the performance of indexing as well as the searching part.
- Increase the value of `open files limit` in Ubuntu if you are indexing on a large corpus as K-way merge sort requires opening a large number of files and by default, the max number of files that you can open at a time is 1024. **Instructions:** [https://easyengine.io/tutorials/linux/increase-open-files-limit/](https://easyengine.io/tutorials/linux/increase-open-files-limit/)

## Problem Statement
- The mini project involves building a search engine on the Wikipedia Data Dump without using any external index. For this project, we use the data dump of size ~64 GB. The search results return in real time. Multi-word and multi-field search on Wikipedia Corpus is implemented.
- You also need to rank the documents and display only the top 10 most relevant documents.
- Search should take <5 seconds and the index should be ~20% of the dump size.

## Search Engine Specifications
### 1. Parsing: Read through the raw dump & extract essential words/phrases for indexing & searching
SAX Parser is used to parse the XML Corpus without loading the entire corpus in memory. This helps parse the corpus with minimum memory. After parsing the following morphological operations are performed to obtain clean vocabulary.

* `Stemming`: python library PyStemmer is used.
* `Casefolding`: Casefolding is easily done.
* `Tokenisation`: Tokenisation is done using regular expressions.
* `Stop Word Removal`: Stop words are removed by referring a stop word list.
* `Stemming`: This converts all the words into its root words. Python library PyStemmer is used.
* `Lemmatization (optional)`: This removes all the morphological transformations from the word and provides its raw form. NLTK lemmatizer is used for this purpose.
* `Term filter`: This removes some of the common terms that are found in abundance in all the pages. These include terms like `redirect`, `URL`, `png`, `HTTP` etc.


### 2. Partial Indexes: Extracting & storing essential information in small partial indexes
The index, consisting of stemmed words and posting list is built for the corpus after performing the above operations. Similar operations are performed for all the other fields. We assign new docIds to each instance of the Wikipedia page which helps in reducing the size as the document_id while storing, thereby reducing the index size. Since the size of the corpus will not fit into the main memory thus several index files are generated. We generate the following files:

* `title.txt`: It stores the title of the Wikipedia document. Each line in the file is of the following format:  
  - `76 International Atomic Time` - Here, the 1st token denotes the `doc_id` of the Wikipedia page in the whole corpus. It will be later used by the search tool to map the `doc_id` to `doc_name`.

* `titleoffset.txt`: This file denotes the offsets that would be used to obtain the title of a particular `doc_id` using Binary search on the offsets. Offsets essentially provide the seek values to be used while reading the file to directly read a particular line. Each of the line in the offset denotes the seek value that must be used to read that line directly in the `title.txt` file.

* `numberOfFiles.txt`: This denotes the total number of documents that are parsed and indexed. This should be equal to the total number of lines in the file `titles.txt`.

* `index0.txt`, `index1.txt`, ... `index9.txt`: These files are partial indexes of size as denoted in the config file. Each of these lines contains information about the occurrence of a word in the corpus. The syntax of each line is as follows:
  - `bilstein 139 0 4 0 0 0  642 0 10 0 0 0  4388 0 1 0 0 0` - Here each occurrence of the word in a document is denoted by a tuple of 6 tokens (eg, `139 0 4 0 0 0`). Each of these tuples gives information about its occurrence in a Wikipedia document.
  - `139 0 4 0 0 0`: Each occurrence of the term in a document has the following syntax. It corresponds to `Doc_Id TitleScore BodyScore InfoBoxScore CategoryScore ExternalLinksScore`. Default it stores the frequency of the terms in the following field. The indexer can be configured using the `config.py` to store the scores instead of frequency to improve both the ranking performance as well as improve the search time.

Once we have generated the partial indexes, we can perform merging to obtain a global index that can allow us to search for a term efficiently.  


### 3. The Global Index: Merging the partial indexes to obtain a sorted big index.
Now each of these separate indexes might contain common terms (in fact a large number of terms are common), so we need to merge the terms a create a common index.  

Next, these index files are merged using **K-Way Merge Sort Algorithm** creating field-based global index files along with their offsets. After the size of the sorted terms reaches a threshold (as defined in `config.py`), the index is created and pushed to a file of the format `<fieldname><filenumber>.txt`. It also stores the offsets of this data in another file named `o<fieldname><filenumber>.txt` for performing the search of a term in the file in **log(n)**. 

Hence, K Way Merge is applied and field-based files are generated along with their respective offsets. These field-based files can be generated using multi-threaded or single-threaded I/O. Multiple I/O simultaneously might not improve the performance, it depends on the configuration of the indexer. Along with this, the vocabulary file is also generated.
We generate the following files in this step:

* `b1.txt`, `t45.txt`, `i3.txt`, `c82.txt`, `e0.txt`: These files denote the fields indexes corresponding to the fields **Body**, **Title**, **Info Box**, **Category** and **External Links** respectively, of the file numbers 1, 45, 3, 82, 0 respectively.  Each of the lines in these files is of the format:
  - `aadhar 1324575 12 619212 3 7185170 1` - Here the 1st token corresponds to the name of the word. The next token will correspond to the `doc_id` of the document in which this word occurred followed by the score of the document. Default score is **freq**. This can be modified to store other score_types by changing the `config.py` file.
  - The order of `doc_id`s in each line is sorted by the doc score (default score is freq, so sorted by frequency) corresponding to that word.
  - This property is useful as it allows us to obtain `Top N` documents for each term allowing us to perform various time-based heuristics or word importance based heuristics to improve performance.

* `ob1.txt`, `ot45.txt`, `oi3.txt`, `oc82.txt`, `oe0.txt`: These files correspond to the offsets of each of these files. These offsets allow us to search for a word in the index file with **log(n)** complexity. The syntax of each of lines is as follows:
  - `6344225 26` - 1st token denotes the offset that will be used to seek the file pointer to read that line directly, while the 2nd token denotes the `doc_freq` of that term or the total number of unique documents where this term occurs.
  - This information can be used while performing intersection/union/difference of posting lists which can improve the performance.

* `vocabularyList.txt`: This file contains the merged vocabulary obtained from Wikipedia dump. It is sorted by word and each line is of the following format:  
  - `barack 21 25706` - Here 1st token denotes the name of the word, 2nd token denotes the file number that stores more information about the word, essentially the global index, while the 3rd token denotes the document frequency or count of the number of documents that have at least one occurrence of the word.  

* `offset.txt`: Since the Wikipedia dump is pretty huge, we cannot even store the entire vocabulary in the main memory, so we create offset of this file as well so that we can perform a lookup of a word in the covabularyList in **log(VocabSize)** which is quite fast.


* **Note**: We merge the partial index files `index1.txt` ... to obtain global index files `b0.txt`, `i13.txt` etc. Once a full partial index is used, we delete it from HDD to free space. Hence, after the merge process, we obtain the files `numberofFiles.txt`, `titles.txt`, `titleoffset.txt` and `vocabularyListtxt` along with the global index files.


### 4. Search: Performing multi-word / multi-field queries
The built search supports the following type of queries:
 - **Multi-word queries**
   - Eg. `Barach Obama`: We can perform such queries by searching for posting lists of individual words and then taking the union of the results. Since we have 5 fields, we search for each word in all the fields and then merge the results.
   - `Rank?` - To rank these results, we compute the scores for each document for a multi-word query as **score = summation of (weighted summation of scores of a word in all fields) for each word in query**. This provides us an absolute score for each document. Regarding the weights, these weights denote the importance of each field for a word, thus altering its score based on application. For example, a word occurring in the title once would have much more importance than a word occurring 10 times in external links.

 - **Field queries**
   - Eg. `b:Barach b:Obama i:president`: We can perform such queries by searching for posting lists of individual words in those particular field index only. We perform the union of these results.
   - `Rank?` - To rank these results, we compute the scores for each document for a multi-word query as **score = summation of scores of individual words**. This provides us an absolute score for each document and thus allows us to rank.

- **Multi-word field queries**
   - Eg. `Barack Obama i:president c:politics`: To perform such queries we combine both the above methods to obtain common scores for each of the documents. For words with specific fields attached, we obtain scores as per the *Field queries* method, while for words which do not have explicit field requests, we obtain weighted scores using the method *Multi-word queries*.

These methods allow us to perform most of the complex queries, some examples are as follows:

| Query Syntax           |     Summary       |
| :------------------------------------ |:----------------------------------------------------------------------------------------------|
| `Barack Obama c:politics`  | Fetches pages that have `Barack Obama` in content along with `politics` in categories section.|
| `c:president`    | Find all pages that have the category as president.      |
| `President of USA i:president` | Find pages containing `President of USA` along with having the term `president` in the InfoBox. |
| `Life Of Pi c:movies`   | Find the pages containing the movie name `life of pi`.     |


### 5. Search Complexity? : Analyzing the runtime
- `Search Time`: The above optimizations by using sorted indexes & the offset trick allows us to perform the search in less than linear time using Binary Search over all the index files. To be accurate, the search time reduces to **O(log(m) * log(n))** where m is the number of words in the vocabulary file and n is the number of words in the largest field file.
- With sorted indexes, we can further reduce the search time for multi-keyboard queries by truncation the posting lists so that merging is efficient for even words with a huge number of occurrences, eg, for words like *play*.


## Source Code walkthrough!
The src folder contains the following files:

* `config.py`:  This file contains the various configuration that is used by the indexer as well as the searcher. The index is built as per the configuration mentioned here.

* `wikiIndexer.py`: This function takes as input the corpus and creates the entire index in field separated manner. Along with the field files, it also creates the offsets for the same. It also creates a map for the title and the document id along with its offset. Apart from this it also creates the Vocabulary List.  
 
 To execute, run the following command: **python wikiIndexer.py <wiki-XML-dump-path> <output-index-folder-path>**

* `search.py` - This function takes as input the query and returns the top ten results from the Wikipedia corpus.

 To execute, run the following command: **python search.py <output-index-folder-path>**


## Helper Functions:

* `textProcessing.py`: This helper function does all the preprocessing. It acts as helper for search.py, wikiIndexer.py
* `fileHandler.py`: This function does all the file preprocessing. It acts as helper for wikiIndexer.py
