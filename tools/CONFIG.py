URL = "https://www.riksdagen.se"
URL_MOTION = "%s/sv/dokument-lagar/?doktyp=mot" % (URL) # &p=$i

DIR_MOTIONS = "./motioner"

SQL_CONFIG = {
  "host": "127.0.0.1",
  "database": "demorazzia",
  "port": 8889,
  "user": "***REMOVED***",
  "password": "***REMOVED***"
}

BL_FILES = [".DS_Store"]