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
                       EQUIVALENCE_OUTPUT_PATH,
                       VENTURE_EXPERT_PROCESSED_IDS,
                       PATENT_FREQUENCY_OUTPUT_PATH,
                       VENTUREX_FREQUENCY_OUTPUT_PATH)

import os
import operator

def normalize_words(sentence):
    sentence = sentence.upper()
    words = sentence.split()
    normalized = list()
    for word in words:
        word = re.sub('[^A-Za-z0-9]+', '', word).strip()
        normalized.append(word)
    return normalized

def normalize_dictionary_data(dict_data):
    frequency_dict = dict()
    for key, value in dict_data.items():
        normalized_word = normalize_words(value)
        for words in normalized_word:
        	if words not in frequency_dict:
        		frequency_dict[words] = 0
        	frequency_dict[words] += 1
    sorted_frequency = sorted(frequency_dict.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_frequency

def get_patent_frequency():
    patent_df = load_patend_pkl(PATENT_PKL_PATH)
    patent_df = patent_df[['pnum', 'company_name']]
    patent_dict = patent_df.set_index('pnum').to_dict()['company_name']
    frequency_dict = normalize_dictionary_data(patent_dict)
    return frequency_dict

def get_venture_frequency():
    patent_df = load_patend_pkl(VENTURE_EXPERT_PKL_PATH)
    patent_df = patent_df[['vxfirm_id', 'company_name']]
    patent_dict = patent_df.set_index('vxfirm_id').to_dict()['company_name']
    frequency_dict = normalize_dictionary_data(patent_dict)
    return frequency_dict

def write_to_file(file_path, data):
    with open(file_path, "a") as fp:
        for value in data:
            fp.write(str(value[0]) + '|' + str(value[1]) + "\n")


patent_frequency = get_patent_frequency()
write_to_file(PATENT_FREQUENCY_OUTPUT_PATH, patent_frequency)

venturex_frequency = get_venture_frequency()
write_to_file(VENTUREX_FREQUENCY_OUTPUT_PATH, venturex_frequency)