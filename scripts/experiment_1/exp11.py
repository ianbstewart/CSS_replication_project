from __future__ import division
import json
import csv
import pandas as pd
import progressbar
from collections import defaultdict, Counter
from random import shuffle

LANG_ID_FILE = '../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered_langid.csv'
TWEETS_FILE = '../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags_filtered.json'
USERS_FILE = '../../data/user_groups.csv'
PERMUTATIONS = 100000

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

print 'read {} language ids'.format(len(lang_ids))

# get users
users = pd.read_csv(USERS_FILE)
user_ids = users['username'].tolist()

print 'read {} user assignments'.format(len(users))

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

print 'read {} tweets in ca/es from users'.format(\
            sum([sum(ls.values()) for u,ls in user_langs.items()]))

def ca_rate(u):
    if u not in user_langs:
        return float('NaN')
    return user_langs[u]['ca'] / sum(user_langs[u].values())

users['ca_rate'] = [ca_rate(u) for u in user_ids]

def phats(df=users, gid='group'):
    phat_yes = df[df[gid] == 'YES']['ca_rate'].mean()
    phat_no = df[df[gid] == 'NO']['ca_rate'].mean()
    yn_d = phat_yes - phat_no
    return phat_yes, phat_no, yn_d
    
true_ph_yes, true_ph_no, true_yn_d = phats()
print 'YES:', true_ph_yes
print 'NO:', true_ph_no
print 'd:', true_yn_d

print 'Performing permutation test'
bar = progressbar.ProgressBar()
d_larger = 0
group_assigns = users['group'].tolist()
for i in bar(xrange(PERMUTATIONS)):
    shuffle(group_assigns)
    users['s_group'] = group_assigns
    _, _, d_i = phats(users, 's_group')
    if d_i > true_yn_d:
        d_larger += 1

print 'p:', d_larger / PERMUTATIONS