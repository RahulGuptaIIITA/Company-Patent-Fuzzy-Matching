# Trie Service Package
from trie.daTrie import DaTrie
from trie.trie_utility import TrieUtility
from constants import (TRIE_CACHE_DIRECTORY,
                       PATENT_PKL_PATH,
                       NOISE_WORDS_FILE_PATH,
                       CONFIGURATION_PATH)

from parse_patent import (parse_patent_data,
                          load_patend_pkl)
 
from trie.ranking_search_result import EquivalenceSimilaritySearchRanking

import os
import json

import sys
import codecs
from operator import itemgetter
import re

def read_configuration_file():
    """
    Reading the configuration file
    """
    with open(CONFIGURATION_PATH) as fp:
        config = json.loads(fp.read())
    return config

config = read_configuration_file()

NOISE_WORDS = config['noise_word_grammar']
FREQUENCY_THRESHOLD = config['trie_word_frequency_threshold']
IS_HARD_PREFIX = config['is_hard_prefix']
PREFIX_LENGTH = config['prefix_length']

def get_noise_words():
    """
    Reading the noise words
    """
    with open(NOISE_WORDS_FILE_PATH) as fp:
        data = json.loads(fp.read())
    return data[NOISE_WORDS]

def memoize(f):
    """ 
    Memoization decorator for functions taking one or more arguments.
    """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)


def normalize_words(sentence):
    """
    1. Replace -/_ the given company names with the space
    2. Remove all the special characters from the company names.
    3. Return only the string containing the alphabhets and digits.
    
    Takes company name as the parameter and returns normalized company name
    """
    sentence = sentence.upper()
    sentence = re.sub('[-_]', ' ', sentence)
    words = sentence.split()
    normalized = list()
    for word in words:
        word = re.sub('[^A-Za-z0-9]+', '', word).strip()
        if not word or word in NOISE_WORDS:
            continue
        normalized.append(word)
    return " ".join(normalized)

def normalize_dictionary_data(dict_data):
    """
    Takes the dict_data containing the patent_id and company_name. 
    Returns the dictionay of patent_id and normalized company name.
    """
    new_dict = dict()
    for key, value in dict_data.items():
        normalized_word = normalize_words(value)
        if not normalized_word:
            continue
        new_dict[key] = normalized_word
    return new_dict

@memoize
def get_company_information():
    """
    1. Loads the patent dump pickel file with required columns
    2. Converts the data into a dictionary of patent_id and company name
    3. Normalizes the company names
    4. Returns the dictionary of patent_id and normalized company name
    """
    patent_df = load_patend_pkl(PATENT_PKL_PATH)
    patent_df = patent_df[['pnum', 'company_name']]
    patent_dict = patent_df.set_index('pnum').to_dict()['company_name']
    patent_dict = normalize_dictionary_data(patent_dict)
    return patent_dict

@DaTrie.cache_datrie_to_file(TRIE_CACHE_DIRECTORY)
def get_company_detail_address_trie():
    """
    Service which gets a data with the single key column
    whose key will be the leaf node of the trie & the rest of the data is used to create a trie
    along with the key column

    The datrie cannot be serialized with cPickel and hence it requires customized serialization
    The trie to serialization will do the following
        - If the trie is not available in cache, tries to serialize the trie and write it to 
        the appropriate path. The file name will be the function name
        - If the trie is available in the cache, then deserialize the trie from the appropriate 
        path where it was earlier serialized
    """
    print ('Reading the company information text file')
    company_info_dict = get_company_information()
    trie_util = TrieUtility()
    datrie_obj = DaTrie()
    trie = trie_util.create_trie_from_dict(datrie_obj, company_info_dict)

    print ('Owned Deal Trie: Completed, Trie is ready to use')
    return trie


@memoize
def get_company_detail_trie():
    """
    Function to memorize the trie creation/fetch that was earlier executed
    """
    return get_company_detail_address_trie()


def get_company_details_top_search_results(leaf_node_key_list):
    """
    Service which returns a datab data for only the search result keys for futher ranking of the algorithm.
    Here Key will be the leaf node of the trie.
    """
    company_info_dict = get_company_information()
    required_company_info = dict()
    for val in leaf_node_key_list:
        required_company_info[val] = company_info_dict[val]
    return required_company_info


def get_company_search_ids(search_words):
    """
    For the given list of search_words, looks in the trie and finds all the 
    patent_ids (leafs) that can be reached from given prefix words.

    1. Load trie from cached data
    2. Search in trie, get matching keys list (for each word, list of keys)
    3. Return all the search ids for the given words.
    """
    # Fetch the trie object from memorized data
    trie = get_company_detail_trie()

    # Call the factory class & set the trie object to the respective trie class ie, datrie
    trie_obj = DaTrie()
    trie_obj.trie = trie

    # Search for the word in the trie using the trie utility
    trie_util = TrieUtility()

    search_ids = list()
    for word in search_words:
        result = trie_util.search_from_trie(trie_obj, word)
        search_ids.extend(result[0])
    return search_ids

def get_search_ids(company_name, first_n_prefix):
    """
    For the given company name from the venture expert data, get all the 
    search_ids from the trie that matches this word.

    1. If the length of the word is less than the prefix, then ignore
    2. Else find all the search_ids (patent_ids) from the trie that matches the patent company names.
    3. Find it for all the words in company_name
    4. If the search_ids for a word is greater than threshold, then its put to probable_noise
        and processed only when the other words didn't fetch any value.
    """
    search_ids = list()
    probable_noise = list()        
    for company_word in company_name.split():
        if len(company_word) < first_n_prefix:
            continue
        result = assume_first_n_characters_valid(company_word, n_constant=first_n_prefix)
        if len(result) > FREQUENCY_THRESHOLD:
            probable_noise.append(company_word)
            continue
        search_ids.extend(result)
    return search_ids, probable_noise

def assume_first_n_characters_valid(company_word, n_constant):
    """
    Considering only the first_n words for search in trie.
    """
    unique_set = [company_word[:n_constant]]
    return get_company_search_ids(unique_set)

def get_search_ids_probable_noise(company_name, first_n_prefix):
    """
    If we come across the words in probable noise (Those words with higher frequency).
    This function is called only when other words don't give any result.
    """
    search_ids = list()
    for company_word in company_name.split():
        if len(company_word) < first_n_prefix:
            continue
        result = assume_first_n_characters_valid(company_word, n_constant=first_n_prefix)
        search_ids.extend(result)
    return search_ids

def get_company_to_patent_mapping(search_ids, seen_search_ids, company_name, first_n_prefix):
    """
    1. For the search_ids looked up from the trie word and for the iteration of certain prefix length,
    the equivalence search is performed.
    
    2. If the similarity match between those search_ids and the venture company names is 70%, 
    then all those matches are considered and further decreasing the prefix length is stopped and 
    the result is returned.
    
    3. If the given prefix_lenght doesn't give any result, then it remembers all those search_ids
    and doesnt do the equivalence search. The equivalence search is costly process.  
    
    Output: get matching keys with ranking

    For the searched trie results, the algorithm helps in providing the most appropriate results using
        - Equivalent & Similarity Search alogrithm
    Please look at each function for more details for each implemented algorithm
    """
    search_ids = list(set(search_ids) - set(seen_search_ids))
    (patent_company_dict, ranked_company_result) = perform_equivalence_search(search_ids, company_name)

    company_to_patent_mapping = list()
    for company_id, rank in ranked_company_result.items():
        if rank < 0.7:
            break
        company_to_patent_mapping.append([company_id, patent_company_dict[company_id], rank, first_n_prefix])
    return company_to_patent_mapping

def possible_company_search(company_name):
    """
    Main function called for patent parsing using fuzzy search.
    1. Normalizes the company words from the Venture Expert Data
    
    2. Have a soft prefix constraint that first PREFIX_LENGTH words are fixed. To lookup in the trie. 
    Trie does a prefix search if this is not fixed, then gives very large number of matched ids.
    
    3. The above is a soft prefix. Its not the hard prefix, since its doesn't tell that the matching
    word must always have the first 3 words in same as patent dataset.
    
    4. The PREFIX_LENGTH is used in the such a way that first the highest prefix like 7 is fixed and
        the equivalence and similarity search is appllied on the resultant search ids.
    
    5. If this doesn't give any result with probability match >70%, then this prefix_length is reduced
        by 2. This is done till prefix_length = 3 and then gives up.
    
    6. Have a logic to capture those high frequency words and use only when no result is provided.
        But for now, the threshold for this high frequency is very high.
        So nothing goes to this list.(50000)
    """
    sentence = list()
    search_ids = list()
    seen_search_ids = list()
    company_name = normalize_words(company_name)   

    first_n_prefix = PREFIX_LENGTH    
    while(first_n_prefix >= 3):
        search_ids, probable_noise = get_search_ids(company_name, first_n_prefix)
        company_to_patent_mapping = get_company_to_patent_mapping(search_ids, seen_search_ids,\
                                                                  company_name, first_n_prefix)
        if company_to_patent_mapping:
            return company_to_patent_mapping
        
        if probable_noise:
            new_company_name = ' '.join(company_name)
            search_ids = get_search_ids_probable_noise(company_name, first_n_prefix)
            company_to_patent_mapping = get_company_to_patent_mapping(search_ids, seen_search_ids,\
                                                                      company_name, first_n_prefix)
            if company_to_patent_mapping:
                return company_to_patent_mapping

        first_n_prefix -= 2
        seen_search_ids.extend(search_ids)

def perform_equivalence_search(search_ids, search_word):
    """
    1. For the given search_ids (related to patent data) and 
     search word from the venture expert data, runs the equivalence search algorithm.

    2. If in configuration file you have a hard prefix constraint. That is the first 
    few characters must always match in both data. Then it does equivalence search on only
    those data. This is very fast than doing soft prefix search.
    """
    top_frq_dict = get_company_details_top_search_results(search_ids)

    if IS_HARD_PREFIX:
        filtered_top_frq_dict = dict()
        for key, value in top_frq_dict.items():
            if value[:3] == search_word[:3]:
                filtered_top_frq_dict[key] = value
        top_frq_dict = filtered_top_frq_dict

    eql_obj = EquivalenceSimilaritySearchRanking(search_word)
    
    equivalence_search_result = eql_obj.equivalence_and_similarity_search_result(top_frq_dict)
    return (top_frq_dict, equivalence_search_result)

"""
This was doing more robust search. For this project its not required.
The trie looks for first few characters fixed. This approach removes
the first few characters and checks in the trie. But not required.
This is very costly and gives many False negative values.

def call_recursion_removing_letters(company_word):
    possible_words = rec_search_by_removal_letter(company_word, dict()) 
    unique_set = list(set(possible_words.keys()))
    return get_company_search_ids(unique_set)


def rec_search_by_removal_letter(search_word, possible_search_words):
    if len(search_word) <= 2 or search_word in possible_search_words:
        return possible_search_words
    else:
        if search_word:
            possible_search_words[search_word] = True
        rec_search_by_removal_letter(search_word[:-1], possible_search_words)
        #rec_search_by_removal_letter(search_word[1:], possible_search_words)
        return possible_search_words
"""
