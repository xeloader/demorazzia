import sys
import time
import requests
import re
import math

from bs4 import BeautifulSoup
from pathlib import Path

from CONFIG import *
from TOOLS import *

# Transform html into beautifulSoup instance
def BS(htmlString):
  return BeautifulSoup(htmlString, "html.parser")

# Join a path and a base URL to create fully qualified url
def joinFullUrl(path, baseUrl = URL):
  return "%s%s" % (baseUrl, path)

# Get the url for a certain motion page
def getMotionUrlForPage(page = 1):
    motionArgs = "&p=%s" % (page)
    return joinFullUrl(motionArgs, URL_MOTION)

# Parse the number of hits and convert to an int from the represented string
def parseNumberOfHits(hitsString):
  craps = ["träffar", "(", ")", u"\xa0"]
  for crap in craps:
    hitsString = hitsString.replace(crap, "")
  hitsString = hitsString.strip()
  return int(hitsString)

# Get html string for a certain motion page
def getMotionPageHtml(page):
  pageUrl = getMotionUrlForPage(page)
  resp = requests.get(pageUrl)
  if resp.ok:
    printX("Fetched page %s" % page)
    return resp.text
  else:
    printX("Request of page %s failed" % page, "err")
    exit()

# Fetch the first page of the motion website
def getFirstPageHtml():
  return getMotionPageHtml(1)

# Get number of search hits from a string of html
def getNumberOfMotionerFromHtml(htmlString):    
    firstPage = BS(htmlString)
    hitsString = firstPage.find(class_="font-normal").text
    return parseNumberOfHits(hitsString)

# Get number of motioner from website
def getNumberOfMotioner():
  return getNumberOfMotionerFromHtml(getFirstPageHtml());

# Get number of pages that contains motions from website
def getNumberOfMotionPages():
  MOTIONS_PER_PAGE = 20
  return math.ceil((getNumberOfMotioner() / MOTIONS_PER_PAGE))

def parseListItemSubHeaderFromText(subHeaderText):
  START = 'Motion'
  END = 'av'
  motionId = subHeaderText
  res = re.search('%s(.*)%s' % (START, END), subHeaderText)
  if res is not None:
    motionId = res.group(0)
  motionId = replaceAll(["motion", "av", " "], "", motionId).strip()
  return {
    "motionId": motionId
  }

# Parse relevant data from motion list item
def parseMotionDataFromListItem(listItem):
  header = listItem.header
  subHeader = listItem.find(class_="normal font-bold")
  motionId = parseListItemSubHeaderFromText(subHeader.text)["motionId"]
  motionId = renameMotionId(motionId)
  return {
    "url": joinFullUrl(header.a['href']),
    "title": header.a.string,
    "motionId": motionId
  }

# rename motionId to os-friendly filename
def renameMotionId(motionId):
  motionId = re.sub("\D", "", motionId)
  motionId = replaceAll(["/", ":"], "", motionId)
  return motionId

# Parse every motionId from a list of motions and reformat it
def parseMotionsFromHtml(htmlString):
  motionPage = BS(htmlString)
  motionList = motionPage.findAll(class_="content-list")

  motions = []
  for listItem in motionList:
    motionData = parseMotionDataFromListItem(listItem)
    motions.append(motionData)

  return motions

# Get the file path for a certain motion
def getMotionPath(motionData):
  return "%s/m%s.html" % (DIR_MOTIONS, motionData["motionId"])

def motionExistsLocally(motionData):
  motionId = motionData["motionId"]
  motionFile = Path(getMotionPath(motionData))
  return motionFile.is_file()

# List
# 1. Fetch number of pages
# 1.1 Get motionIds for each page
# 2. Download each motion for each page

def fetchMotionFromWeb(motionData):
  url = motionData["url"]
  motionId = motionData["motionId"]
  resp = requests.get(url)
  if resp.ok:
    printX("Fetched motion %s from web" % motionId)
    return resp.text
  else:
    printX("Request of motion %s failed" % motionId, "err")
    exit()
  
def storeMotionHtml(motionData, motionHtml):
  motionId = motionData["motionId"]
  motionPath = getMotionPath(motionData)
  f = open(motionPath, 'w+')
  f.write(motionHtml)
  f.close();