START=$1
END=$[$1 + $2]
DATE=$(date +%Y-%m-%d$)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CMD_DUMP="$CHROME "

for i in $(seq $START $END); do 
  "$CHROME" \
  --headless --disable-gpu --dump-dom \
  "https://www.riksdagen.se/sv/dokument-lagar/?doktyp=mot&p=$i" \
  > "$DATE_p$i.html"
done