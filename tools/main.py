import config
import database
import itertools
import psycopg2
import spotipy
import functions
import time
import threading

from multiprocessing import Process, Lock
from random import shuffle
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(
    client_id=config.ENV['SP_ID'],
    client_secret=config.ENV['SP_SECRET'])

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, 
                     requests_timeout=config.ENV['SP_TIMEOUT'])

conn = psycopg2.connect('dbname=' + config.ENV['DB_NAME'] + ' ' + 
                        'user=' + config.ENV['DB_USER'] + ' ' + 
                        'password=' + config.ENV['DB_PASS'])

conn.set_session(autocommit=True)
cur = conn.cursor()
lock = Lock()

def artist_worker(combinated_genre):
    functions.insert_artists_by_genres(combinated_genre)

def album_worker(artist):
    functions.insert_albums(artist)

def song_worker(album):
    functions.insert_songs(album)
    
def sp_collector(arg, reset=False):
    if (arg == 'song'):
        items = functions.get_albums_from_db()
        func = song_worker
    elif (arg == 'album'):
        items = functions.get_artists_from_db()
        func = album_worker
    elif (arg == 'artist'):
        cur.execute('DELETE FROM combinated_genres;') if reset else None
        available_genres = functions.available_genres()
        combinated_genres = itertools.combinations(available_genres, config.ENV['NUM_COMBINATION'])
        combinated_genres = list(combinated_genres)
        if (len(combinated_genres) == 0):
            return
        shuffle(combinated_genres)
        functions.get_and_insert_artists(combinated_genres)
        return
    else:
        print('Spotify collector ERROR!')
        return

    iterator = 0
    for item in items:
        t = threading.Thread(target=func, args=(item,))
        t.start()
        iterator += 1
        time.sleep(2.5) if iterator % 5 == 0 else None

if __name__ == '__main__':
    database.create_tables(cur)
    sp_collector('artist', False)
    sp_collector('album')
    sp_collector('song')
    functions.genre_song_label()
    cur.close()
    conn.close()
