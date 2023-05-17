
from dataclasses import dataclass, asdict
import json
# Type hints
import numbers
from datetime import datetime


@dataclass
class Model:
  '''Get user infor (name, age, username) and return it as a string
  '''
  name: str
  age: int
  username: str
  time: str = str(datetime.utcnow())
  
  def __post_init__(self):
    '''Check it valid types were passed, and set output if so
    '''
    valid_attribute_types = True
    # Use abstract base class for integers
    valid_types = [str, numbers.Integral, str, str]
    
    # Validate entry types
    for i, item in enumerate(vars(self)):
      if not isinstance(vars(self)[item], valid_types[i]):
        valid_attribute_types = False
        self.output = f'Invalid {item} entry'
    
    # Output results if entries are valid
    if valid_attribute_types:  
      output = f'your name is {self.name}\nyou age is {self.age}\nyour username is {self.username}'
      print(output)
      
      # Log results
      with open('log.txt', 'a+') as file:
        log = json.dumps(asdict(self))
        file.write(f'{log}\n')
  
  
if __name__ == '__main__':
  M = Model(
    name='Femi',
    age=1,
    username='pass'
  )
  #print(json.dumps(asdict(M), indent=2))
