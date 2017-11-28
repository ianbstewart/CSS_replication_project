from __future__ import division
import json
import csv
import pandas as pd
from collections import defaultdict, Counter

LANG_ID_FILE = '../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered_langid.csv'
TWEETS_FILE = '../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered.json'
USERS_FILE = '../../data/user_groups.csv'

# cache lang ids
lang_ids = {}
with open(LANG_ID_FILE) as lang_id_file:
    cr = csv.reader(lang_id_file)
    cr.next() # pass header
    for t,l,c in cr:
        if float(c) < 0.9:
            continue
        if l == 'es' or l == 'ca':
            lang_ids[int(t)] = l

# get users
users = pd.read_csv(USERS_FILE)
user_ids = users['username'].tolist()

# mine tweets
user_langs = defaultdict(Counter)
js_dec = json.JSONDecoder()
with open(TWEETS_FILE) as tweets_file:
    for tj in tweets_file:
        tweet = js_dec.decode(tj)
        user = tweet['user']
        if user in user_ids:
            id = tweet['id']
            if id in lang_ids:
                user_langs[user][lang_ids[id]] += 1

def ca_rate(u):
    if u not in user_langs:
        return float('NaN')
    return user_langs[u]['ca'] / sum(user_langs[u].values())

users['ca_rate'] = [ca_rate(u) for u in user_ids]
print 'YES:', users[users['group'] == 'YES']['ca_rate'].mean()
print 'NO:', users[users['group'] == 'NO']['ca_rate'].mean()
print users[:10]