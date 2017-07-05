from html.parser import HTMLParser
from lxml import html
from bs4 import BeautifulSoup
import requests
import os, os.path

url = "https://www.riksdagen.se"

# simple version for working with CWD
DIR = './sidor/'
sidor = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])

print("let's get this party started, %d motionssidor to go" % sidor)

for i in range(1,sidor):
  print("Parsing sidor/%d.html of %d..." % (i, sidor))
  datasource = open('./sidor/%d.html' % i).read()
  soup = BeautifulSoup(datasource, 'html.parser')

  motions = soup.findAll(class_="content-list") # '.content-list.medium-12.columns'
  for j in range(0, len(motions)):
    motion = motions[j]
    header = motion.header
    title = header.a.string
    link = header.a['href']
    print("Fetching %s..." % link )

    full_url = "%s%s" % (url, link)
    resp = requests.get(full_url)
    if resp.ok:
        f = open('./motioner/p%d-m%d.html' % (i, j), 'w+')
        f.write(resp.text)
        print("Done, fetched, closing.")
        f.close();
    else:
        print ("Boo! {}".format(resp.status_code))
        print (resp.text)

  # print(motions[0])
  # print(len(motions))