from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join

import MySQLdb as mysql
import re

from CONFIG import URL, DIR_MOTIONS, SQL_CONFIG as conf
from TOOLS import printX

import pprint
pp = pprint.PrettyPrinter(indent=4)

T_M_NOT_EXISTS = {
  "motionId": "poop",
}

T_M_EXISTS = {
  "motionId": "Motion 2016/17:3753"
}

c = mysql.connect(
  host=conf["host"],
  database=conf["database"],
  port=conf["port"],
  user=conf["user"],
  password=conf["password"]
)

cur = c.cursor()

# Check if a motion is already added by its motionId
def motionExists(motionData):
  motionId = motionData["motionId"]
  query = "SELECT id FROM propositions WHERE motion_id = %s"
  cur.execute(query, [motionId])
  motion = cur.fetchone()
  return motion is not None

# Extract date and name from a concatenated event string
def extractEventData(eventString):
  eventData = eventString.lower().split(":", 1)
  if(len(eventData) > 1):
    return {
      "key": eventData[0].strip(),
      "value": eventData[1].strip()
    }
  else:
    return None

# Extract party and name from a concatenated politician string
def extractPoliticianData(politicianString):
  name = re.sub(r'\([^)]*\)', '', politicianString)
  party = re.findall('\((.*?)\)', politicianString)
  if (len(party) > 0):
    party = party[0].upper().strip()
    name = name.strip();
    return {
      "name": name,
      "party": party
    }
  else:
    return None

def extractIdFrom(string):
  return string.replace("Motion", "").strip()

# Get all the motions from the local file system
def getMotionFiles():
  files = []
  for f in listdir(DIR_MOTIONS):
    fullPath = join(DIR_MOTIONS, f)
    if isfile(fullPath) and f.endswith(".html"):
      files.append(fullPath)
  return files

# get motion header from website
def _getHeader(html):
  return html.find(class_="top-type-one")

def _getInfo(html):
  return html.find(class_="component-document-activity")

# get the politician container in html
def _getPoliticians(html):
  return html.findAll(class_="fellow-item-container") # alla personer som skickade in motionen.

# get all politicians from html
def getPoliticians(html):
  politicians = []
  containers = _getPoliticians(html)
  for container in containers:
    title = container.find(class_="fellow-name").text
    p = {}
    p["name"] = re.sub(r'\([^)]*\)', '', title).strip()
    p["imageUrl"] = container.img['src']
    p["url"] = "%s%s" % (URL, container['href'])
    p["party"] = re.findall('\((.*?)\)', title)[0].upper().strip() # extract party from name
    politicians.append(p)
  return politicians

# get information fields
def getEvents(html):
  info = _getInfo(html)
  if info is not None:
    htmlInfos = info.findAll(class_="medium-smaller")
    return list(map(lambda html: extractEventData(html.text), htmlInfos))

# get the title of a motion
def getTitle(html):
  header = _getHeader(html)
  if header is not None:
    string = header.find(class_='biggest').text
    return string.strip()

# get the id from motion
def getMotionId(html):
  header = _getHeader(html)
  if header is not None:
    string = header.find(class_='big').text
    return extractIdFrom(string)

def getPdf(html):
  pdfHtml = html.find(class_="link-file file-type-pdf")
  if pdfHtml is not None:
    return pdfHtml['href']
  else:
    return None

def getURL(html):
  return "%s%s" % (URL, html.find(class_="aspnetForm")['action'])

# get event with key from a list with events
def getKeyFromEvents(key, events):
  for event in events:
    if event is not None:
      eventName = event["key"].lower()
      if eventName == key.lower():
        return event["value"]

def getHtmlFromFile(file):
  motionFile = open(file, 'r').read()
  return BeautifulSoup(motionFile, "html.parser")

def getBodyFrom(html):
  bodyHtml = html.find(class_="Section1")
  if bodyHtml is not None:
    return bodyHtml.getText().strip()

def getYrkandenFrom(html):
  yrkandenHtml = html.find(id="item0")
  if yrkandenHtml is not None:
    return yrkandenHtml.getText().strip()

def fetchPartyBySymbol(symbol):
  cur.execute("SELECT id FROM parties WHERE symbol = %s", [symbol])
  partyData = cur.fetchone();
  if partyData is not None:
    return partyData[0] # return party id

def storeParty(symbol):
  query = ("INSERT INTO parties "
            "(symbol) "
            "VALUES "
            "(%s)")
  cur.execute(query, [symbol])
  return cur.lastrowid # return new party id

def fetchPersonByName(name):
  query = "SELECT id, name FROM politicians WHERE name = %s"
  cur.execute(query, [name])
  p = cur.fetchone()
  if p is not None:
    return p[0] # return person id

def storePerson(person):
  query = ("INSERT INTO politicians"
            "(party_id, name, picture_url, url)"
            "VALUES"
            "(%s, %s, %s, %s)")
  partyId = fetchPartyBySymbol(person["party"])
  cur.execute(query, [partyId, person["name"], person['imageUrl'], person['url']])
  return cur.lastrowid # return new person id

def storeSenderRelation(personId, motionId):
  query = "INSERT INTO proposition_senders (proposition_id, politician_id) VALUES (%s, %s)";
  cur.execute(query, [motionId, personId])
  return cur.lastrowid # return new relation id

def fetchSenderRelation(personId, motionId):
  query = "SELECT id FROM proposition_senders WHERE politician_id = %s AND proposition_id = %s"
  cur.execute(query, [personId, motionId])
  rel = cur.fetchone()
  if rel is not None:
    return rel[0]


def fetchMotionById(motionId):
  query = "SELECT id FROM propositions WHERE motion_id = %s"
  cur.execute(query, [motionId])
  m = cur.fetchone()
  if m is not None:
    return m[0]

# store a row in the persistent storage of motions and only that motion. No relations.
def _storeMotion(motion):
  m = motion
  cur.execute("INSERT INTO propositions "
              "(type, body, title, motion_id, url, pdf_url, dedicated_to, yrkanden, added, category) "
              "VALUES "
              "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
              (m["category"], m["body"], m["title"], m["motionId"], m["url"], m["pdf"], m["assigned"], m["statements"], m["added"], m["category"]))
  return cur.lastrowid # return new motion id

def storeMotion(motion):

  m = motion
  newStores = {
    "motionId": None,
    "partyIds": [],
    "personIds": [],
    "relationIds": []
  }
  # indicate if a new motion was added or not

  motionId = fetchMotionById(m["motionId"])
  if motionId is None:
    motionId = _storeMotion(motion)
    newStores["motionId"] = motionId

  for p in m["politicians"]:
    party = p["party"]
    name = p["name"]
    partyId = fetchPartyBySymbol(party)
    personId = fetchPersonByName(name)
    relId = None

    if partyId is not None and personId is not None:
      relId = fetchSenderRelation(personId, motionId)

    if partyId is None: # check if party exists
      partyId = storeParty(party)
      newStores["partyIds"].append(str(partyId))

    if personId is None: # check if person exists
      personId = storePerson(p)
      newStores["personIds"].append(str(personId))

    if relId is None: # check if relation between person and motion exists
      relId = storeSenderRelation(personId, motionId) # store relation between person and motion
      newStores["relationIds"].append(str(relId))
    
  c.commit()
  return newStores