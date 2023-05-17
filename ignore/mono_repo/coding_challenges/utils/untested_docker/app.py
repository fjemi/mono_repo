import docker
from dataclasses import dataclass


@dataclass
class Data:
  image: str = ''



client = docker.from_env()
client.containers.run("ubuntu:latest", "sleep infinity", detach=True)
client.close()

if __name__ == '__main__':
  pass