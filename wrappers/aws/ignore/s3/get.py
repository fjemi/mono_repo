#!/usr/bin/env python3

import boto3
from dataclasses import dataclass, field
from typing import Any, Callable, Dict
from os import path, makedirs
import json
import time

from shared.get_environment import app as get_environment
from shared.error_handler import app as error_handler
from shared.setup_data import app as setup_data


# TODO: GET configs from yaml
# CONFIGS = get_configs.main(f'module_path: {__file__}')
# ENV = get_environment.main(configs=CONFIGS)
# BUCKET = configs['bucket'][ENV.ENV]
ENV = get_environment.main(f'module_path: {__file__}')
BUCKET = '/sdcard/mono_repo/data/s3/'


@dataclass
class Data:
  bucket: str = field(default=BUCKET)
  file_name: str | None = None
  content: Any | None = None
  file_path: str | None = None
  key: str | None = None
  module_path: str | None = None
  folder_name: str | None = None
  

@error_handler.main()    
def case_session_not_none(
  session: 'Session', 
  env: 'Env' = None,
) -> 'Session':
  return session
  

@error_handler.main()    
def case_session_none_and_env_local(
  session: 'Session' = None, 
  env: 'Env' = None,
) -> 'Session':
  return None
  

@error_handler.main()    
def case_session_none_and_env_not_local(
  session: 'Session' = None, 
  env: 'Env' = None,
) -> 'Session':
  return boto3.Session(
    aws_access_key_id=env.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
    region_name=env.REGION_NAME,
  )
  
  
GET_SESSION = {
  "{'session': 1, 'env': 1}": case_session_none_and_env_local,
  "{'session': 1, 'env': 0}": case_session_none_and_env_not_local,
  "{'session': 0, 'env': 1}": case_session_not_none,
  "{'session': 0, 'env': 0}": case_session_not_none,
}


@error_handler.main()  
def get_session(
  env: 'Env' = ENV, 
  session: 'Session | None' = None,
) -> 'Session | None':
  conditions = {
    'session': int(session is None),
    'env': int(env.ENV == 'local'), 
  }
  conditions = str(conditions)
  function = GET_SESSION[conditions]
  return function(session=session, env=env)
  

@error_handler.main()    
def case_client_not_none(
  client: 'S3', 
  session: 'Session | None', 
) -> 'S3':
  return client
  

@error_handler.main()  
def case_client_none_session_none(
  client: 'S3', 
  session: 'Session | None', 
) -> None:
  return None
  

@error_handler.main()    
def case_client_none_session_not_none(
  client: 'S3', 
  session: 'Session | None', 
) -> 'S3':
  return session.client('s3')
  
    
GET_CLIENT = {
  "{'client': 1, 'session': 0}": case_client_none_session_not_none,
  "{'client': 0, 'session': 1}": case_client_not_none,
  "{'client': 1, 'session': 1}": case_client_none_session_none,
  "{'client': 0, 'session': 0}": case_client_not_none,
}


@error_handler.main()
def get_client(
  session: 'Session | None', 
  client: 'S3 | None',
) -> 'S3 | None':
  conditions = {
    'client': int(client is None),
    'session': int(session is None),
  }
  conditions = str(conditions)
  function = GET_CLIENT[conditions]
  return function(
    session=session, 
    client=client,
  )
  
  
@error_handler.main()
def case_folder_name_not_none(
  folder_name: str,
  module_path: str | None,
) -> str:
  return folder_name
  
  
@error_handler.main()  
def case_folder_name_and_module_path_are_none(
  folder_name: None,
  module_path: None,
) -> str:
  return ''
  
  
@error_handler.main()  
def case_folder_name_and_module_path_are_not_none(
  folder_name: None | str,
  module_path: str,
) -> str:
  directory = path.dirname(module_path)
  return path.basename(directory)
  

GET_FOLDER_NAME = {
  '[1, 0]': case_folder_name_not_none,
  '[0, 1]': case_folder_name_and_module_path_are_not_none,
  '[1, 1]': case_folder_name_and_module_path_are_none,
  '[0, 0]': case_folder_name_and_module_path_are_not_none,
}
  
  
@error_handler.main()  
def get_folder_name(
  module_path: str | None = None,
  folder_name: str | None = None,
) -> str | None:
  conditions = [
    int(module_path is None),
    int(folder_name is None or len(folder_name) == 0),
  ]
  conditions = str(conditions)
  function = GET_FOLDER_NAME[conditions]
  return function(module_path=module_path, folder_name=folder_name)


@error_handler.main()
def get_timestamp_key(
  key: None = None,
  file_path: None = None
) -> str:
  timestamp = time.time()
  return str(timestamp)


GET_KEY = {
  0: lambda key, file_path: path.basename(file_path),
  1: lambda key, file_path: key,
  2: lambda key, file_path: get_timestamp_key(key=key, file_path=file_path),
}

  
@error_handler.main()
def get_key(
  file_path: str | None, 
  key: str | None,
  module_path: str | None,
  folder_name: str | None,
) -> str:
  folder_name = get_folder_name(
    module_path=module_path,
    folder_name=folder_name
  )
  conditions = [
    key is None and file_path is not None,
    key is not None,
    key is None and file_path is None
  ]
  _case = conditions.index(1)
  function = GET_KEY[_case]
  key = function(
    file_path=file_path,
    key=key,
  )
  return path.join(folder_name, key) 
  
  
@error_handler.main()
def case_content_not_none(content: Any, file_path: None = None) -> str:
  return json.dumps(content)
  
  
@error_handler.main()  
def case_file_path_not_none(
  file_path: str, 
  content: Any | None = None,
) -> str | None:
  with open(file_path, 'r') as file:
    return file.read()
    

CASE_UPLOAD_TO_FILE_SYSTEM = {
  '[0, 1]': case_content_not_none,
  '[1, 0]': case_file_path_not_none,
  '[0, 0]': case_file_path_not_none,
  '[1, 1]': lambda *x: '',
}


@error_handler.main(return_value=False)
def case_upload_to_file_system(
  client: None, 
  bucket: str, 
  file_path: str | None = None, 
  content: Any = None,
  key: str | None = None,
) -> bool:
  conditions = [
    int(content is None),
    int(file_path is None),
  ]
  conditions = str(conditions)
  function = CASE_UPLOAD_TO_FILE_SYSTEM[conditions]
  content = function(content=content, file_path=file_path)
  # Save to file system
  target_path = path.join(bucket, key)
  # Create the directory if it doesn't exist
  directory = path.dirname(target_path)
  if path.exists(directory) is False:
    makedirs(directory)
  # Save to file system
  with open(target_path, 'w') as file:
    file.write(content)
  return True


@error_handler.main(return_value=False)
def case_upload_to_s3(
  client: 'S3', 
  bucket: str, 
  file_path: str, 
  content: Any = None,
  key: str | None = None,
) -> bool | None:
  if content is not None:
    client.upload_fileobj(
      Fileobj=content, 
      Bucket=bucket, 
      Key=key,
    )
    return True

  if file_name is not None: 
    client.upload_file(
      Filename=file_name, 
      Bucket=bucket, 
      Key=key,
    )
    return True


UPLOAD = {
  0: case_upload_to_s3,
  1: case_upload_to_file_system,
}


@error_handler.main(return_value=False)
def upload(
  client: 'S3 | None', 
  bucket: str,
  file_path: str | None = None, 
  content: Any | None = None,
  key: str | None = None, 
) -> bool:
  _case = int(client is None)
  function = UPLOAD[_case]
  response = function(
    client=client,
    bucket=bucket,
    file_path=file_path,
    content=content,
    key=key,
  )
  return response
  

# @error_handler.main()
def main(
  data: Data | dict | str,
  session: 'Session | None' = None,
  client: 'S3 | None' = None,
) -> Any:
  data = setup_data.main(data=data, data_class=Data)
  session = get_session(env=ENV, session=session)
  client = get_client(session=session, client=client)
  data.key = get_key(
    file_path=data.file_path, 
    key=data.key,
    module_path=data.module_path,
    folder_name=data.folder_name,
  )
  response = upload(
    client=client,
    bucket=data.bucket,
    key=data.key,
    content=data.content,
    file_path=data.file_path,
  )
  return response


def example() -> None:
  data = f'''
    module_path: {__file__}
    file_path: null
    content: 
      test: test
    key: test.txt
    folder_name: test
  '''
  data = main(data=data)
  print(data)


if __name__ == '__main__':
  example()
