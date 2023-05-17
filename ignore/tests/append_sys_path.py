

def append_sys_path() -> 'None':
  import sys
  
  ''''''
  paths = [
    '../app',
    '../app/routes',
    '../app/utils']
  
  # add paths to environment
  for path in paths:
    sys.path.insert(0, path)
  
  return None


if __name__ == '__main__':
  append_sys_path()
  from os import environ
  print(environ)

