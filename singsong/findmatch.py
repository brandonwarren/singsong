from glob import iglob

class Song(object):
    def __init__(self, title, lyrics, url=None ):
        self.title = title
        self.lyrics = lyrics
        self.url = url
        self.num_used = 0

class Songs(object):
    def __init__(self, song_path=None, url_path=None):
        # load from csv file - later
        self.songs = []
        if not song_path:
            self.songs.append(Song('again', 'this never happened before'))
            self.songs.append(Song('first time', 'it feels like the first time'))
            self.songs.append(Song('i wanna hold your hand', 'i wanna hold your hand'))
            self.songs.append(Song('give me a hand', 'give me a hand'))
        else:
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
                        urls[title] = url

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
            if score > best_score and song.num_used < 1:
                best_score = score
                best_match = song
        best_match.num_used += 1
        return best_match, best_score

if __name__ == '__main__':
    song_path = '/home/brandon/other_projects/singsong/singsong/all.txt'
    url_path = '/home/brandon/other_projects/singsong/singsong/songs_url.csv'
    try:
        songs = Songs(song_path, url_path)
    except Exception as exp:
        print exp

    if not song_path:
        in_texts = [['this', 'never', 'happened', 'to', 'me'],
                    ['hold', 'hand'],
                    ['it', 'feels', 'like', 'the', 'first', 'time'],
                    ['hold', 'hand'],
                    ]
    else:
        in_texts = [['heaven', 'thunder'], # ch24
                    ['hold', 'hand'],
                    ['psychic', 'emanations'],
                    ['it', 'feels', 'like', 'the', 'first', 'time'],
                    ['romeo', 'juliet'],
                    ]

    for in_text in in_texts:
        song,score = songs.find_best_match(in_text)
        print 'best match (score={}) for {} is "{} {}"'.format(score, in_text, song.title, song.url)
