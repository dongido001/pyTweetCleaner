#!/usr/bin/env python

"""
pyTweetCleaner.py: Python module to clean twitter json data and remove unnecessary tweet data

REMOVE:        TWEETS THAT HAVE in_reply_to_status_id !=null i.e. COMMENTS ON SOMEONE ELSE'S TWEETS
               TWEETS THAT HAVE lang != en i.e. NOT IN ENGLISH LANGUAGE
               DATA ABOUT DELETED TWEETS
               NON-ASCII CHARACTERS FROM text
               links FROM text
               HASH(#) SYMBOLS BUT KEEP HASHTAG AS NORMAL TWEET TEXT BUT SPLIT HASHTAG AT UPPERCASE LETTERS 
               @ SYMBOL IN @name MENTIONS IN TEXT AND SPLITTING NAME AT UPPERCASE. EX: '@AbcXyz' --> 'abc xyz' 
  
KEEP:          created_at
               id
               text IN LOWERCASE AFTER SPLITTING COMPOUND WORDS, REMOVING STOPWORDS AND WORDS OF LENGTH 1
               user_id
               user_name
               user_screen_name
               geo
               coordinates
               place
               retweet_count
               entities
"""

__author__ = 'Keval Morabia'
__license__ = 'MIT'
__email__ = 'kevalmorabia97@gmail.com'

import json
import re
import string 

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class TweetCleaner:
    def __init__(self, remove_stop_words = False, remove_retweets=True):
        """
        clean unnecessary twitter data
        remove_stop_words = True if stopwords are to be removed (default = False)
        remove_retweets = True if retweets are to be removed (default = True)
        """
        
        if remove_stop_words: self.stop_words = set(stopwords.words('english'))
        else: self.stop_words = set()
        
        self.remove_retweets = remove_retweets
        
        self.punc_table = str.maketrans("", "", string.punctuation) # to remove punctuation from each word in tokenize
    
    def compound_word_split(self, compound_word):
        """
        Split a given compound word and return list of words in given compound_word
        Ex: 'pyTWEETCleaner' --> ['py', 'TWEET', 'Cleaner']
        """
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', compound_word)
        return [m.group(0) for m in matches]
    
    def remove_non_ascii_chars(self, text):
        """
        return text after removing non-ascii characters i.e. characters with ascii value >= 128
        """
        return ''.join([w if ord(w) < 128 else ' ' for w in text])
    
    def remove_hyperlinks(self,text):
        """
        return text after removing hyperlinks
        """
        return ' '.join([w for w in text.split(' ')  if not 'http' in w])
      
    def get_cleaned_text(self, text):
        cleaned_text = text.replace('\"','').replace('\'','').replace('-',' ')
            
        cleaned_text =  self.remove_non_ascii_chars(cleaned_text)
        
        # retweet
        if cleaned_text.startswith('RT @'): # retweet
            if self.remove_retweets: return ''
            cleaned_text = cleaned_text[cleaned_text.index(':')+2:]
        
        cleaned_text = self.remove_hyperlinks(cleaned_text)
        
        cleaned_text = cleaned_text.replace('#','splitstart').replace('@','splitstart') # to split #hashtags and @name after removing punctuations
        
        tokens = [w.translate(self.punc_table) for w in word_tokenize(cleaned_text)] # remove punctuations and tokenize
        new_tokens = []
        for w in tokens: 
            if w.startswith('splitstart'): new_tokens += self.compound_word_split(w[10:])
            else: new_tokens.append(w)
        tokens = [w.lower() for w in new_tokens if not w.lower() in self.stop_words and len(w)>1]
        cleaned_text = ' '.join(tokens)
        
        return cleaned_text

    def clean_tweets(self, input_file, output_file='cleaned_tweets.json'):    
        """
        input_file: name or path of input twitter json data
        output_file: file name or path where cleaned twitter json data is stored (default='cleaned_tweets.json')
        """
        in_file = open(input_file, 'r')
        out_file = open(output_file, 'w')
        
        while True:
            line = in_file.readline()
            if line=='': break
            tweet = json.loads(line)
            
            if not "created_at" in tweet: continue # remove info about deleted tweets
            if not tweet['lang'] == 'en': continue # remove tweets in non engligh(or lang) language
            if not tweet['in_reply_to_status_id'] == None or not tweet['in_reply_to_user_id'] == None: continue # remove comments of any tweet
            
            cleaned_text = self.get_cleaned_text(tweet['text'])
            if cleaned_text == '': continue

            cleaned_tweet = {}
            cleaned_tweet['created_at'] = tweet['created_at']
            cleaned_tweet['id'] = tweet['id']
            cleaned_tweet['text'] = cleaned_text
            cleaned_tweet['user'] = {}
            cleaned_tweet['user']['id'] = tweet['user']['id']
            cleaned_tweet['user']['name'] = tweet['user']['name']
            cleaned_tweet['user']['screen_name'] = tweet['user']['screen_name']
            cleaned_tweet['geo'] = tweet['geo']
            cleaned_tweet['coordinates'] = tweet['coordinates']
            cleaned_tweet['place'] = tweet['place']
            cleaned_tweet['retweet_count'] = tweet['retweet_count']
            cleaned_tweet['entities'] = tweet['entities']
            
            out_file.write(json.dumps(cleaned_tweet)+'\n')
        
        in_file.close()
        out_file.close()
    
if __name__  == '__main__':
    #tc = TweetCleaner(remove_stop_words = False)
    tc = TweetCleaner(remove_stop_words = True, remove_retweets=True)
    tc.clean_tweets(input_file='data/sample_input.json', output_file='data/sample_output.json')
    print(tc.get_cleaned_text('Cleaning unnecessary data with pyTweetCleaner by @kevalMorabia97. #pyTWEETCleaner Check it out at https:\/\/github.com\/kevalmorabia97\/pyTweetCleaner'))    
    print('TweetCleaning DONE...')
