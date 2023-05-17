'''Find longest word in list that is a subsequence of a string
https://techdevguide.withgoogle.com/resources/find-longest-word-in-dictionary-that-subsequence-of-given-string/#!
'''
# Library to get the maximum value from a dictionary
import operator

# Data modeling
from dataclasses import dataclass, asdict, field
import json
# Type hints
from typing import List, Dict, Any
# Arrays
import numpy as np

@dataclass
class Model:
  '''Finds the longest word in a last that is subsequence of a string
  '''
  string: str
  words: List[str]
  subsequences: List = field(default_factory=lambda: [])
  longest_subsequence: List = field(default_factory=lambda: None)
  
  def __post_init__(self):
    '''Execute after the class initializes
    '''
    
    def check_subsequence(string, word):
      '''Check whether a word is a subsequence of a string
      '''
      
      # Check if the word is larger than the string
      if len(word) > len(string):
        return -1
      
      # Check if word chars a sub list of the string chars
      for char in word:
        if char not in list(string):
          return -1
        
      # Store removed chars and indices
      removed_chars = {}
      
      # Add matching chars to the Store
      for i, sub_char in enumerate(string):
        for word_char in word:
          if sub_char == word_char:
            if sub_char not in removed_chars.keys():
              removed_chars[sub_char] = i
      
      # Subsequence if store keys match word
      if list(removed_chars.keys()) == list(word):
        return len(word)
      
      return -1
    
    # Set all subsequences and the longest ones
    max = 0
    for word in self.words:
      cs = check_subsequence(self.string, word)
      if cs != -1:
        self.subsequences.append(word)
        if cs > max:
          self.longest_subsequence = [word]
        if cs == max:
          self.longest_subsequence.append(word)

if __name__ == '__main__':
  STRING = "abppplee"
  WORDS = ["able", "ale", "apple", "bale", "kangaroo", "abple"]
  M = Model(string, words)
  print(json.dumps(asdict(M), indent=2))
  
