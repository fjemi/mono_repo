from dataclasses import dataclass, field
import requests
# from os import path
import jinja2
import requests_html

from shared.untested_error_handler import app as error_handler


HTML_ELEMENTS_TO_REPLACE = [
  'flowchart_data',
  'js_content', 
]

HTML_PATH = __file__.replace('.py', '.html')
JS_PATH = __file__.replace('.py', '.js')


@dataclass
class Data:
  ping_url: str = 'https://google.com'
  flowchart_data: str | None = 'flowchart_data'
  html_path: str | None = field(default_factory=lambda: HTML_PATH)
  js_path: str | None = field(default_factory=lambda: JS_PATH)
  html_content: str | None = None
  js_content: str | None = None
  html_elements_to_replace: list = field(
    default_factory=lambda: HTML_ELEMENTS_TO_REPLACE)
  svg_content: str | None = None


# @error_handler.main
def check_network_connection_active(ping_url) -> None:
  '''An active internet connection is needed to render html/javascript
  in the functions below. This function a pings a URL to verify the network 
  connection is active, or raises an error if it is inactive.'''

  response = requests.get(ping_url)
  if response.status_code == 200:
    return
  message = ''
  raise RuntimeError(message)


# @error_handler.main
def get_data_from_file_path(file_path: str, content: str | None) -> str | None:
  '''Returns data from a file given the file's path'''
  if content is not None:
    return content
  with open(file_path, 'r') as file:
    return file.read()


# @error_handler.main
def replace_elements_in_html_content(data: Data) -> str:
  '''Replaces strings within a HTML file with elements (flowchart data, 
  javascript code, etc.)'''
  for element in data.html_elements_to_replace:
    value = getattr(data, element)
    match_string = '{{element|safe}}'.replace('element', element)
    data.html_content = data.html_content.replace(match_string, value)
  return data.html_content


# @error_handler.main
def render_html_content(html_content: str) -> str:
  '''Renders a HTML template and return the HTML'''
  html = requests_html.HTML(html=html_content)
  html.render(retries=2, sleep=2, timeout=15)
  return html.html


# @error_handler.main
def get_svg_content_from_html(html_content: str | None) -> None:
  '''Returns the contents within with SVG tag of the HTML'''
  svg_content = None
  start = html_content.find('<svg')
  end = html_content.find('</svg>') + len('</svg>')
  svg_content = html_content[start:end]
  return svg_content


# @error_handler.main
def main(data: Data | dict) -> str:
  '''An orchestration function used to execute the other functions in this 
  module'''
  check_network_connection_active(ping_url=data.ping_url)
  data.js_content = get_data_from_file_path(
    file_path=data.js_path,
    content=data.js_content,
  )
  data.html_content = get_data_from_file_path(
    file_path=data.html_path,
    content=data.html_content,
  )
  data.html_content = replace_elements_in_html_content(data=data)
  data.html_content = render_html_content(html_content=data.html_content)
  data.svg_content = get_svg_content_from_html(html_content=data.html_content)
  return data.svg_content


def example() -> None:
  data = Data(
    flowchart_data='''
      st0=>start: start a_pyflow_test:>https://google.com
      op1=>operation: do something
      cond2=>condition: Yes or No?
      io3=>inputoutput: output: something...
      sub4=>subroutine: A Subroutine
      e5=>end: end a_pyflow_test


      st0->op1
      op1->cond2
      cond2(yes,)->io3
      cond2(no,)->sub4
      io3->e5
      sub4(right)->op1
    '''
  )
  data = main(data=data)
  print(data)
  

if __name__ == '__main__':
  example()



# @dataclass
# class Data:
#   ping_url: str = 'https://google.com'
#   html_path: str | None = None
#   flowchart_data: str | None = 'flowchart_data'
#   js_script_path: str | None = field(default_factory=lambda: JS_SCRIPT_PATH)
#   js_script: str | None = None
#   source_code: str | None = None
#   html: str | None = None
#   get_svg_element: str | None = None
#   html_elements_to_replace: dict = field(
#     default_factory=lambda: HTML_ELEMENTS_TO_REPLACE)


# @error_handler.main
# def check_network_connection_active(data: Data) -> Data:
#   response = requests.get(data.ping_url)
#   if response.status_code == 200:
#     return data
#   message = ''
#   raise RuntimeError(message)


# @error_handler.main
# def set_html_path(data: Data) -> Data:
#   if data.html_path is not None or data.source_code is not None:
#     return data
#   data.html_path = __file__.replace('.py', '.html')
#   return data


# @error_handler.main
# def get_html_from_path(data: Data) -> Data:
#   if data.source_code is not None:
#   with open(data.html_path, 'r') as file:
#     data.source_code = file.read()
#     return data


# @error_handler.main
# def get_js_from_path(data: Data) -> Data:
#   if data.js_script is not None:
#     return data
#   with open(data.js_script_path, 'r') as file:
#     data.js_script = file.read()
#     return data


# @error_handler.main
# def replace_elements_in_html(data: Data) -> Data:
#   for key, value in data.html_elements_to_replace.items():
    
#     attribute_value = getattr(data, value)
#     print(key, value, attribute_value)
#     data.source_code = data.source_code.replace(key, attribute_value)
#   return data


# @error_handler.main
# def set_rendered_html(data: Data) -> Data:
#   html = requests_html.HTML(html=data.source_code)
#   html.render(retries=2, sleep=2, timeout=15)
#   data.html = html.html
#   return data


# @error_handler.main
# def main(data: Data | dict) -> str:
#   data = check_network_connection_active(data=data)
#   data = set_html_path(data=data)
#   data = get_html_from_path(data=data)
#   data = replace_elements_in_html(data=data)
#   data = set_rendered_html(data=data)
#   return data.html


# def example() -> None:
#   data = Data(
#     flowchart_data='''
#       st0=>start: start a_pyflow_test:>https://google.com
#       op1=>operation: do something
#       cond2=>condition: Yes or No?
#       io3=>inputoutput: output: something...
#       sub4=>subroutine: A Subroutine
#       e5=>end: end a_pyflow_test


#       st0->op1
#       op1->cond2
#       cond2(yes,)->io3
#       cond2(no,)->sub4
#       io3->e5
#       sub4(right)->op1
#     '''
#   )
#   data = main(data=data)
#   print(data)


# if __name__ == '__main__':
#   example()



# # from requests_html import HTML


# # file_path = '/home/femij/mono_repo/coding_challenges/utils/untested_create_flowchart/index.html'
# # with open(file_path) as file:
# #   source_code = file.read()
# #   parsed_html = HTML(html=source_code)
# #   parsed_html.render(retries=2, sleep=1)
  
# #   print(dir(parsed_html), parsed_html.html)
# #   parsed_html.browser