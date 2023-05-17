from yaml import safe_load


#@error_handler(message=f'Nonfig file not found', type='warning')
def get_config(path: str, type: str) -> dict:
    '''
    description: Loads the configurations for a python script at a specified path
    paramters: 
      - name: path
        type: str
        description: The path to a python file
    returns: dict
    '''
    
    config_path = path.replace('.py', '.yml')
    with open(config_path, 'r') as file:
        return safe_load(file)
