

from dataclasses import dataclass, field
from os import path
from shelve import DbfilenameShelf
import zlib
from urllib.request import urlopen

from api import models
from shared.get_environment import app as get_environment
# from shared.get_request_form_data import app as get_form_data
from wrappers.aws import app as aws


ENV = get_environment.main(f'module_path: {__file__}')
THIS_FILE_PATH = __file__


@dataclass
class Storage:
  this_file_path = THIS_FILE_PATH
  persistent: DbfilenameShelf | None = None
  s3_bucket: str = ENV.S3_BUCKET
  folder: str | None = None
  directory: str = ENV.DATA_PATH


@dataclass
class Data:
  content: str | None = None
  form: models.Form | None = None
  storage: Storage = field(default_factory=lambda: Storage())
  response: models.Response = field(
    default_factory=lambda: models.Response())


async def add_chunk_to_persistent_storage(data: Data) -> Data:
  file_name = data.form.json.file_name
  if file_name not in data.storage.persistent.keys():
    data.storage.persistent[file_name] = {}

  chunks = data.storage.persistent[file_name]
  chunk = f'chunk_{data.form.json.chunk_i}'
  chunks[chunk] = data.form.binary.content
  data.storage.persistent[file_name] = chunks
  return data


async def combined_chunks(data: Data) -> bytes:
  if data.form.json.chunk_i + 1 != data.form.json.chunks_n:
    return None

  file_name = data.form.json.file_name
  chunks = list(data.storage.persistent[file_name].values())
  chunks_n = len(chunks)

  if data.form.json.chunks_n != chunks_n:
    message = 'One or more previous chunk was not received'
    raise RuntimeError(message)

  content = b''
  for i in range(chunks_n):
    content += chunks[i]
  return content


async def remove_chunks(data: Data) -> Data:
  if data.content is not None:
    file_name = data.form.json.file_name
    del data.storage.persistent[file_name]
    data.storage.persistent = None
  return data


async def decompress_content(content: bytes) -> str:
  if content is None:
    return content

  decompress = zlib.decompressobj(15)
  content = decompress.decompress(content)
  content += decompress.flush()
  content = content.decode('utf-8')
  return content


async def process_data_url_content(
  content: str,
  read_as: str,
) -> str:
  if read_as != 'data_url':
    return content

  data = None
  with urlopen(content) as response:
    data = response.read()
  return data


async def set_final_storage(data: Data) -> Data:
  folder = path.dirname(data.storage.this_file_path)
  folder = path.dirname(folder)
  folder = path.basename(folder)
  data.storage.folder = folder
  return data


async def save_content_to_file_system(data: Data) -> bool:
  directory = path.join(
    data.storage.directory, 
    data.storage.folder,
  )
  if path.exists(directory) is False:
    makedirs(directory)
  file_path = path.join(
    directory, 
    data.form.json.file_name,
  )
  mode = 'w+'
  if data.form.json.read_as == 'data_url':
    mode = 'wb+'
  with open(
    file=file_path,
    mode=mode,
    encoding='utf-8',
  ) as file:
    file.write(data.content)
  return True


async def save_content_to_s3(data: Data) -> bool:
  key = '{folder}/chunk_{file_name}'.format(
    folder=data.storage.folder,
    file_name=data.form.json.file_name,
  )
  data = f'''
    service_name: s3.put_object
    service_params:
      Bucket: {data.storage.s3_bucket}
      Body: {data.content}
      Key: {key}
    parse_response:
    - ResponseMetadata.HTTPStatusCode
  '''
  response = aws.main(data=data)
  return response.request_response


SAVE_CONTENT = {
  'file_system': save_content_to_file_system,
  's3': save_content_to_s3,
}


async def save_content_to_final_destination(data: Data) -> bool:
  if data.content is None:
    return False
  function = SAVE_CONTENT[data.form.json.location]
  result = await function(data=data)
  return result


async def get_response(data) -> models.Response:
  response_data = {
    'message': 'Chunk saved to persistent storage',
    'chunk': data.form.json.chunk_i,
    'file_name': data.form.json.file_name,
  }
  if data.content is not None:
    message = f'Chunks combined and file saved to {data.form.json.location}'
    response_data['message'] = message
    del response_data['chunk']
  response = models.Response(data=response_data)
  return response


async def main(
  request: 'Request',
  persistent_storage: DbfilenameShelf,
) -> dict:
  data = Data(form=request.data.form)
  data.storage = Storage(persistent=persistent_storage)
  data = await add_chunk_to_persistent_storage(data=data)
  data.content = await combined_chunks(data=data)
  data = await remove_chunks(data=data)
  data.content = await decompress_content(content=data.content)
  data.content = await process_data_url_content(
    content=data.content,
    read_as=data.form.json.read_as,
  )
  data = await set_final_storage(data=data)
  result = await save_content_to_final_destination(data=data)
  data.response = await get_response(data=data)
  return data.response
f'File saved to {data.form.json.location}'