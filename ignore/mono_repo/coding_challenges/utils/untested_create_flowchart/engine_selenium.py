# https://stackoverflow.com/questions/1555234/fill-form-values-in-a-web-page-via-a-python-script-not-testing
# https://stackoverflow.com/questions/66549097/how-to-interact-with-ace-editor-using-selenium-webdriver


from __future__ import annotations
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import inspect
from dataclasses import dataclass, field
from typing import Dict, List, Any



WEB_DRIVER_OPTIONS = dict(
  headless=True,
)


@dataclass
class Element:
  by: str = None
  name: str = None


EDITOR_ELEMENTS = [
  Element(by='class name', name='editor-wrapper'),
  Element(by='css selector', name='.ace_text-input'),
]


SEND_KEYS = [
  ['\ue009', 'a'],
  ['\ue003'],
  [inspect.cleandoc('''
    st=>start: Start:>http://www.google.com[blank]
    e=>end:>http://www.google.com
    op1=>operation: My Operation
    sub1=>subroutine: My Subroutine
    cond=>condition: Yes
    or No?:>http://www.google.com
    io=>inputoutput: catch something...
    para=>parallel: parallel tasks

    st->op1->cond
    cond(yes)->io->e
    cond(no)->para
    para(path1, bottom)->sub1(right)->op1
    para(path2, top)->op1
  ''')
  ],
]

SVG_ATTRIBUTES = dict(
  width='500px',
  height='600px',
  x='50%',
  y='50%',
)

SVG_PARENT_ELEMENT_XPATH = ['xpath', ".//*[@class='diagram diagram1']"]


@dataclass
class Data:
  browser: str = 'Firefox'
  web_driver_options: Dict[str, Any] | 'Options' = field(
    default_factory=lambda: WEB_DRIVER_OPTIONS)
  url: str = 'https://flowchart.js.org/'
  editor_elements: List[Elements] = field(
    default_factory=lambda: EDITOR_ELEMENTS)
  flowchart_txt_path: str = 'data/flowchart.txt'
  send_keys: List[List[Any]] = field(
    default_factory=lambda: SEND_KEYS)
  png_path: str = 'data/flowchart.png'
  svg_attributes: Dict[str, str] = field(
    default_factory=lambda: SVG_ATTRIBUTES)
  svg_html: str | None = None
  html_path: str = 'data/flowchart.html'
  svg_saved_as_png: bool = False
  svg_parent_element_xpath: List[str] = field(
    default_factory=lambda: SVG_PARENT_ELEMENT_XPATH)
  svg_saved_as_html: bool = False
  web_driver: 'WebDriver' = None


def get_web_driver_options(
  web_driver: 'WebDriver', 
  options: Dict[str, Any],
  browser: str,
) -> 'Options':
  '''Returns options for a webdriver'''
  browser = browser.lower()
  web_driver = getattr(webdriver, browser)
  web_driver_options = web_driver.options.Options()
  for key, value in options.items():
    setattr(web_driver_options, key, value)
  return web_driver_options


def get_driver(browser: str, options: 'Options') -> 'WebDriver':
  '''Returns a selenium webdriver with options set'''
  return webdriver.Firefox(options=options, keep_alive=False)


def get_editor_element(
  driver: 'WebDriver', 
  editor_elements: List[Dict[str, str]],
) -> 'WebElement':
  parent_element = driver
  for element in editor_elements:
    parent_element = parent_element.find_element(
      element.by, 
      element.name,
    )
  return parent_element


def send_keys_to_editor_element(
  driver: 'WebDriver', 
  element: 'WebElement',
  send_keys: List[List[str | Any]],
) -> bool:
  for _keys in send_keys:
    element.send_keys(*_keys)
  return True


def get_svg_element(driver: 'WebDriver') -> 'WebElement':
  attribute = dict(by='tag name', name='svg')
  values = attribute.values()
  element = driver.find_element(*values)
  return element


def set_svg_attributes(
  driver: 'WebDriver', 
  element: 'WebElement',
  attributes: Dict[str, Any],
) -> 'WebElement':
  ''''''
  for key, value in attributes.items():
    driver.execute_script(
      f'arguments[0].setAttribute("{key}", arguments[1])',
      element, 
      value,
    )
  return driver


def save_svg_as_png(
  element: 'WebElement', 
  png_path: str,
) -> bool | None:
  '''Saves a SVG image to file and returns True if successful'''
  if element.tag_name != 'svg':
    message = 'WebElement must be a SVG element.'
    raise RuntimeError(message)
  element.screenshot(png_path)
  return True


def get_svg_html(
  driver: 'WebDriver',
  element_xpath: List[str],
  html_path: str,
) -> str:
  element = driver.find_element(*element_xpath)
  return element.get_attribute('innerHTML')


def save_svg_as_html(
  html: str,
  html_path: str,
) -> str:
  with open(html_path, 'w+') as file:
    file.write(html)
  return True


def tear_down_driver(driver: 'WebDriver') -> None:
  if driver is None:
    return
  driver.quit()
    

def main(data: Data) -> Any:
  web_driver_options = get_web_driver_options(
    web_driver=data.web_driver, 
    options=data.web_driver_options,
    browser=data.browser,
  )
  driver = get_driver(
    browser=data.browser, 
    options=web_driver_options,
  )
  driver.get(data.url)

  editor_element = get_editor_element(
    driver=driver, 
    editor_elements=data.editor_elements,
  )
  keys_sent = send_keys_to_editor_element(
    driver=driver,
    element=editor_element,
    send_keys=data.send_keys,
  )
  if keys_sent != True:
    tear_down_driver(driver=driver)
    message = 'An ace editor element could not be found.'
    raise RuntimeError(message)

  svg_element = get_svg_element(driver=driver)
  if svg_element is None:
    message = 'A SVG element could not be found'
    raise RuntimeError(message)
  svg_attributes_set = set_svg_attributes(
    element=svg_element,
    attributes=data.svg_attributes,
    driver=driver,
  )
  data.svg_saved_as_png = save_svg_as_png(
    element=svg_element,
    png_path=data.png_path,
  )
  data.svg_html = get_svg_html(
    driver=driver,
    element_xpath=data.svg_parent_element_xpath,
    html_path=data.html_path,
  )
  data.svg_saved_as_html = save_svg_as_html(
    html=data.svg_html,
    html_path=data.html_path,
  )

  tear_down_driver(driver=driver)
  return data.svg_saved_as_html


def example() -> None:
  data = Data()
  data = main(data=data)
  print(data)


if __name__ == '__main__':
  example()



