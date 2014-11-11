#!/usr/bin/env python3

import base64

def chop(thestring, beginning):
  if thestring.startswith(beginning):
    return thestring[len(beginning):]
  return thestring

def rchop(thestring, ending):
  if thestring.endswith(ending):
    return thestring[:-len(ending)]
  return thestring

def htmlToBase64(html):
    return "data:text/html;charset=utf-8;base64," + base64.b64encode((html.replace('\n', '')).encode('utf-8')).decode('utf-8')

def cssToBase64(css):
    return "data:text/css;charset=utf-8;base64," + base64.b64encode((css.replace('\n', '')).encode('utf-8')).decode('utf-8')
