#!/usr/bin/env python

from xml.dom import minidom
import os
import urllib2

class Config:
  """
  configuration container and access class
  """
  def __init__(self, configfilename):
    """
    constructor
    """
    # TODO: find out what can happen when file does not exist,
    # TODO: when file is wrong-formatted
    fd = open(configfilename, "r");
    self.username = fd.read().strip()
    fd.close();

  def getUsername(self):
    """
    data read access method
    """
    return self.username

class Connector:
  """
  a network connector and retriever class

  the connection is trying to be established and information retrieved upon
  object creation
  """
  def __init__(self, uri):
    """
    constructor
    """
    self.uri = uri

  def getData(self):
    """
    connects with given URI and returns data

    each time it is being called it will reconnect
    """
    # TODO: expect things like url cannot be opened
    return urllib2.urlopen(urllib2.Request(self.uri)).read()

def extractText(source):
  """
  returns status text from status.net XML response

  source should be well-formed XML status.net response
  """
  # TODO: handle parse errors
  wholexml = minidom.parseString(source)
  # TODO: handle absense of XML tags
  statuses = wholexml.getElementsByTagName('statuses')[0]
  # TODO: handle absense of any text entries in user's microblog
  laststatus = statuses.getElementsByTagName('status')[0]
  textelemnt = laststatus.getElementsByTagName('text')[0]
  text = textelemnt.firstChild.data

  return text

if __name__ == "__main__":
  config = Config(os.path.expanduser("~/.stampp"))
  uri = "https://identi.ca/api/statuses/user_timeline/" +\
      config.getUsername() + ".xml?count=1"
  connector = Connector(uri)

  extractText(connector.getData())
