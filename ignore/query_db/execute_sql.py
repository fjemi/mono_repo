

from dataclasses import dataclass


@dataclass
class DB_Connection:
  db: str = 'db'
  user: str = 'user'
  host_address: str = '0.0.0.0'
  password: str | None = None
  port: int = 5432


@dataclass
class Data:
  db_connection: DB_Connection | None = None
  query_string: str | None = None
  


def set_connection(data: 'dict') -> 'dict':
  ''''''

  #data = ConnectParams(**data)
  db_connection = DB_Connection()

  

  return db_connection




'''
import psycopg2
from os import environ

connection = psycopg2.connect(
    environ['DB_URL']
  )
connection.autocommit = True
'''


def execute_sql(data: 'dict'):
  ''''''
  
  data = Data(**data)
  
  print(vars(data))
  return vars(data)

if __name__ == '__main__':
  execute_sql({})
