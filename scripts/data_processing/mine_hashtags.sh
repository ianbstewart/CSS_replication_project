DATA_DIR=../../data

## load hashtags
# regular list
#HASHTAG_FILE=$DATA_DIR/expanded_hashtags.csv
# expanded list
HASHTAG_FILE=$DATA_DIR/expanded_fixed_hashtags.csv
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
OUT_FILE=${ARCHIVE_FILE/.json/_ref_hashtags_fixed.json}

## define hashtag string
function join_by { local IFS="$1"; shift; echo "$*"; }
HASHTAG_STR=$(join_by "," "${HASHTAG_LIST[@]}")

## mine!
# from JSON
#QUERY_STR="select(.text | contains($HASHTAG_STR)) | [.text, .user.screen_name, .id, .created_at]"
# fromjson? used to check for valid JSON
QUERY_STR="fromjson? | select(.text | contains($HASHTAG_STR)) | [.text, .user.screen_name, .id, .created_at]"
# echo $QUERY_STR
# --raw-input and fromjson? used to check for valid JSON
./jq-linux64 -c "$QUERY_STR" --raw-input $ARCHIVE_FILE > $OUT_FILE