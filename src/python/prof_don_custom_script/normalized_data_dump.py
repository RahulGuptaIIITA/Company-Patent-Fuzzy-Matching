from parse_patent import (parse_patent_data,
                          save_parsed_patend_data,
                          load_patend_pkl)
from parse_venture_expert import (parse_venture_data,
                                  save_parsed_venture_data,
                                  load_venture_pkl)
from company_info_trie import possible_company_search

import pandas as pd
import numpy as np
from trie.daTrie import DaTrie
from trie.trie_utility import TrieUtility
from constants import (TRIE_CACHE_DIRECTORY,
                       PATENT_PKL_PATH)

from parse_patent import (parse_patent_data,
                          load_patend_pkl)
 
from company_info_trie import (possible_company_search,
                               normalize_words)

from trie.ranking_search_result import FrequencySearchRanking
from trie.ranking_search_result import EquivalenceSimilaritySearchRanking
from trie.ranking_search_result import CombineFrequencyAndEquivalencRanking

import os
import json

import sys
import codecs
from operator import itemgetter
import re
from constants import (VENTURE_EXPERT_PKL_PATH,
                       PATENT_PKL_PATH,
                       PATENT_NORMALIZED_DUMP_PATH,
                       VENTUREX_NORMALIZED_DUMP_PATH)

import os
import operator


def get_patent_normalized_dump():
    patent_df = load_patend_pkl(PATENT_PKL_PATH)
    patent_df['pat_nomralized_company'] = patent_df['company_name'].apply(normalize_words)
    return patent_df

def get_venture_normalized_dump():
    venture_df = load_patend_pkl(VENTURE_EXPERT_PKL_PATH)
    venture_df['pat_nomralized_company'] = venture_df['company_name'].apply(normalize_words)
    return venture_df

def write_to_file(file_path, df):
    df.to_csv(file_path, sep="|", index =False)


patent_dump = get_patent_normalized_dump()
write_to_file(PATENT_NORMALIZED_DUMP_PATH, patent_dump)

venturex_dump = get_venture_normalized_dump()
write_to_file(VENTUREX_NORMALIZED_DUMP_PATH, venturex_dump)