from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()


@app.get("/root")
async def root():
  '''
  Summary
  
  Parameters
    name: The name of the person or thing to greet
  
  Returns
  '''
  return {"hello": "world"}


@app.get("/items/")
async def read_items():
    return [{"name": "Foo"}]


def custom_openapi(app=app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    import json
    print(app.routes)
    print(json.dumps(openapi_schema, indent=2))
    #del[openapi_schema['content']['/items/']]
    openapi_schema["paths"]['root'] = {
        "get": {
            "requestBody": {"content": {"application/json": {}}, "required": True}, "tags": ["Test"]
        }}
    openapi_schema["paths"]["/api/auth"] = {
        "post": {
            "requestBody": {
              "content": {
                "application/json": {}
              }, 
              "required": True,
              
            }, 
            "tags": ["Auth"]
        },
        "parameters": [
          {
            "name": "id",
            "in": "path",
            "description": "ID of pet to use",
            "required": True,
            "schema": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "style": "simple"
          }
        ]
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == '__main__':
  import uvicorn


  uvicorn.run(
    'app:app',
    host="0.0.0.0",
    port=8000,
    reload=True,
    workers=2, )