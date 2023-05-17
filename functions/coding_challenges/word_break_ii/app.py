#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
from copy import deepcopy
import yaml

from api import models


@dataclass 
class Body(models.Body):
  string: str = ''
  word_dict: List[str] = field(default_factory=lambda: [])


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class ModuleData:
  body: Body | None = None
  sentences: List[str] = field(default_factory=lambda: [])


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


async def get_response(data: ModuleData) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      sentences: {data.sentences}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  data.sentences = await get_sentences(
    word_dict=data.body.word_dict,
    string=data.body.string,
  )
  data.sentences = await process_sentences(
    sentences=data.sentences)
  data = await get_response(data=data)
  return data
