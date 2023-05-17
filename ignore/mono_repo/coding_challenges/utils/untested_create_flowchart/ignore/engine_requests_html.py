from requests_html import HTML

html = HTML(html="<a href='http://www.example.com/'>")

script = """
function escramble_758(){
  var a,b,c
  a='+1 '
  b='84-'
  a+='425-'
  b+='7450'
  c='9'
  return a+c+b;
}
"""

val = html.render(script=script, reload=False)
print(val)


# from requests_html import HTMLSession
# session = HTMLSession()

# url = '///home/femij/mono_repo/coding_challenges/utils/create_flowchart/ignore/index.html'
# r = session.get(url)

import json
import re
import urllib

text = urllib.open('http://dcsd.nutrislice.com/menu/meadow-view/lunch/').read()
print(text)