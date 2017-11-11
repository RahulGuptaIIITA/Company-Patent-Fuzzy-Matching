import re


class TrieUtility(object):
    """
    TrieUtility function for searching the trie and creating trie.
    """
    @classmethod
    def create_trie_from_dict(self, trie_class_obj, dict_input, min_word_len=0, pattern_break=r"[\s,']"):
        """
        Utility function for creating the trie from the dictionary.
        1. Converts all the words into uppercase
        2. Breaks the words on provided pattern. Default pattern is space or '
        3. Minimum length of the word to go into trie is also considered.

        Returns a trie object
        """
        for key, value in dict_input.items():
            leaf = str(key).upper()
            trie_words = re.split(pattern_break, value)
            for word in trie_words:
                if not len(word) >= min_word_len:
                    continue
                word = str(word.upper())
                trie_class_obj.put_to_trie(word, leaf)
        return trie_class_obj.trie

    @classmethod
    def search_from_trie(self, trie_class_obj, search_words, min_word_len=0, pattern_break=r"[\s,']"):
        """   
        Get all the search results from the trie for the given search_word. 
        
        Each word is split on space & for each word the value set is taken
        trie_result = [set('Search result of ABC'), set('Search result of XYZ')], 
        if search_word is 'ABC XYZ'
        """
        search_results = list()
        splt_words = re.split(pattern_break, search_words)
        for word in splt_words:
            if not len(word) >= min_word_len:
                continue
            result = trie_class_obj.fetch_from_trie(word)
            if result:
                res = list()
                for r in result:
                    res.extend(r)
                search_results.append(res)
            else:
                search_results.append(result)
        return search_results