"""
  This module has parent trie class which defines
  trie related methods signatures to work in 
  ABS trie based autocomplete framework.
"""

from collections import defaultdict

import re

################################################################################

class Trie(object):
    """
    This is parent trie class for any trie which wants to use
    ABS trie based autocomplete framework.

    This class defines some abstract methods which every child class
    needs to implement to leverage resuable autocomplete features.
    e.g. search algorithms.
    """
    def __init__(self,
                 keys_break_pattern=r"[\w']+",
                 case_sensitive_keys=False):
        self._keys_break_pattern = keys_break_pattern
        self._case_sensitive_keys = case_sensitive_keys

#################################################################

    @property
    def trie(self):
        raise NotImplementedError('Please create an trie attribute in wrapper class')

#################################################################

    @property
    def keys_break_pattern(self):
        return self._keys_break_pattern

#################################################################

    @keys_break_pattern.setter
    def keys_break_pattern(self, value):
        self._keys_break_pattern = value

#################################################################

    @property
    def case_sensitive_keys(self):
        return self._case_sensitive_keys

#################################################################

    @case_sensitive_keys.setter
    def case_sensitive_keys(self, value):
        self._case_sensitive_keys = value

#################################################################

    def _get_keys_break_pattern(self, keys_break_pattern=None):
        _keys_break_pattern = self.keys_break_pattern
        if keys_break_pattern:
            _keys_break_pattern = keys_break_pattern
        return _keys_break_pattern

#################################################################

    def _split_keys(self, keys_str, keys_break_pattern=None):
        keys =  re.findall(self._get_keys_break_pattern(keys_break_pattern),
                           str(keys_str))
        return [self.get_key_in_trie_format(key) for key in keys]

#################################################################

    def get_key_in_trie_format(self, key):
        if not self.case_sensitive_keys:
            key = str(key).upper()
        return key

#################################################################

    def put_keys_in_trie(self, keys_str, leaf_node, keys_break_pattern=None):
        """
        This method takes put various keys with same value in trie.
        It splits the keys with pattern given.
        """
        keys = self._split_keys(
            keys_str,
            self._get_keys_break_pattern(keys_break_pattern))

        for key in keys:
            self.put_in_trie(key, leaf_node)

#################################################################

    def put_in_trie(self, key, leaf_node):
        """
        Abstract method to put data in trie
        """
        raise NotImplementedError('Please Implement put_to_trie method')

#################################################################

    def put_to_trie(self, key, value):
        """
        Deprecate this one later on in favour of put_in_trie method.
        Abstract method to put data in trie
        """
        raise NotImplementedError('Please Implement put_to_trie method')

#################################################################

    def get_items_from_trie(self, keys_str, keys_break_pattern=None):
        search_keys = self._split_keys(
            keys_str,
            self._get_keys_break_pattern(keys_break_pattern))

        search_results_items = []
        for key in search_keys:
            search_results_items.extend(self.fetch_from_trie(key))

        return search_results_items

#################################################################

    def fetch_from_trie(self, search_word):
        """
        Abstract method to get data from trie
        """
        raise NotImplementedError('Please Implement fetch_from_trie method')

#################################################################
