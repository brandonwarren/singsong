import json
from time import sleep

import tweepy
from nltk.tokenize import word_tokenize


LOCAL_ONLY = False # don't connect to twitter if True (for debug)
SECRETS_FILE = 'credentials.json'
SINCE_ID_FILE = 'since_id'
SONG_PATH = 'all_songs.txt'
URL_PATH = 'songs_url.csv'
OUR_BOT_NAME = 'botpavel26'
TIME_BETWEEN_POLL = 60 # seconds to sleep before polling Twitter again


if LOCAL_ONLY:
    sim = 'SAME_GROW' # emulate what Twitter API seems to be doing
    mention_id = 10
    num_mentions_to_ret = 4
    TIME_BETWEEN_POLL=1

    tweet_texts = [
        '{} heaven thunder'.format(OUR_BOT_NAME),  # ch24
        '{} hold hand'.format(OUR_BOT_NAME),
        '{} psychic emanations'.format(OUR_BOT_NAME),
        '{} it feels like the first time'.format(OUR_BOT_NAME),
        '{} romeo juliet'.format(OUR_BOT_NAME),
        ]

    class Author(object):
        def __init__(self):
            self.screen_name = 'Joe'

    class Mention(object):
        def __init__(self):
            global mention_id
            self.id = mention_id
            mention_id += 10
            tweet_index = self.id//10 - 2
            if tweet_index < 0:
                tweet_index = 0
            if tweet_index >= len(tweet_texts):
                tweet_index = 0
            self.text = tweet_texts[tweet_index]
            self.author = Author()
        def __str__(self):
            return str(self.id)

    def mock_mentions_timeline(since_id=None):
        # if since_id is None:
        #     since_id = 10
        global mention_id, num_mentions_to_ret
        if sim == 'PROPER':
            mentions = []
            for i in range(4):
                mentions.append(Mention())
            return mentions
        elif sim == 'SAME_GROW':
            mention_id = 10
            mentions = []
            for i in range(num_mentions_to_ret):
                mentions.append(Mention())
            num_mentions_to_ret += 4
            return mentions


class Song(object):
    def __init__(self, title, lyrics, url=None ):
        self.title = title
        self.lyrics = lyrics
        self.url = url
        self.num_used = 0


class Songs(object):
    def __init__(self, song_path=None, url_path=None):
        self.songs = []
        # load
        # for file in iglob(os.path.join(song_path,'*.txt')):
        #     with open(file) as f:
        #         line = f.read()
        #     title, lyrics = self.split(line)
        #     self.songs.append(title, lyrics)
        urls={} # key is song title
        if url_path:
            with open(url_path) as f:
                while 1:
                    line = f.readline()
                    if not line:
                        break
                    title, url = line.split(',')
                    urls[title] = url.strip()

        with open(song_path) as f:
            while 1:
                line = f.readline()
                if not line:
                    break
                title, lyrics = self.split(line)
                self.songs.append(Song(title, lyrics.lower(), urls.get(title)))

    def split(self, line):
#        closing_quote_indx = line.rfind('"')
        closing_quote_indx = 1 + line[1:].find('"')
        return line[1:closing_quote_indx], line[closing_quote_indx+1:]

    def compute_score(self, s, verse):
        score = 0
        for word in s:
            if word in verse:
                score += 1
        return score

    def find_best_match(self, words):
        best_score = -1
        best_match = None
        for song in self.songs:
            score = self.compute_score(words, song.lyrics)
            if score > best_score: # and song.num_used < 1:
                best_score = score
                best_match = song
        best_match.num_used += 1
        return best_match, best_score


def send_msg(api, msg, destination):
    try:
        status = api.send_direct_message(screen_name=destination, text=msg)
    except tweepy.error.TweepError as e:
        print('Error posting tweet: {}'.format(repr(e)))


def main():

    songs = Songs(SONG_PATH, URL_PATH)

    if not LOCAL_ONLY:
        # Twitter API setup
        with open(SECRETS_FILE) as f:
            secrets = json.load(f)
        auth = tweepy.OAuthHandler(secrets['consumer_key'], secrets['consumer_secret'])
        auth.set_access_token(secrets['access_token'], secrets['access_secret'])
        api = tweepy.API(auth)

    # since_id is earliest tweet (mention) we are interested in
    if LOCAL_ONLY:
        since_id=10
    else:
        since_id=783816354184900608
        try:
            with open(SINCE_ID_FILE) as f:
                line = f.readline()
                since_id = int(line)
        except:
            print('Unable to read {}. (ok if first time this has been run.)'.format(SINCE_ID_FILE))

    our_bot_name_len = len(OUR_BOT_NAME)

    try:
        while True:
            if LOCAL_ONLY:
                mentions = mock_mentions_timeline(since_id=since_id)
            else:
                mentions = api.mentions_timeline(since_id=since_id)
            print('got {} mentions'.format(len(mentions)))
            for mention in mentions:
                if mention.id <= since_id:
                    print('since_id filter not working: mention.id={} since_id={}'.format(
                        mention.id, since_id))
                    continue
                tweet_author = mention.author.screen_name
                tweet_text = mention.text[our_bot_name_len+1:]
                song,score = songs.find_best_match(word_tokenize(tweet_text))
                msg = '{} {}'.format(song.title, song.url)
                print('To {} in resp to "{}", to tweet "{}" (score={}, id={})'.format(
                    tweet_author, tweet_text, msg, score, mention.id))
                if not LOCAL_ONLY:
                    send_msg(api, msg, tweet_author)
                since_id = mention.id
            print('about to sleep for {} sec'.format(TIME_BETWEEN_POLL),)
            sleep(TIME_BETWEEN_POLL)
            print('woke up')
    except KeyboardInterrupt:
        print('keyboard interrupt')
    finally:
        with open(SINCE_ID_FILE, 'w') as f:
            f.write('{}\n'.format(since_id))
        print('{} updated'.format(SINCE_ID_FILE))

if __name__ == '__main__':
    main()
