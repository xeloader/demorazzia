from parseMotionerByPage import *

files = getMotionFiles()
files.sort(reverse = True)
i = 0
end = len(files)
START = 0 # to skip motions, if run is aborted you may continue anywhere

for f in files:

  if i < START:
    i = i + 1
    continue

  printX("Parsing %s" % f, "m")

  motion = {}
  html = getHtmlFromFile(f)
  events = getEvents(html)

  motion["motionId"] = getMotionId(html)
  motion["added"] = getKeyFromEvents("inlämnad", events)
  motion["category"] = getKeyFromEvents("motionskategori", events)
  motion["assigned"] = getKeyFromEvents("tilldelat", events)
  motion["title"] = getTitle(html)
  motion["events"] = getEvents(html)
  motion["url"] = getURL(html)
  motion["pdf"] = getPdf(html)
  motion["body"] = getBodyFrom(html)
  motion["statements"] = getYrkandenFrom(html)
  motion["politicians"] = getPoliticians(html)

  newStores = storeMotion(motion)

  # print info
  percentage = "{0:.2f}".format(i / end * 100)
  printX("Progress", "{}%".format(percentage))

  mId = newStores["motionId"]
  if mId is not None:
    persons = ",".join(newStores["personIds"])
    parties = ",".join(newStores["partyIds"])
    relations = ",".join(newStores["relationIds"])

    printX("Added (%s)" % (mId), "mot")
    printX("Added (%s)" % (persons), "person")
    printX("Added (%s)" % (parties), "party")
    printX("Added (%s)" % (relations), "relation")
  else:
    printX("Already exists", "mot")

  print("---------------------------")

  i = i + 1