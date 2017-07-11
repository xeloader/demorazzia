from bs4 import BeautifulSoup
import requests
import MySQLdb as mysql
import re
import pprint

url = "https://www.riksdagen.se"
pp = pprint.PrettyPrinter(indent=4)

con = mysql.connect(
  host='127.0.0.1',
  database='demorazzia',
  port=8889,
  user='***REMOVED***',
  password='***REMOVED***')

cur = con.cursor();

PAGES = 512
MOTIONS_PER_PAGE = 20
START_AT = 189

# Check if a proposition is already added by its motionId
def propExists(motionId):
  query = "SELECT id FROM propositions WHERE motion_id = %s";
  cur.execute(query, [motionId])
  motion = cur.fetchone()
  return motion is not None

# Extract date and name from a concatenated event string
def extractEventData(eventString):
  eventData = eventString.split(":", 1)
  return {
    "date": eventData[1],
    "name": eventData[0]
  }

# Extract party and name from a concatenated politician string
def extractPoliticianData(politicianString):
  name = re.sub(r'\([^)]*\)', '', politicianString).strip()
  party = re.findall('\((.*?)\)', politicianString)
  if (len(party) > 0):
    party = party[0].upper().strip()
  return {
    "name": name,
    "party": party
  }

def joinFullUrl(path):
  return "%s%s" % (url, path)

for i in range(START_AT, PAGES + 1):
  for j in range(0, MOTIONS_PER_PAGE):
    print("[parsing p%d-m%d]" % (i, j))
    motion = open('./motioner/p%s-m%s.html' % (i, j), 'r').read()

    html = BeautifulSoup(motion, "html.parser")
    header = html.find(class_="top-type-one")
    info = html.find(class_="component-document-activity")

    title = header.find(class_='biggest').text
    motion_id = header.find(class_="big").text
    senders = header.find(class_="medium-smaller").text

    infos = info.findAll(class_="medium-smaller")
    
    handelser = []
    motionCategory = None
    dedicatedTo = None

    for idx in range(0, len(infos)):
      info = infos[idx].get_text()
      if "motionskategori" in info.lower():
        motionCategory = info
      elif "tilldelat" in info.lower():
        dedicatedTo = info
      else:
        handelser.append(info.lower())

    for event in handelser:
      print(extractEventData(event))
      # print(event)

    motion_url = "%s%s" % (url, html.find(class_="aspnetForm")['action'])
    pdf_url = html.find(class_="link-file file-type-pdf")
    if pdf_url is not None:
      pdf_url = pdf_url['href']
    bodyHtml = html.find(class_="Section1")
    body = None
    if bodyHtml is not None:
      body = bodyHtml.getText().strip()

    yrkandenHtml = html.find(id="item0")
    yrkanden = None
    if yrkandenHtml is not None:
      yrkandenHtml = yrkandenHtml.getText().strip()


    politicians = []
    phtmls = html.findAll(class_="fellow-item-container") # personer som skickade in motionen.
    for phtml in phtmls:
      fullName = phtml.find(class_="fellow-name").text

      poliName = re.sub(r'\([^)]*\)', '', fullName).strip()
      poli = {
        "picture_url": phtml.img['src'],
        "url": "%s%s" % (url, phtml['href']),
        "name": poliName
      }
      poli['party'] = re.findall('\((.*?)\)', fullName)[0].upper() # extract party from name
      politicians.append(poli)

    exit();

    cur.execute("INSERT INTO propositions "
                "(type, body, title, motion_id, url, pdf_url, dedicated_to, yrkanden, sender) "
                "VALUES "
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                (motionCategory, body, title, motion_id, motion_url, pdf_url, dedicatedTo, yrkanden, senders))
    propId = cur.lastrowid
    print("Added prop with id %d" % propId)

    for politician in politicians:
      personName = politician['name']
      personParty = politician['party']
      partyId = None
      personId = None

      # Check if party exists.
      cur.execute("SELECT id FROM parties WHERE symbol = %s", [personParty])
      partyData = cur.fetchone();
      if partyData is not None: # add partyId to variable
        partyId = partyData[0]
      else: # add party
        query = ("INSERT INTO parties "
                "(symbol) "
                "VALUES "
                "(%s)")
        cur.execute(query, [personParty])
        partyId = cur.lastrowid
        print("Added party %s to db with id %d" % (personParty, partyId))

      # Check if politician exists.
      query = "SELECT id, name FROM politicians WHERE name = %s"
      cur.execute(query, [personName])
      p = cur.fetchone()
      if p is not None: # add to personId variable
         personId = p[0]
      else: # add politician to db
        # print("V has the id %s" % party_id[0])
        query = ("INSERT INTO politicians"
                "(party_id, name, picture_url, url)"
                "VALUES"
                "(%s, %s, %s, %s)")
        cur.execute(query, [partyId, personName, politician['picture_url'], politician['url']])
        personId = cur.lastrowid
        print("Added person %s to db with id %d" % (personName, personId))

      query = "INSERT INTO proposition_senders (proposition_id, politician_id) VALUES (%s, %s)";
      cur.execute(query, [propId, personId])
      print("Added politician %s as sender to propId %d as relationId %d" % (personName, propId, cur.lastrowid))

    print("Added %d senders to prop %s (%d)" % (len(politicians), title, propId))



    con.commit()

    # pp.pprint(politicians)
    # pp.pprint(handelser)
    # print(motionCategory)
    # print(dedicatedTo)
    # print(motions_cat, tilldelat, inlamnad, bordlagd, granskad, hanvisad, sep='\n', end='\n')
    # print(pdf_url, end='\n')
    # print(motion_url, end='\n')
    # print(title, motion_id, senders, sep='\n')
    print("------------------")



cur.close()
con.close()
exit();


# for i in range(1,sidor):
#   print("Parsing sidor/%d.html of %d..." % (i, sidor))
#   datasource = open('./sidor/%d.html' % i).read()
#   soup = BeautifulSoup(datasource, 'html.parser')

#   motions = soup.findAll(class_="content-list") # '.content-list.medium-12.columns'
#   for j in range(0, len(motions)):
#     motion = motions[j]
#     header = motion.header
#     title = header.a.string
#     link = header.a['href']
#     print("Fetching %s..." % link )

#     full_url = "%s%s" % (url, link)
#     resp = requests.get(full_url)
#     if resp.ok:
#         f = open('./motioner/p%d-m%d.html' % (i, j), 'w+')
#         f.write(resp.text)
#         print("Done, fetched, closing.")
#         f.close();
#     else:
#         print ("Boo! {}".format(resp.status_code))
#         print (resp.text)

# print(motions[0])
# print(len(motions))