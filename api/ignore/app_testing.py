#!/usr/bin/env python3

from typing import List, Any
from dataclasses import dataclass
from fastapi import FastAPI, Request
import uvicorn
import pathlib
import asyncio

from shared.get_environment import app as get_environment
from shared.load_function_from_path import app as load_function_from_path
from shared.get_persistant_storage import app as get_persistant_storage


THIS_MODULE_PATH = __file__
ENV = get_environment.main(f'module_path: {THIS_MODULE_PATH}')
PERSISTANT_STORAGE = None


@dataclass
class Data:
  route: str | List[str] | None = None
  # working_directory: str = field(defualt_factory=lambda: ENV.WORKINGDIR)


app = FastAPI()


# # print(dir(app))
# # print(app.openapi_schema)

# # # print(type(app).__name__)
# # # print(app.routes)
# import inspect
# # signature = inspect.signature(app.openapi)
# signature = inspect.signature(app.add_api_route)
# print(signature)


# def test():
#   return 'test'


# # def custom_openapi(app: FastAPI = app):
# #   if app.openapi_schema:
# #       return app.openapi_schema
# #   from fastapi.openapi.utils import get_openapi
# #   openapi_schema = get_openapi(
# #       title="Custom title",
# #       version="2.5.0",
# #       description="This is a very custom OpenAPI schema",
# #       routes=app.routes,
# #   )
# #   import json
# #   print(app.routes)
# #   print(json.dumps(openapi_schema, indent=2))
# #   #del[openapi_schema['content']['/items/']]
# #   openapi_schema["paths"]['root'] = {
# #       "get": {
# #           "requestBody": {"content": {"application/json": {}}, "required": True}, "tags": ["Test"]
# #       }}
# #   openapi_schema["paths"]["/api/auth"] = {
# #       "post": {
# #           "requestBody": {
# #             "content": {
# #               "application/json": {}
# #             }, 
# #             "required": True,
            
# #           }, 
# #           "tags": ["Auth"]
# #       },
# #       "parameters": [
# #         {
# #           "name": "id",
# #           "in": "path",
# #           "description": "ID of pet to use",
# #           "required": True,
# #           "schema": {
# #             "type": "array",
# #             "items": {
# #               "type": "string"
# #             }
# #           },
# #           "style": "simple"
# #         }
# #       ]
# #   }
# #   app.openapi_schema = openapi_schema
# #   return app.openapi_schema

# # print('custom_openapi', custom_openapi, '\n\n')
# # app.openapi = custom_openapi
# # print(app.openapi_schema)

# openapi_schema = '''
#   openapi: 3.0.2
#   info:
#     title: API Title
#     description: API Description
#     version: 2.0.5
#   tags:
#   - name: API
#     description: Single API for handling GET and POST routes.
#   - name: Functions
#     description: Functions to call to process requests
#   - name: Pages
#     description: Pages or templates served from GET routes
#   paths:
#     /{function_path}/:
#       get:
#         tags: 
#         - API
#         summary: Function Path
#         operationId: call_function.get
#         parameters:
#         - in: path
#           name: function_path
#           schema:
#             type: string
#           required: True
#           example: api.functions.ping
#           description: |
#             Dot delimited path to a function to call to process the request. The path starts from a folder in the working directory of the app, which is set to the environment variable `WORKDIR`, and the **main** function in the module **app.py** is returned.
#         - in: query
#           name: data
#           required: False
#           example: {}
#           schema:
#             type: object
#           description: Data for the function to process
#         responses:
#           200: 
#             description: Successful Response
#             content: 
#               application/javascript:
#                 schema:
#                   type: object
#                   additionalProperties: true
#                 example:
#                   ping: pong
#               text/plain:
#                 schema:
#                   oneOf:
#                   - type: string
#                   - type: integer
#                 example: |
#                   {"ping": "pong"}
#       post:
#         tags:
#         - API
#         summary: Function Path
#         operationId: call_function.post
#         parameters:
#         - in: path
#           name: function_path
#           schema:
#             type: string
#           required: True
#           example: api.functions.hello_world
#           description: |
#             Dot delimited path to a function to call to process the request. The path starts from a folder in the working directory of the app, which is set to the environment variable `WORKDIR`, and the **main** function in the module **app.py** is returned.
#         requestBody:
#           content:
#             application/json:
#               schema: 
#                 type: object
#                 additionalProperties: true
#                 example: 
#                   name: Mars
#             text/plain:
#               schema: 
#                 type: string
#               example: |
#                   name: Jupyter
#             multipart/form-data: 
#               schema:
#                 properties: 
#                   meta-data:
#                     type: string
#                     format: binary
#                     example: |
#                       {"file_name": "someimage.jpg", "file_size_kb": "100"}
#                   file:
#                     type: array
#                     items:
#                       type: string
#                       format: binary
#                     example:
#                     - externalValue: http://wwww.someimage.com
#         responses:
#           200: 
#             description: Successful Response
#             content: 
#               application/javascript:
#                 schema:
#                   type: object
#                   additionalProperties: true
#                 example:
#                   text: Hello World!
#               text/plain:
#                 schema:
#                   oneOf:
#                   - type: string
#                   - type: integer
#                   - type: array
#                   - type: null
#                   - type: object
#                 example: |
#                   text:
#                     Hello World!
# '''
# import yaml
# openapi_schema = yaml.safe_load(openapi_schema)
# app.openapi_schema = openapi_schema


# # async def get_handler(
# #   request: Request,
# #   persistant_storage: get_persistant_storage.DbfilenameShelf = PERSISTANT_STORAGE,
# # ) -> Any:
# #   data = f'''
# #     function:
# #       directory: {request.query_params['route']}
# #   '''
# #   function = await load_function_from_path.main(data=data)
# #   response = await function(
# #     request=request,
# #     persistant_storage=persistant_storage,
# #   )
# #   return response


# # async def handle_application_json(request: Request) -> dict:
# #   body = await request.json()
# #   body = PostData(**body)
# #   setattr(request, 'data', body)
# #   request.json = None
# #   return request


# # async def handle_text_plain(request: Request) -> Request:
# #   body = await request.body()
# #   body = yaml.safe_load(body)
# #   body = PostData(**body)
# #   setattr(request, 'data', body)
# #   request.body = None
# #   return request


# # async def handle_multipart_form_data(request: Request) -> Request:
# #   form = await request.body()
# #   body = f'''
# #     function: {request.headers.get('route')},
# #     data:
# #       form: {form}
# #   '''
# #   body = PostData(**body)
# #   setattr(request, 'data', body)
# #   # request.body = None
# #   return request


# # CONTENT_HANDLER = {
# #   'application/json': handle_application_json,
# #   'text/plain': handle_text_plain,
# #   'multipart/form-data': handle_multipart_form_data,
# # }  


# # async def post_handler(
# #   request: Request,
# #   persistant_storage: get_persistant_storage.DbfilenameShelf = PERSISTANT_STORAGE,
# # ) -> Any:
# #   content_type = request.headers.get('Content-Type')
# #   content_handler = CONTENT_HANDLER[content_type]
# #   print(content_handler, content_type)
# #   ...


# # METHOD_HANDLER = {
# #   'GET': get_handler,
# #   'POST': post_handler,
# # }


# # from fastapi import UploadFile
# # @app.post('/upload/')
# # async def create(file: UploadFile):
# #   return {'filename': file.filename}


@app.api_route(
  path='/{function_path}/', 
  methods=['GET', 'POST'],
)
@app.api_route(
  path='/{function_path}',
  methods=['GET', 'POST'],
  include_in_schema=False,
)
async def call_function(
  request: Request, 
) -> Any:
  # Route is used to determine which function to use
  function_path = request.path_params.get('function_path')
  function_path = function_path.lower()
  function_data = f'''
    function:
      directory: {function_path}
  '''
  function = await load_function_from_path.main(data=function_data)
  response = await function(
    request=request,
    persistant_storage=PERSISTANT_STORAGE,
  )
  return response

  

async def start_server(env: 'Env', module_name: str) -> None:
  uvicorn.run(
    f'{module_name}:app', 
    host=env.API_HOST, 
    port=int(env.API_PORT), 
    reload=env.API_RELOAD,
    workers=int(env.API_WORKERS),
  )


async def get_this_module_name(
  module_path: str = ,
) -> str:
  path = pathlib.Path(module_path)
  file_name = path.stem
  return file_name


@app.on_event('startup')
async def main() -> None:
  module_name = await get_this_module_name()
  global PERSISTANT_STORAGE
  if PERSISTANT_STORAGE is None:
    PERSISTANT_STORAGE = await get_persistant_storage.main()
  await start_server(env=ENV, module_name=module_name)


if __name__ == '__main__':
  import asyncio
  

  asyncio.run(main())
  