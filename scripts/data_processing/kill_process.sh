# kill process by name
#1;95;0cPROCESS=zgrep
#PROCESS=gzip
#PROCESS="bash mine_hashtags_in_chunks.sh"
PROCESS="./jq-linux64"
PROCESSES=$(ps aux | grep "$PROCESS" | awk '{print $2}')
echo $PROCESSES
kill $PROCESSES
