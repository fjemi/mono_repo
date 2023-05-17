from dataclasses import dataclass, field
  
  
@dataclass
class Data:
  a: int = 0
  b: int = 0
  remove_fields: List[str] = field(default_factory=lambda: [])
