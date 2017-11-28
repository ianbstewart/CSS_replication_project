# mine all tweets in archive that were written by specified user
source generate_dates.sh
DATA_DIR=../../data
USER_COUNT_FILE=$DATA_DIR/user_groups.csv
USER_NAMES=$(tail -n+2 $USER_COUNT_FILE | cut -d, -f 2)

# join names
function join_by { local IFS="$1"; shift; echo "$*"; }
USER_NAME_STR=$(join_by "|" $USER_NAMES)
QUERY_STR="\"screen_name\":\"($USER_NAME_STR)\""
CORPUS_DIR=/hg190/corpora/twitter-crawl/new-archive
ARCHIVE_FILE=$CORPUS_DIR/tweets-Oct-01-17-04-06.gz
START_DATE=Dec-31-16
END_DATE=Oct-31-17
ARCHIVE_FILES=$(generate_date_files "$START_DATE" "$END_DATE")
OUT_FILE=$DATA_DIR/tweets/extra_user_tweets/"$START_DATE"_"$END_DATE"_user_tweets.json
if [ -e $OUT_FILE ];
then
    rm $OUT_FILE
fi
# use zgrep because it's FASTER than jq
for F in $ARCHIVE_FILES;
do
    echo "mining file $F"
    zgrep -P "$QUERY_STR" $ARCHIVE_FILE >> $OUT_FILE
done