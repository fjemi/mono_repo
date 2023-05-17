#!/usr/bin/env python3

from append_sys_path import append_sys_path; append_sys_path()
from app import app
from fastapi.testclient import TestClient
from fastapi import HTTPException


client = TestClient(app)


def test_root():
  '''Test API Get request in `../api/app/app.py`
  '''
  response = client.get('/')
  assert response.status_code == 200


def test_api():
  '''Test the API Post request in `../api/app/app.py`
  '''
  # no route passed
  response = client.post('/api', {})
  assert response.status_code == 422 or response.status_code == 405
  # data is not a valid json
  response = client.post('/api', json={'route': 'ping', 'data': {}})
  assert response.status_code == 200


if __name__ == '__main__':
  tests = [test_root, test_api]
  for test in tests:
    test()
    print(f'{test.__name__}: Succesful')
  
  
