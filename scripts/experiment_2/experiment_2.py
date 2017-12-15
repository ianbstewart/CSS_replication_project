"""
Hard-coded version of experiment_2.ipynb and experiment_2_addon.ipynb.
"""
from __future__ import division
import pandas as pd
from argparse import ArgumentParser
from scipy.stats import ttest_1samp
import re
import logging
import os

def run_compare_test(tweet_data_1, tweet_data_2):
    relevant_users = set(tweet_data_1.loc[:, 'user'].unique()) & set(tweet_data_2.loc[:, 'user'].unique())
    tweet_data_relevant_1 = tweet_data_1[tweet_data_1.loc[:, 'user'].isin(relevant_users)]
    tweet_data_relevant_2 = tweet_data_2[tweet_data_2.loc[:, 'user'].isin(relevant_users)]
    logging.info('%d tweets in data 1'%(tweet_data_relevant_1.shape[0]))
    logging.info('%d tweets in data 2'%(tweet_data_relevant_2.shape[0]))
    logging.info('%d relevant users'%(len(relevant_users)))
    ca_1 = tweet_data_relevant_1.groupby('user').apply(lambda x: (x.loc[:, 'lang']=='ca').astype(int).sum() / x.shape[0])
    ca_2 = tweet_data_relevant_2.groupby('user').apply(lambda x: (x.loc[:, 'lang']=='ca').astype(int).sum() / x.shape[0])
    ca_use_diff = ca_1 - ca_2
    d_u = ca_use_diff.mean()
    N = len(ca_use_diff)
    d_u_err = ca_use_diff.std() / N**.5
    h_0 = 0.
    t_stat, p_val = ttest_1samp(ca_use_diff, h_0)
    logging.info('d_u = %.5f, err = %.5f, t=%.3f (p=%.3E)'%(d_u, d_u_err, t_stat, p_val))
    return d_u, d_u_err, t_stat, p_val

def main():
    parser = ArgumentParser()
    parser.add_argument('--tweet_file', default='../../data/tweets/extra_user_tweets/Jan-01-17_Oct-31-17_user_tweets.tsv')
    args = parser.parse_args()
    tweet_file = args.tweet_file
    if(not os.path.exists('../../output/')):
        os.mkdir('../../output/')
    logging.basicConfig(level=logging.INFO, filemodel='w', format='%(message)s', filename='../../output/experiment_2.txt')

    ## load data
    tweet_data = pd.read_csv(tweet_file, sep='\t', index_col=False)
    tweet_data.fillna('', inplace=True)
    tweet_data.loc[:, 'hashtag_count'] = tweet_data.loc[:, 'hashtags'].apply(lambda x: 0 if x=='' else len(x.split(',')))
    # tag @-replies
    at_matcher = re.compile('@\w+')
    tweet_data.loc[:, 'reply'] = tweet_data.apply(lambda r: int(len(at_matcher.findall(r.loc['text'])) > 0 and r.loc['retweeted']==0), axis=1)
    # and hashtag counts
    tweet_data.loc[:, 'hashtag_count'] = tweet_data.loc[:, 'hashtags'].apply(lambda x: len(x.split(',')) if x != '' else 0)
    tweet_data_original = tweet_data[tweet_data.loc[:, 'retweeted'] == 0]
    # language cutoff
    lang_conf_cutoff = 0.90
    allowed_langs = set(['es', 'ca'])
    tweet_data_original_high_conf = tweet_data_original[(tweet_data_original.loc[:, 'lang_conf'] >= lang_conf_cutoff) &
                                                        (tweet_data_original.loc[:, 'lang'].isin(allowed_langs))]
    logging.info('%d relevant tweets'%(tweet_data_original_high_conf.shape[0]))
    # restrict to relevant users
    relevant_users = tweet_data_original_high_conf.groupby('user').apply(lambda x: (x.loc[:, 'contains_ref_hashtag'].max()==1 and 
                                                                                    x.loc[:, 'contains_ref_hashtag'].min()==0))
    relevant_users = relevant_users[relevant_users].index.tolist()
    logging.info('%d relevant users'%(len(relevant_users)))
    tweet_data_relevant = tweet_data_original_high_conf[tweet_data_original_high_conf.loc[:, 'user'].isin(relevant_users)]
    logging.info('%d relevant tweets'%(tweet_data_relevant.shape[0]))

    ## split into referendum and control data
    logging.info('starting referendum versus control test')
    tweet_data_ref = tweet_data_relevant[tweet_data_relevant.loc[:, 'contains_ref_hashtag'] == 1]
    tweet_data_control = tweet_data_relevant[tweet_data_relevant.loc[:, 'contains_ref_hashtag'] == 0]
    logging.info('%d referendum tweets'%(tweet_data_ref.shape[0]))
    logging.info('%d non-referendum tweets'%(tweet_data_control.shape[0]))
    logging.info('%d users'%(tweet_data_relevant.loc[:, 'user'].nunique()))
    logging.info('referendum tweet language distribution')
    logging.info(tweet_data_ref.loc[:, 'lang'].value_counts())
    logging.info('control tweet language distribution')
    logging.info(tweet_data_control.loc[:, 'lang'].value_counts())

    ### first test: referendum versus non-referendum tweets

    ## compute probability of Catalan in referendum and control tweets
    test_lang = 'ca'
    compute_prob_lang = lambda x: x[x.loc[:, 'lang'] == test_lang].shape[0] / x.shape[0]
    cat_prob_ref = tweet_data_ref.groupby('user').apply(compute_prob_lang)
    cat_prob_control = tweet_data_control.groupby('user').apply(compute_prob_lang)
    all_control_d_u = cat_prob_ref - cat_prob_control
    all_control_d_u_mean = all_control_d_u.mean()
    all_control_d_u_stderr = all_control_d_u.std() / len(all_control_d_u)**.5
    logging.info('d_u for all control tweets is %.3f +/- %.3f'%(all_control_d_u_mean, all_control_d_u_stderr))
    
    ## test for significance
    d_u_null = 0.
    t_stat, p_val = ttest_1samp(all_control_d_u, d_u_null)
    logging.info('significance: t=%.3f p=%.3E'%(t_stat, p_val))

    ### second test: referendum versus non-referendum tweets with hashtags
    logging.info('starting referendum versus hashtag control test')

    ## re-segment data
    tweet_data_with_hashtags = tweet_data_original_high_conf[tweet_data_original_high_conf.loc[:, 'hashtag_count'] > 0]
    # recompute relevant users
    relevant_users = tweet_data_with_hashtags.groupby('user').apply(lambda x: (x.loc[:, 'contains_ref_hashtag'].max()==1 and 
                                                                               x.loc[:, 'contains_ref_hashtag'].min()==0))
    relevant_users = relevant_users[relevant_users].index.tolist()
    # recompute relevant data
    tweet_data_relevant_with_hashtags = tweet_data_with_hashtags[tweet_data_with_hashtags.loc[:, 'user'].isin(relevant_users)]
    tweet_data_ref = tweet_data_relevant_with_hashtags[tweet_data_relevant_with_hashtags.loc[:, 'contains_ref_hashtag'] == 1]
    tweet_data_control = tweet_data_relevant_with_hashtags[tweet_data_relevant_with_hashtags.loc[:, 'contains_ref_hashtag'] == 0]
    logging.info('%d referendum tweets'%(tweet_data_ref.shape[0]))
    logging.info('%d non-referendum tweets'%(tweet_data_control.shape[0]))
    logging.info('%d users'%(tweet_data_relevant_with_hashtags.loc[:, 'user'].nunique()))
    cat_prob_ref = tweet_data_ref.groupby('user').apply(compute_prob_lang)
    cat_prob_control = tweet_data_control.groupby('user').apply(compute_prob_lang)
    hashtag_control_d_u = cat_prob_ref - cat_prob_control
    hashtag_control_d_u_mean = hashtag_control_d_u.mean()
    hashtag_control_d_u_stderr = hashtag_control_d_u.std() / len(hashtag_control_d_u)**.5
    logging.info('d_u for all control hashtag tweets is %.3f +/- %.3f'%(hashtag_control_d_u_mean, hashtag_control_d_u_stderr))
    d_u_null = 0.
    t_stat, p_val = ttest_1samp(hashtag_control_d_u, d_u_null)
    logging.info('significance: t=%.3f p=%.3E'%(t_stat, p_val))

    ## third test: @-replies versus non-replies with hashtag
    #reply_data = tweet_data_original[(tweet_data_original.loc[:, 'reply']==1) & (tweet_data_original.loc[:, 'hashtag_count']==0)]
    #hashtag_data = tweet_data_original[(tweet_data_original.loc[:, 'reply']==0) & (tweet_data_original.loc[:, 'hashtag_count']>0)]
    logging.info('starting reply versus not-reply test')
    reply_data = tweet_data_original_high_conf[(tweet_data_original_high_conf.loc[:, 'reply']==1) & (tweet_data_original_high_conf.loc[:, 'hashtag_count']==0)]
    hashtag_data = tweet_data_original_high_conf[(tweet_data_original_high_conf.loc[:, 'reply']==0) & (tweet_data_original_high_conf.loc[:, 'hashtag_count']>0)]
    test_results = run_compare_test(reply_data, hashtag_data)

if __name__ == '__main__':
    main()
