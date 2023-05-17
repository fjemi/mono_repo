from app import run_server
from app import app

from fastapi.testclient import TestClient


client = TestClient(app)

