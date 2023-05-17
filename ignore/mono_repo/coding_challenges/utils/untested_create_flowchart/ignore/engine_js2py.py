import js2py
require = js2py.require('require')

js_code = 'function console_log() {return "Hello World!"}'
python_code = js2py.eval_js(js_code)


js_code = "const axios = require('axios')"
python_code = js2py.eval_js(js_code)

if __name__ == '__main__':
  print(python_code())