from fetchMotionerByPage import *

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