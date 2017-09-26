WRITE_PAGES_TO_FILE = 5000

# LEMMATIZER_OR_STEMMER = 'lemmatization'
LEMMATIZER_OR_STEMMER = 'stemming'

# SCORE_TYPE = "freq_ratio"
# SCORE_TYPE_TYPE = float

SCORE_TYPE = "freq"
SCORE_TYPE_TYPE = int

COMPRESS_INDEX = False

TOP_N_RESULTS = 10


# Champion lists?
CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD = True
TOP_N_POSTINGS_FOR_EACH_WORD = 200000


# Variable field weights?
# FIELD_WEIGHTS = {
#     't': 0.3,
#     'b': 0.3,
#     'i': 0.2,
#     'c': 0.1,
#     'e': 0.1
# }
#FIELD_WEIGHTS = {
#    't': 20,
#    'b': 1,
#    'i': 5,
#    'c': 1,
#    'e': 1
#}
#FIELD_WEIGHTS = {
#    't': 5,
#    'b': 1,
#    'i': 10,
#    'c': 2,
#    'e': 1
#}
FIELD_WEIGHTS = {
    't': 1,
    'b': 1,
    'i': 1,
    'c': 1,
    'e': 1
}
