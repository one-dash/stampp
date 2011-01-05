#!/usr/bin/env python

import os

class Config:
  """
  configuration container class
  """
  def __init__(self, configfilename):
    """
    constructor
    """
    fd = open(configfilename, "r");
    self.username = fd.read().strip()
    fd.close();
  def getUsername(self):
    """
    data read access method
    """
    return self.username

if __name__ == "__main__":
  config = Config(os.path.expanduser("~/.stampp"))
