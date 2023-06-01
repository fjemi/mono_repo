#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  string: str = ''
  word_dict: List[str] = dc.field(default_factory=lambda: [])


@dc.dataclass
class Data:
  body: Body | None = None
  sentences: List[str] = dc.field(default_factory=lambda: [])


async def build_sentence(
  index: int,
  word_dict: List[str],
  string: str,
) -> List[str]:
  sentence = []
  for i in range(index, len(word_dict)):
    word = word_dict[i]
    if string.find(word) != 0:
      continue
    sentence.append(word)
    string = string[len(word):]

  if len(string) != 0:
    sentence = []
  return sentence


async def get_sentences(
  word_dict: List[str],
  string: str,
) -> List[List[str]]:
  sentences = []
  for index in range(len(word_dict)):
    sentence = await build_sentence(
      index=index,
      word_dict=word_dict,
      string=deepcopy(string),
    )
    sentences.append(sentence)
  return sentences


async def process_sentences(sentences: List[List[str]]) -> List[str]:
  store = []
  for sentence in sentences:
    if len(sentence) == 0:
      continue
    sentence = ' '.join(sentence)
    store.append(sentence)
  return store


async def get_response(data: Data) -> dict:
  return {'sentences': data.sentences}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  string: str | None = None,
  word_dict: List[str] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data.sentences = await get_sentences(
    word_dict=data.body.word_dict,
    string=data.body.string,
  )
  data.sentences = await process_sentences(
    sentences=data.sentences)
  data = await get_response(data=data)
  return data
