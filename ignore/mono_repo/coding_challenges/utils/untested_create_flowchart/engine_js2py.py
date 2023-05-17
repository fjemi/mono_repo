import js2py
axios = js2py.require('axios')

js_code = 'function console_log() {return "Hello World!"}'
python_code = js2py.eval_js(js_code)




if __name__ == '__main__':
  print(python_code())


import os

