import os

##############          Edit the top directory    ########################
# Edit the top directory based on your respository

#TOP_DIRECTORY = "/Users/student/Downloads/RA_Patent/"
TOP_DIRECTORY = "/home/sunil/Documents/RA_Patent"

DATA_DIRECTORY = os.path.join(TOP_DIRECTORY, "data/")
##########################################################################

# Trie cache
TRIE_CACHE_DIRECTORY = os.path.join(DATA_DIRECTORY, "cache/")
if not os.path.exists(TRIE_CACHE_DIRECTORY):
    os.makedirs(TRIE_CACHE_DIRECTORY)

# Logging
LOGGING_DIRECTORY = os.path.join(DATA_DIRECTORY, "logging/")
if not os.path.exists(LOGGING_DIRECTORY):
    os.makedirs(LOGGING_DIRECTORY)

# Venture constants
#VENTURE_EXPERT_DATA_DUMP_PATH = "/home/sunil/Documents/RA_Patent/Trail/VentureExpertData.csv"
VENTURE_EXPERT_DATA_DUMP_PATH = os.path.join(DATA_DIRECTORY, "VentureExpertData.csv")

VENTURE_EXPERT_PKL_PATH = os.path.join(LOGGING_DIRECTORY, "venture_pkl.pkl")
VENTURE_EXPERT_PROCESSED_IDS = os.path.join(LOGGING_DIRECTORY, "venture_proceed_ids.txt")
DEFAULT_END_DATE = "12/31/2020"


# Patent constants
#PATENT_DATA_FILE = "/home/sunil/Documents/RA_Patent/Trail/PatentData4_trail.txt"
PATENT_DATA_FILE = os.path.join(DATA_DIRECTORY, "PatentData4_Sunil_V1.txt")

PATENT_PKL_PATH = os.path.join(LOGGING_DIRECTORY, "patent_pkl.pkl")

REQUIRED_PATENT_HEADERS = ['pnum', 'firstassignee', 'ayear', 'patassg_group_bfh_2017']
FILTER_ASSIGNED_GROUP_BFH_2017_DATA = ['05 Govt', '06 Universities', '07 Individuals']


# Output file path
EQUIVALENCE_OUTPUT_PATH = os.path.join(LOGGING_DIRECTORY, "equivalence_output.txt")
PROCESSED_EQUIVALENCE_OUTPUT_PATH = os.path.join(LOGGING_DIRECTORY, "processed_equivalence_output.txt")


# Frequency Path
PATENT_FREQUENCY_OUTPUT_PATH = os.path.join(LOGGING_DIRECTORY, "patent_frequency_output.txt")
VENTUREX_FREQUENCY_OUTPUT_PATH = os.path.join(LOGGING_DIRECTORY, "ventureX_frequency_output.txt")

# Normalized Company name path
PATENT_NORMALIZED_DUMP_PATH = os.path.join(LOGGING_DIRECTORY, "PatentData4_Sunil_V1_Normalized_Company.txt")
VENTUREX_NORMALIZED_DUMP_PATH = os.path.join(LOGGING_DIRECTORY, "VentureExpertData_Normalized_Company.txt")


# Configuration file path
CONFIGURATION_PATH = os.path.join(DATA_DIRECTORY, "configuration.txt")

# Noise words file path
NOISE_WORDS_FILE_PATH = os.path.join(DATA_DIRECTORY, "noise_words_dict.txt")