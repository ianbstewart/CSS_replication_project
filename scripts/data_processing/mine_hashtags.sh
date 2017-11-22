DATA_DIR=../../data

## load hashtags
HASHTAG_FILE=$DATA_DIR/expanded_hashtags.csv
HASHTAG_LIST=( $(tail -n +2 $HASHTAG_FILE | cut -d ',' -f2))
# echo "${HASHTAG_LIST[@]}"
HASHTAG_COUNT="${#HASHTAG_LIST[@]}"
echo "$HASHTAG_COUNT hashtags collected"
# add quote marks to all hashtags
for ((i=0;i<$HASHTAG_COUNT;i++)); do
    HASHTAG_LIST[i]="\"#${HASHTAG_LIST[i]}\""
done

## define file(s)
ARCHIVE_FILE=$DATA_DIR/tweets/archive_Sep-30-16_Oct-31-17_ES_tweets.json
OUT_FILE=${ARCHIVE_FILE/.json/ref_hashtags.json}

## define hashtag string
function join_by { local IFS="$1"; shift; echo "$*"; }
HASHTAG_STR=$(join_by "," "${HASHTAG_LIST[@]}")

## mine!
QUERY_STR="select(.text | contains($HASHTAG_STR))"
echo $QUERY_STR
jq -c "$QUERY_STR" $ARCHIVE_FILE > $OUT_FILE