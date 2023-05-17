edibles = [
  dict(name='gummies', thc=100, price=20),
  dict(name='gummies', thc=500, price=70),
  dict(name='gummies', thc=300, price=40), 
]

for edible in edibles:
  print(edible['name'], edible['thc'] / edible['price'])