#!/usr/bin/env python

from xml.dom import minidom
import ConfigParser
import io
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
    default_settings = """
[core]
update_period_sec: 30
respect_xmpp_status: true

[statusnet]
username: evan
uri_prefix: https://identi.ca/api/statuses/user_timeline/
uri_postfix: .xml?count=1

[xmpp]
change_status_if_online: true
"""
    # TODO: handle absence of config file and/or wrong formatting
    self.cp = ConfigParser.SafeConfigParser()
    self.cp.readfp(io.BytesIO(default_settings))
    self.cp.read(configfilename)
    self.username = self.cp.get('statusnet', 'username').strip()
    self.uriPrefix = self.cp.get('statusnet', 'uri_prefix').strip()
    self.uriPostfix = self.cp.get('statusnet', 'uri_postfix').strip()
    self.updatePeriod = float(self.cp.get('core', 'update_period_sec').strip())

    if self.cp.get('xmpp', 'change_status_if_online') == "true":
      self.ifOnline = True
    else:
      self.ifOnline = False

    # see self.getXmppStatusRespect() description
    if self.cp.get('core', 'respect_xmpp_status').strip() == "true":
      self.respectXmpp = True
    else:
      self.respectXmpp = False

    # write config
    with open(configfilename, 'wb') as fd:
      self.cp.write(fd)

  def getUsername(self):
    """
    data read access method
    """
    return self.username

  def getUriPrefix(self):
    """
    returns base URI prefix
    """
    return self.uriPrefix

  def getUriPostfix(self):
    """
    returns base URI postfix
    """
    return self.uriPostfix

  def getUpdatePeriod(self):
    """
    returns update period in seconds
    """
    return self.updatePeriod

  def getChangeIfOnline(self):
    """
    returns true if status should be changed only if XMPP status is set to
    'online'
    """
    return self.ifOnline

  def getXmppStatusRespect(self):
    """
    returns False if XMPP status set by user should should be overriden
    returns True if XMPP status set by user should not be overriden unless there
    is a newer status from statusnet
    """
    return self.respectXmpp

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

class StatusnetClient:
  """
  status.net instance client class
  """
  def __init__(self, uri):
    """
    class constructor

    uri should be a URI to user's timeline in API XML, e.g.
    https://identi.ca/api/statuses/user_timeline/evan

    """
    self.connector = Connector(uri)

  def getLastStatus(self):
    """
    returns last status from user's timeline
    """

    # TODO: handle parse errors
    wholexml = minidom.parseString(self.connector.getData())
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

def changeXmppStatus(statusnetStatus, xmppStatusMsg, xmppClient):
  """
  as it says, it changes XMPP client status
  """
  if snetStatusMsg != xmppStatusMsg:
    # XMPP status changes only if it differs from status.net
    xmppClient.setStatusMsg(snetStatusMsg)
  else:
    pass

if __name__ == "__main__":
  config = Config(os.path.expanduser("~/.stampp"))
  uri = config.getUriPrefix() +\
      config.getUsername() + config.getUriPostfix()
  snetClient = StatusnetClient(uri)

  xmppClient = XMPPClient("gajim")

  # previous status.net status message is stored here
  prevSnetMsg = snetClient.getLastStatus()
  # previous XMPP status message is stored here
  prevXmppMsg = xmppClient.getStatusMsg()
  while True:
    xmppStatusMsg = xmppClient.getStatusMsg()

    # XMPP status changes if user is online or by setting from config
    if ((config.getChangeIfOnline() == True) and\
        (xmppClient.getStatus() == "online")) or\
        (config.getChangeIfOnline() == False):
      snetStatusMsg = snetClient.getLastStatus()
      if snetStatusMsg == prevSnetMsg:
        if config.getXmppStatusRespect() == False:
          changeXmppStatus(snetStatusMsg, xmppStatusMsg, xmppClient)
        else:
          pass
        # if status.net status message has not changed, do nothing
      else:
        # status.net status message has changed
        prevSnetMsg = snetStatusMsg

        if xmppStatusMsg == prevXmppMsg:
          # if XMPP status has not changed by the user, it does not affect
          # anything
          changeXmppStatus(snetStatusMsg, xmppStatusMsg, xmppClient)
          xmppStatusMsg = xmppClient.getStatusMsg()
          prevXmppMsg = xmppStatusMsg
        else:
          # assume that XMPP status message has changed by the user
          prevXmppMsg = xmppStatusMsg
          if config.getXmppStatusRespect() == True:
            # respect user XMPP status message, thus not changing it
            pass
          else:
            # don't respect user changing XMPP status message, change it to
            # coinside w/ status.net
            changeXmppStatus(snetStatusMsg, xmppStatusMsg, xmppClient)
            xmppStatusMsg = xmppClient.getStatusMsg()
            prevXmppMsg = xmppStatusMsg
    else:
      pass
    time.sleep(config.getUpdatePeriod())
