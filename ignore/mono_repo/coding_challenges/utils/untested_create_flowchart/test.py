# import webbrowser



# file_name = '/home/femij/mono_repo/coding_challenges/utils/untested_create_flowchart/ignore/test/web/index.html'
# webbrowser.open(file_name)
# print(dir(webbrowser))
# print(webbrowser.subprocess)


import requests
from dataclasses import dataclass
from requests_html import HTMLSession

from shared.untested_error_handler import app as error_handler


@dataclass
class Data:
  ping_url: str = 'https://google.com'
  network_connection_active: bool = False


# @error_handler.main
def check_network_connection_active(data: Data) -> Data:
  response = requests.get(data.ping_url)
  if response.status_code == 200:
    data.network_connection_active = True
  return data





def main(data) -> Data:
  data = check_network_connection_active(data=data)

  return data


if __name__ == '__main__':

  data = Data()
  data = main(data=data)
  print(data)


# sessions = HTMLSession()
# url = 'https://pythonclock.org'
# url = 'file:///home/femij/mono_repo/coding_challenges/utils/untested_create_flowchart/index.html'
# r = sessions.get(url)
# r.html.render()
# raw_html = r.html.raw_html
# svg = r.html.find('svg', first=True)
# print(svg.raw_html)

from requests_html import HTML


file_path = '/home/femij/mono_repo/coding_challenges/utils/untested_create_flowchart/index.html'
with open(file_path) as file:
  source_code = file.read()
  parsed_html = HTML(html=source_code)
  parsed_html.render(retries=2, sleep=1)
  
  print(dir(parsed_html), parsed_html.html)
  parsed_html.browser


# import jinja2

# environment = jinja2.Environment()
# template = environment.from_string('''
#   <!DOCTYPE html>
#   <html>
#   <head>
#   <meta id="data" value='{{data|safe}}'>
#   </head>
#   <body>
#   <div class="display" id="display"></div>
  
#   <script src="https://cdnjs.cloudflare.com/ajax/libs/raphael/2.3.0/raphael.min.js"></script>
#   <script src="https://cdnjs.cloudflare.com/ajax/libs/flowchart/1.17.1/flowchart.min.js"></script>
#   <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
#   </body>
#   </html>
# ''')

# data = '''
#   st0=>start: start a_pyflow_test:>https://google.com
#   op1=>operation: do something
#   cond2=>condition: Yes or No?
#   io3=>inputoutput: output: something...
#   sub4=>subroutine: A Subroutine
#   e5=>end: end a_pyflow_test


#   st0->op1
#   op1->cond2
#   cond2(yes,)->io3
#   cond2(no,)->sub4
#   io3->e5
#   sub4(right)->op1
# '''
# template = template.render(data=data)
# print(template)

