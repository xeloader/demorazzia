import sys
import time
import requests
import re
import math

from bs4 import BeautifulSoup
from pathlib import Path

URL = "https://www.riksdagen.se"
URL_MOTION = "%s/sv/dokument-lagar/?doktyp=mot" % (URL) # &p=$i
MOTIONS_PER_PAGE = 20

DIR_MOTIONS = "./motioner"

# Transform html into beautifulSoup instance
def BS(htmlString):
  return BeautifulSoup(htmlString, "html.parser")

# Custom printing method for messages
def printX(msg, status = "i"):
  status = status.lower()
  print("[%s] %s" % (status, msg))

# Replace every occurence of olds with new in a string
def replaceAll(olds, new, string):
  string = string.lower()
  for old in olds:
    old = old.lower()
    string = string.replace(old, new)
  return string

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

startPage = 1
endPage = None

argLen = len(sys.argv)
if (argLen >= 2):
  startPage = int(sys.argv[1])

if(argLen >= 3):
  endPage = startPage + int(sys.argv[2])
else:
  printX("Fetching number of pages...")
  endPage = getNumberOfMotionPages()

totalPages = endPage - startPage

motionsFetched = 0

for p in range(startPage, endPage + 1):

  percentage = ((p - startPage) / totalPages) * 100
  printX("Fetching page {} of {}...".format(p, endPage), "{0:.2f}%".format(percentage))
  
  pageHtml = getMotionPageHtml(p) # current page html
  motions = parseMotionsFromHtml(pageHtml) # motions in the current page

  for motion in motions:
    motionId = motion["motionId"]
    if not motionExistsLocally(motion): # download motion from url
      printX("Motion %s does not exist, fetching from web..." % (motionId))
      motionHtml = fetchMotionFromWeb(motion)
      storeMotionHtml(motion, motionHtml)
      motionsFetched += 1
    else: # the motion already exists, next
      continue

printX("Done, fetched %s new motions." % (motionsFetched))