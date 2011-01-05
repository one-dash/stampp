#!/usr/bin/env python

from xml.dom import minidom
import os
import subprocess
import time
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

class GajimClient:
  """
  class for a gajim type client
  """
  def __init__(self):
    """
    constructor
    """
    # TODO: chech if such client really exists
    self.binName = "gajim-remote"

  def getStatus(self):
    """
    return gajim status
    """
    # TODO: chech return code, generate exceptions
    return os.popen(self.binName + " get_status").read().strip()

  def getStatusMsg(self):
    """
    return gajim status message
    """
    # TODO: chech return code, generate exceptions
    return os.popen(self.binName + " get_status_message").read().strip()

  def setStatusMsg(self, newMsg):
    """
    set gajim's new status message
    """
    # TODO: handle exit code
    subprocess.call([self.binName, "change_status", self.getStatus(), newMsg])

class XMPPClient:
  """
  XMPP client class
  """
  def __init__(self, clientType):
    """
    constructor

    client type is a string determining type of a client w/ a name
    """

    if clientType == "gajim":
      self.clientBackend = GajimClient()
    else:
      pass
      # TODO: write other clients backends!

  def getStatus(self):
    """
    returns client status
    """
    return self.clientBackend.getStatus()

  def getStatusMsg(self):
    """
    return client status message
    """
    return self.clientBackend.getStatusMsg()

  def setStatusMsg(self, newMsg):
    """
    set Jabber/XMPP status method
    """
    self.clientBackend.setStatusMsg(newMsg)

if __name__ == "__main__":
  config = Config(os.path.expanduser("~/.stampp"))
  uri = "https://identi.ca/api/statuses/user_timeline/" +\
      config.getUsername() + ".xml?count=1"
  connector = Connector(uri)

  xmppClient = XMPPClient("gajim")

  while True:
    xmppStatusMsg = xmppClient.getStatusMsg()
    # TODO: the following check should be configurable
    if xmppClient.getStatus() == "online":
      snetStatusMsg = extractText(connector.getData())
      if snetStatusMsg != xmppStatusMsg:
        # XMPP status changes only if it differs from status.net
        xmppClient.setStatusMsg(snetStatusMsg)
      else:
        pass
    else:
      pass
    # TODO: make sleep time configurable
    time.sleep(30)
