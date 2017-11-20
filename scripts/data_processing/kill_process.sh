# kill process by name
#PROCESS=zgrep
PROCESS=gzip
PROCESSES=$(ps aux | grep "$PROCESS" | awk '{print $2}')
echo $PROCESSES
kill $PROCESSES
