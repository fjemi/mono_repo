#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  words: List[str] | None = None
  k: int = 0


@dc.dataclass
class TopKWords:
  values: List[str] | None = None
  n: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  counts: Dict[str, int] = dc.field(default_factory=lambda: {})
  top_k_words: TopKWords | None = None


async def get_counts(words: List[str]) -> Dict[str, int]:
  counts = {}
  for word in words:
    if word not in counts:
      counts[word] = 0
    counts[word] += 1
  return counts


async def process_counts(counts: Dict[str, int]) -> List[str]:
  # Number of zeros to pad count
  counts_n = len(counts)
  counts_n = len(str(counts_n))
  # Combine counts and words into single string for sorting
  store = []
  for word, count in counts.items():
    count = str(count).zfill(counts_n)
    word = f'{count}.{word}'
    store.append(word)
  store.sort(reverse=True)
  return store


async def get_top_k_words(counts: List[str], k: int) -> List[str]:
  counts = counts[:k]
  store = {}
  for count_word in counts:
    count, word = count_word.split('.')
    if count not in store:
      store[count] = []
    store[count].append(word)
    store[count].sort()

  values = list(store.values())[0]
  n = len(values)
  top_k_words = TopKWords(values=values, n=n)
  return top_k_words


async def get_response(data: Data) -> dict:
  return {
    'top_k_words': data.top_k_words.values,
    'count': data.top_k_words.n,
  }


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  words: List[str] | None = None,
  k: int | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.counts = await get_counts(words=data.body.words)
  data.counts = await process_counts(counts=data.counts)
  data.top_k_words = await get_top_k_words(counts=data.counts, k=data.body.k)
  data = await get_response(data=data)
  return data
