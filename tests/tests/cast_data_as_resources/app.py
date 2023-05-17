from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass
from dataclasses import dataclass as standard_dataclass


@standard_dataclass
class Standard_Dataclass:
  a: int = None
  b: int = None


class Basemodel(BaseModel):
  a: int = None
  b: int = None


@pydantic_dataclass
class Pydantic_Dataclass:
  a: int = None
  b: int = None


String = str
