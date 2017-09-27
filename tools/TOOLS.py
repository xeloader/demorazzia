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