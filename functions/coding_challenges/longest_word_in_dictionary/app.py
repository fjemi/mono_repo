#!/usr/bin/env python3

from typing import List, Dict
from dataclasses import dataclass, field, asdict
from copy import deepcopy
import yaml

from api import models


@dataclass
class Body(models.Body):
  words: List[str] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  string: str = ''
  words: List[str] = field(default_factory=lambda: [])
  string_sequences: List[List[str]] = field(default_factory=lambda: [])
  subsequences: Dict[int, List[str]] = field(default_factory=lambda: {})
  n: int = 0


def get_sequences(string: str) -> List[List[str]]:
  store = []
  n = len(string)

  # Handle empty string
  if n == 0:
    return store

  store = [[string[0]]]
  # Handle strings of length 1
  if n == 1:
    return store

  # Handle string of length n >= 2
  for i in range(1, n):
    sequence = store[-1]
    if string[i] not in sequence:
      sequence = [string[i]]
      store.append(sequence)
      continue
    sequence.append(string[i])
  return store


def subsequence_check(
  string_sequences: List[List[str]],
  word_sequences: List[List[str]],
) -> bool:
  n = len(string_sequences)
  m = len(word_sequences)

  # Handle case of word having more char sequences than string
  if m > n:
    return False

  # Handle all other cases
  store = []
  n = len(word_sequences)
  m = len(string_sequences)
  # Index to start iterating through string sequences
  start_index = 0

  # Iterate thorugh sequences of the word sequences
  for i in range(n):
    word_sequence = word_sequences[i]
    word_char = word_sequence[0]
    word_char_n = len(word_char)
    # Iterate through sequences of the string 
    # sequences to find matches
    for j in range(start_index, m):
      string_sequence = string_sequences[j]
      string_sequence_n = len(string_sequence)
      # Conditions for a word char to match a string 
      # sequence's char and order
      conditions = [
        word_char in string_sequence,
        word_char_n <= string_sequence_n,
      ]
      # Word char doesn't match the chars in the string sequence
      if sum(conditions) != len(conditions):
        continue
      # When word char matches chars in the string sequence
      # store the word char and set the start index for the 
      # string sequences to the current index
      store.append(word_char)
      start_index = j
      break

  if len(store) == n:
    return True
  return False


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)} 
    output: 
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.string_sequences = get_sequences(string=data.string)
  for word in data.words:
    word_sequences = get_sequences(string=word)
    check = subsequence_check(
      string_sequences=data.string_sequences, 
      word_sequences=word_sequences,
    )
    if check is False:
      continue
    # Store subsequences by length of word
    n = len(word)
    if n not in data.subsequences:
      data.subsequences[n] = []
    data.subsequences[n].append(word)
  return data


def example() -> None:
  data = '''
    string: aaabbc
  '''
  data = main(data=data)
  print(data)


if __name__ == '__main__':
  example()
