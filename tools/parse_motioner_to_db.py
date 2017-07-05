from bs4 import BeautifulSoup
import requests
import MySQLdb as mysql
import re
import pprint

url = "https://www.riksdagen.se"
pp = pprint.PrettyPrinter(indent=4)

# con = mysql.connect(
#   host='127.0.0.1',
#   database='demorazzia',
#   port=8889,
#   user='root',
#   password='root')

for i in range(1, 512):
  for j in range(0, 20):
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

    for idx in range(0, len(infos)):
      handelser.append(infos[idx].get_text())

    # motions_cat = infos[idx].get_text()
    # tilldelat = info.findAll(class_="medium-smaller")[1].get_text()
    # inlamnad = info.findAll(class_="medium-smaller")[2].get_text()
    # bordlagd = info.findAll(class_="medium-smaller")[3].get_text()
    # granskad = info.findAll(class_="medium-smaller")[4].get_text()
    # hanvisad = info.findAll(class_="medium-smaller")[5].get_text()
    pdf_url = html.find(class_="link-file file-type-pdf")
    bodyHtml = html.find(class_="Section1")
    body = None
    if bodyHtml is not None:
      body = bodyHtml.getText()
    yrkanden = html.find(id="item0").getText()


    politicians = []
    phtmls = html.findAll(class_="fellow-item-container") # personer som skickade in motionen.
    for phtml in phtmls:
      poli = {
        "picture_url": phtml.img['src'],
        "url": phtml['href'],
        "name": phtml.find(class_="fellow-name").text
      }
      poli['party'] = re.findall('\((.*?)\)', poli['name'])[0] # extract party from name
      politicians.append(poli)


    pp.pprint(politicians)
    pp.pprint(handelser)
    # print(motions_cat, tilldelat, inlamnad, bordlagd, granskad, hanvisad, sep='\n', end='\n')
    print(pdf_url, end='\n')
    print(title, motion_id, senders, sep='\n')
    print("------------------")


exit();
cur = con.cursor();

query = ("SELECT * FROM proposition_types")
cur.execute(query)

add_proposition = ("INSERT INTO propositions "
                  "(first_name, last_name, hire_date, gender, birth_date) "
                  "VALUES (%s, %s, %s, %s, %s)")

for (id, constant, name, description, parent) in cur:
  print("{}, {}, {}, {}, {}".format(id, constant, name, description, parent))

cur.close();
con.close();


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