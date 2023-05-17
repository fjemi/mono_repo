#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Dict
from math import floor
from copy import deepcopy
import yaml

from api import models


@dataclass
class Transformation:
  sequence: str | List[str] | None = None
  words: List[str] = field(default_factory=lambda: [])


@dataclass 
class Body(models.Body):
  begin_word: str = ''
  end_word: str = ''
  word_list: List[str] | None = None


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class ModuleData:
  body: Body | None = None
  transformations: List[str] | Dict[int, List[List[str]]] = field(default_factory=lambda: [])
  shortest_transformation: int = 0
  stay_in_loop: bool = True


async def pre_processing(data: ModuleData) -> ModuleData:
  # No possible transformation sequence possible
  # if end word not in list of available words
  if data.body.end_word not in data.body.word_list:
    data.stay_in_loop = False
    return data

  # Set the root word and available
  # words for transformation sequences
  root = Transformation(
    sequence=data.body.begin_word,
    words=data.body.word_list,
  )
  data.transformations.append([root])
  return data


async def calculate_distance_between_two_strings(
  string_one: str,
  string_two: str,
) -> float:
  n_one = len(string_one)
  n_two = len(string_two)
  max_n = max([n_one, n_two])
  difference = 0

  for i in range(max_n):
    # Handle strings of different lengths.
    # Increment distance counter and set chars to empty string.
    try:
      char_one = string_one[i]
      char_two = string_two[i]
    except IndexError:
      char_one = ''
      char_two = ''
      difference += 1
    # No transformation (deletion, insertion, or swap)
    # needed if chars are the same
    if char_one == char_two:
      continue
    difference += 1

  difference = floor((max_n - difference) / max_n * 100)
  return difference


async def get_next_words_in_sequence(
  words: List[str],
  sequence_end: str,
) -> List[str]:
  end_n = len(sequence_end)
  # Distance between end and next word of sequence
  # should be match this. Only one char needed to be
  # changed in next word to get the end word
  match_difference = floor((end_n - 1) / end_n * 100)

  # Calculate difference between end word and available words
  store = {}
  for word in words:
    distance = await calculate_distance_between_two_strings(
      string_one=sequence_end,
      string_two=word,
    )
    if distance not in store:
      store[distance] = []
    store[distance].append(word)
  # Return words that match the difference
  if match_difference not in store:
    return []
  return store[match_difference]


async def build_out_transformations(
  transformations: List[List[Transformation]],
  stay_in_loop: bool,
  end_word: str,
) -> List[Transformation]:
  if stay_in_loop is False:
    return transformations

  while stay_in_loop is True:
    store = []
    last_transformations = transformations[-1]
    for transformation in last_transformations:
      sequence_end = transformation.sequence.split('.')[-1]
      next_words_in_sequence = await get_next_words_in_sequence(
        words=transformation.words,
        sequence_end=sequence_end,
      )
      for word in next_words_in_sequence:
        # Create next sequence and list of available words
        next_sequence = f"{transformation.sequence}.{word}"
        next_words = deepcopy(transformation.words)
        # Remove last word in next sequence from next list of available words
        index = next_words.index(word)
        del next_words[index]

        transformation = Transformation(
          sequence=next_sequence,
          words=next_words,
        )
        store.append(transformation)
        if word == end_word:
          stay_in_loop = False

    transformations.append(store)
  return transformations


async def process_transformations(
  transformations: List[Transformation],
  end_word: str,
) -> Dict[int, List[List[str]]]:
  if len(transformations) == 0:
    return {}

  transformations = transformations[-1]
  store = {}
  for transformation in transformations:
    sequence = transformation.sequence
    # sequence = sequence['sequence']
    if sequence.find(end_word) == -1:
      continue
    sequence = sequence.split('.')
    sequence_n = len(sequence) - 1
    if sequence_n not in store:
      store[sequence_n] = []
    store[sequence_n].append(sequence)
  return store


async def get_response(data: ModuleData) -> models.Response:
  n = data.shortest_transformation
  values = []
  if n != 0:
    values = data.transformations[n]

  data = f'''
    input: {asdict(data.body)}
    output:
      shortest_transformation: 
        n: {n}
        values: {values}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data
  

async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  request = None
  data = await pre_processing(data=data)
  data.transformations = await build_out_transformations(
    transformations=data.transformations,
    end_word=data.body.end_word,
    stay_in_loop=data.stay_in_loop,
  )
  data.transformations = await process_transformations(
    transformations=data.transformations,
    end_word=data.body.end_word,
  )
  data.shortest_transformation = min(data.transformations) if data.transformations != {} else 0
  data = await get_response(data=data)
  return data
