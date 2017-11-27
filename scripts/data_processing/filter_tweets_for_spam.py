"""
Remove all tweets authored by users
who mostly (>90th percentile) post
tweets with URLs.
"""
from __future__ import division
import json
from argparse import ArgumentParser
from collections import defaultdict
import codecs
import re
import pandas as pd
from collections import Counter

def main():
    parser = ArgumentParser()
    parser.add_argument('--tweet_file', default='../../data/tweets/archive_Jan-01-17_Oct-31-17_ref_hashtags.json')
    parser.add_argument('--hashtag_file', default='../../data/expanded_fixed_hashtags.csv')
    args = parser.parse_args()
    tweet_file = args.tweet_file
    hashtag_file = args.hashtag_file

    ## load data
    tweet_data = []
    for i, l in enumerate(codecs.open(tweet_file, 'r', encoding='utf-8')):
        try:
            j = json.loads(l)
            # limit to relevant data!
            j_relevant = {'user' : j['user']['screen_name'], 'text' : j['text'], 
                          'date' : j['created_at'], 'id' : j['id'], 
                          'location.name' : '', 'location.country' : ''}
            if(j.get('location') is not None and j.get('location').get('place') is not None):
                j_place = j['location']['place']
                j_relevant['location.name'] = j_place['full_name']
                j_relevant['location.country'] = j_place['country']
            tweet_data.append(j_relevant)
        except Exception, e:
            pass
        if(i % 1000 == 0):
            print('processed %d tweets'%(i))
        if(i > 10000):
            break
    print('%d total tweets to start'%(len(tweet_data)))
    
    ## zero pass: make sure tweet contains at least one referendum hashtag
    hashtags = pd.read_csv(hashtag_file, sep=',', index_col=False).loc[:, 'expanded'].values.tolist()
    hashtag_matcher = re.compile('|'.join(hashtags))
    tweet_data = filter(lambda j: len(hashtag_matcher.findall(j['text'])) > 0, tweet_data)
    print('%d valid tweets'%(len(tweet_data)))

    ## first pass: get rid of RTs
    rt_matcher = re.compile('^rt[ :]')
    tweet_data = filter(lambda j: len(rt_matcher.findall(j['text'].lower())) == 0, tweet_data)
    print('%d original tweets'%(len(tweet_data)))
    # print('\n'.join([t['text'] for t in tweet_data[:10]]))

    ## second pass: get user URL counts
    user_url_counts = Counter()
    user_tweet_counts = Counter()
    URL_MATCHER = re.compile('https?://|twitter.com/')
    for j in tweet_data:
        j_txt = j['text']
        j_user = j['user']
        user_tweet_counts[j_user] += 1
        if(len(URL_MATCHER.findall(j['text'])) > 0):
            user_url_counts[j_user] += 1
    # normalize
    user_tweet_counts = pd.Series(user_tweet_counts)
    user_url_counts = pd.Series(user_url_counts)
    user_url_pcts = user_url_counts / user_tweet_counts.loc[user_url_counts.index]
    # compute 90th percentile
    pct = 90
    pct_cutoff = pd.np.percentile(user_url_pcts, pct)
    print('%d percentile of URL counts = %.3f'%(pct, pct_cutoff))
    print('%d high-URL users'%(len(user_url_pcts[user_url_pcts >= pct_cutoff])))
    # remove users with tweet count >= 5 and URL percent >= 90th percentile
    tweet_cutoff = 5
    filtered_users = (user_tweet_counts[user_tweet_counts >= tweet_cutoff].index & 
                      user_url_pcts[user_url_pcts >= pct_cutoff].index)
    filtered_user_tweets = user_tweet_counts.loc[filtered_users].sum()
    print('filtering %d users with %d tweets'%(len(filtered_users), filtered_user_tweets))
    
if __name__ == '__main__':
    main()
        
