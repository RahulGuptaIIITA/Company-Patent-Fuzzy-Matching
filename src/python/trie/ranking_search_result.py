from operator import itemgetter
from collections import OrderedDict

class EquivalenceSimilaritySearchRanking(object):

    def __init__(self, search_words, TOP_MATCH_RESULTS=100):
        self.search_words = search_words
        self.TOP_MATCH_RESULTS = TOP_MATCH_RESULTS

    def equivalence_and_similarity_search_result(self, key_search_dict):
        """
        Break down the given word into pairs.
        Example:
            - Search word - SUNIL M
            - Complete Text - ANIL

        Then the alogrithm splits these words
            - SUNIL M- {'SU', 'UN', 'NI', 'IL', 'L ',' M'}
            - ANIL G - {'AN', 'NI', 'IL', 'L ', 'G '}

        Compares both these and uses the following formula
        Ranking = 2 * Intersection / (Number of pairs in 'SUNIL M') + (Number of pairs in 'ANIL G')
        Ranking = 2 * 3/ (6+5)

        Refer the following link for
        http://www.catalysoft.com/articles/StrikeAMatch.html
        """

        original_pair_list = self._word_letter_pairs(self.search_words)
        similarity_rank_dict = dict()
        top_equi_similar_dict = OrderedDict()
        for (key, value) in key_search_dict.items():
            similarity_rank_dict[key] = \
                self._compareStrings(original_pair_list, value)
            
        for val in sorted(similarity_rank_dict.items(),
                          key=itemgetter(1),
                          reverse=True)[:self.TOP_MATCH_RESULTS]:
            top_equi_similar_dict[val[0]] = val[1]
        return top_equi_similar_dict

    def _letter_pairs(self, string_val):
        """
        Gives the list of pair of letter for a given string
        """

        pairs = list()
        for i in range(0, len(string_val)):
            pairs.append(string_val[i:i + 2])
        return pairs

    def _word_letter_pairs(self, string_val):
        """
        Letter pair for words
        """

        all_pairs = list()
        words = string_val.split("\s")
        for word in words:
            if word == '':
                continue
            pairs_in_word = self._letter_pairs(word)
            for element in pairs_in_word:
                all_pairs.append(element)
        return all_pairs

    def _compareStrings(self, original_pair_list, fetched_word):
        """
        comparing the search string with the original string & adding the ranking value to it.
        """

        fetched_pair_list = self._word_letter_pairs(fetched_word)
        intersection = 0
        union = len(original_pair_list) + len(fetched_pair_list)
        for i in range(0, len(original_pair_list)):
            pair1 = original_pair_list[i]
            for j in range(0, len(fetched_pair_list)):
                pair2 = fetched_pair_list[j]
                if pair1 == pair2:
                    intersection += 1
                    fetched_pair_list.remove(fetched_pair_list[j])
                    break
        return 2.0 * intersection / union
