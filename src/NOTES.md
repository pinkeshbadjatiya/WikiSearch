
Index format for each Wikipedia Page:
""""""
{
  'w1': ["PageID1 TitleScore BodyScore InfoBoxScore CategoryScore ExternalLinksScore", "PageID2 TitleScore BodyScore InfoBoxScore CategoryScore ExternalLinksScore"],
  'w2': ["aaaa", "AAAA", .........]
  ..
  ..
  ..
}
"""""
Here the default score is :
  Score = (Freq of the word in that section of the page)/(Size of vocab in that section of that page)
  [In case of errors default score is "0.0"]

These indexes are then merged to form a larger index. The index format saved on HDD looks like this:

"""""
87388 3822 0.0 0.0003 0.0 0.0 0.0
woodd 2824 0.0 0.0002 0.0 0.0 0.0
woodi 2748 0.0 0.0006 0.0 0.0 0.0
khirwar 4908 0.0 0.0014 0.0 0.0 0.0
sowell 1160 0.0 0.0056 0.0 0.0 0.0  1749 0.0 0.0014 0.0 0.0 0.0  1910 0.0 0.0007 0.0 0.0 0.0
chudson 4446 0.0 0.0008 0.0 0.0 0.0
koncertsal 3088 0.0 0.0002 0.0 0.0 0.0
"""""

Each instance of the word in a document is seperated by '  ' (double spaces)
=========================================================

Search:


To make the index searchable we split the indexes into multiple files and name them 'FIELD_NO'+'FILE_NUMBER' examples include 'b0.txt', 'b23.txt' etc. We then calculate the offset for each of these indexes and save them in the corresponding offset files with names as 'o'+'INDEX_NAME' namely 'ob0.txt', 'ob23.txt' etc.

So, for a index file which looks like this,
"""
aachen 682 1.0
aag 1189 1.0
aagesen 1304 1.0
aal 381 1.0
""""

we create a offset file which looks like this
"""
0 1
16 1
30 1
48 1
"""

So essentially, if we want to fetch the list of postings from a particular index file, then we can perform a Binary Search on the array of offsets to get the mid offset. Seeking the file pointer to the mid offset will fetch us the starting of that particular word which we can use to complete our Binary Search. This assumes that we have the whole offset of the index in memory. It is feasible as we split the index into multiple partial indexes, so to query a word we perform the following steps:
1. Since we split the index into multiple smaller files, we store a list of words with the file number and document frequency in a file we call 'vocabularyList.txt' which looks like this

"""
a 0 3
aa 0 14
aaa 0 126
aaaa 0 2
aaaaaa 0 12
aaaaaaiaaj 0 1
aaaaamaaj 0 3

"""

So we have a offset file named 'offset.txt' for the vocabularyList.txt which allows us to find the file-number and document-frequency in log(n) time.

2. Once we have the file number, we load the offsets from the offset file of that particular file number. Since index for all the fields are separate, so we choose the fields as specified by the user. If nothing is specified, then we query all the fields. Ex our query word is 'abbottabad' which lies in file number 3 and we have to query the field title(t) then we load the offsets of the file named 'ot3.txt' which allows us to serach the index file named 't3.txt'.

3. Once we have the file postings with the corresponding scores for single word queries,





- Top N postings for each word, similar to champion lists
- compute IDF as idf=log(N/(num_docs+1))
- compute TF as tf=log(1+freq)
- ranking_score = SUM(tf * idf * fieldWeights)

Rank the results obtained using the following heuristic:
    1. Compute the TF as TF=log(1+freq)
    2. Compute IDF as TDF=log(total_docs / (num_docs+1))
    3. Fetch the field weights as words in title have more importance over the words in body
    4. Compute the ranking score for a word as:
            score_word = tf * idf * field_weight
    5. To compute the score of query, we do:
            ranking_score = sum(score_word)
