#This function serves as a module to wikiIndexer.py
#It takes as input the text/title given and returns the list of words after
#completing the various parsing operations : casefolding, stop words removal
#tokenisation and stemming
import re
from collections import defaultdict

from Stemmer import Stemmer
# from stemming import porter2 as stemming_porter2
from nltk.stem import WordNetLemmatizer

from nltk.corpus import stopwords as nltk_stopwords
from sets import Set
import pdb
from config import *
import string


STOPWORDS = Set(nltk_stopwords.words('english'))
URL_STOP_WORDS = Set(["http", "https", "www", "ftp", "com", "net", "org", "archives", "pdf", "html", "png", "txt", "redirect"])
STEMMER = Stemmer('english')
LEMMATIZER = WordNetLemmatizer()
EXTENDED_PUNCTUATIONS = Set(list(string.punctuation) + ['\n', '\t', " "])
INT_DIGITS = Set(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

MAX_WORD_LEN = 10
MIN_WORD_LEN = 3

# -*- coding: utf-8 -*-
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def tokenize(data):
  """
    Tokenize the data(string)
  """
  tokenizedWords = re.findall("\d+|[\w]+",data)
  tokenizedWords = [key.encode('utf-8') for key in tokenizedWords]
  return tokenizedWords

def removeNumbersAndPunctuations(listOfWords):
  """
        This function essentially checks each character in the word, and then removes the numbers & punctuations from them.
  """
  temp = []
  for w in listOfWords:
    s = ""
    for c in w:
        # Remove Numbers
        if c in INT_DIGITS:
            continue

        # Remove Punctuation
        if c in EXTENDED_PUNCTUATIONS:
            if len(s) and isEnglish(s):
                temp.append(s)
            s = ""
            continue
        s += c
    if len(s) and isEnglish(s):
        temp.append(s)
  return temp


def removeStopWords(listOfWords):
  temp = []
  for w in listOfWords:
    # Standard StopWords Removal
    if w in STOPWORDS:
      continue

    # URL StopWords Removal
    if w in URL_STOP_WORDS:
      continue

    # Remove word which are not: MIN_WORD_LEN <= len(w) <= MAX_WORD_LEN
    if len(w) < MIN_WORD_LEN:
        continue
    if len(w) > MAX_WORD_LEN:
        continue

    temp.append(w)
  return temp


def stemmer(listofTokens):
  """
    Stemming the list of tokens
  """
  return [STEMMER.stemWord(key) for key in listofTokens]

def lemmatizer(listofTokens):
  """
    Lemmatize the list of tokens
  """
  return [LEMMATIZER.lemmatize(key) for key in listofTokens]


def create__word_to_freq_defaultdict(words):
  """
    Takes a list of words, and the counts the frequency and then returns a defaultdict with key as 'word'
    and value as 'frequency'
  """
  temp = defaultdict(int)
  for key in words:
    temp[key]+=1
  return temp


def cleanup_list(list_of_words, already_lowercase=False):
  """   Do the following cleanup steps on the provided string:
            1. Case Folding
            2. Tokenization
            3. Stop Words Removal
            4. Stemming
  """
  temp = []
  if not already_lowercase:                                         # Case folding only if required
      list_of_words = [s.lower() for s in list_of_words]

  # The received list is already tokenized.
  # SO you just need to remove crap words!

  # First remove punctuations & numbers followed by STOPWORDS. Remember, the order of these steps matter!
  temp = removeNumbersAndPunctuations(list_of_words)       # Number & Punctuation removal
  temp = removeStopWords(temp)                    # Stop Word Removal

  if LEMMATIZER_OR_STEMMER == 'stemming':
      temp = stemmer(temp)                        # Stemming
  elif LEMMATIZER_OR_STEMMER == 'lemmatization':
      temp = lemmatizer(temp)                            # Lemmatization
  else:
      print "ERROR: Unknown type"

  return temp


def cleanup_string(string, already_lowercase=False):
  """   Do the following cleanup steps on the provided string:
            1. Case Folding
            2. Tokenization
            3. Give it to cleanup_list()
  """
  if not already_lowercase:                                         # Case folding only if required
      string = string.lower()
  return cleanup_list(tokenize(string), already_lowercase=True)


def findExternalLinks(data):
  links=[]
  lines = data.split("==external links==")
  if len(lines) > 1:
    lines = lines[1].split("\n")
    for i in xrange(len(lines)):
      if '* [' in lines[i] or '*[' in lines[i]:
        list_of_words = lines[i].split(' ')
        links.extend(cleanup_list(list_of_words, already_lowercase=True))

  return create__word_to_freq_defaultdict(links)



def findInfoBoxTextCategory(data):
  """
    find InfoBox, Text and Category
  """
  info, bodyText, category, links = [], [], [], []
  flagtext = 1
  lines = data.split('\n')
  # pdb.set_trace()
  for i in xrange(len(lines)):
    if '{{infobox' in lines[i]:
      flag = 0
      temp = lines[i].split('{{infobox')[1:]
      info.extend(temp)
      while True:
            if '{{' in lines[i]:
                flag += lines[i].count('{{')
            if '}}' in lines[i]:
                flag -= lines[i].count('}}')
            if flag <= 0:
                break
            i += 1
            try:
                info.append(lines[i])
            except:
                break
    elif flagtext:
      if '[[category' in lines[i] or '==external links==' in lines[i]:
        flagtext = 0
      bodyText.extend(lines[i].split())

    else:
      if "[[category" in lines[i]:
        line = data.split("[[category:")
        if len(line)>1:
            category.extend(line[1:-1])
            temp = line[-1].split(']]')
            category.append(temp[0])
    #   pdb.set_trace()

  # Process category, info and bodyText
  category = cleanup_list(category, already_lowercase=True)
  info = cleanup_list(info, already_lowercase=True)
  bodyText = cleanup_list(bodyText, already_lowercase=True)

  # Count frequencies of all the words in the respective sections
  info = create__word_to_freq_defaultdict(info)
  bodyText = create__word_to_freq_defaultdict(bodyText)
  category = create__word_to_freq_defaultdict(category)

  return info, bodyText, category


def processTitle(data):
  """   Parse Title:
            1. cleanup_string() to get generalized data
            2. Count freq & return a dict as {'word': 'frequency'}
  """
  data = cleanup_string(data, already_lowercase=False)
  return create__word_to_freq_defaultdict(data)


def processText(data):                                              # Parse Text
  """   Parse Text:
            1. Case Folding
            2. Tokenization
  """
  data = data.lower()                                               # Case Folding
  externalLinks = findExternalLinks(data)
  data = data.replace('_', ' ').replace(',', '')
  infoBox, bodyText, category = findInfoBoxTextCategory(data)       #Tokenisation
  return bodyText, infoBox, category, externalLinks
