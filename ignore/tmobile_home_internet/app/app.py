from fastapi import FastAPI
from uvicorn import run
from dataclasses import dataclass, asdict
from os import getenv


app = FastAPI()


@app.post('/')
def hello_world():
    return {'Hello': 'World!'}


@dataclass
class ServerConfigs:
    host: str = getenv('API_HOST') or '0.0.0.0'
    port: int = getenv('API_PORT') or 8000
    reload: bool = getenv('API_RELOAD') or True
    workers: int = getenv('API_WORKERS') or 2


def run_server():
    server_configs = ServerConfigs()
    configs = asdict(server_configs)
    run(
        'app:app',
        **configs, )


if __name__ == '__main__':
    run_server()