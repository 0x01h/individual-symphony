import config
import csv
import datetime
import main
import multiprocessing
import psycopg2
import time

sp = main.sp
cur = main.cur
lock = main.lock

def available_genres():
    try:
        print('Available genres for recommendation was requested!')
        results = sp.recommendation_genre_seeds()['genres']
        print('Available genres: ' + (', '.join(results)))
        return results

    except Exception as e:
        print('Available genres ERROR!')
        print(e)

def genre_song_label():
    try:
        row = []
        songs = get_songs_from_db()
        f = open('../datasets/labeled_songs.csv', 'w')

        with f:
            writer = csv.writer(f)
            for song in songs:
                artist_id = song[15]
                print('artist_id ' + artist_id)
                cur.execute("SELECT * FROM artists WHERE id=(%s);", (artist_id, ))
                artist = cur.fetchone()
                artist_genre = artist[2]

                if (artist_genre is None or artist_genre in ['', '[]', '{}']):
                    print('Artist genre is NULL!')
                    continue

                row = [artist_genre, str(song[0]), str(song[1]), str(song[2]), str(song[3]), str(song[4]), 
                       str(song[5]), str(song[6]), str(song[7]), str(song[8]), str(song[9]), str(song[10]),
                       str(song[11]), str(song[12]), str(song[13]), str(song[14])]

                writer.writerow(row)

    except Exception as e:
        print('Song labeling ERROR!')
        print(e)

def get_artist(artist_id):
    try:
        print('Artist information for ' + artist_id + ' was requested!')
        artist_obj = sp.artist(artist_id)

        if (artist_obj == None):
            print('Artist information returned NULL!')
            return None

        print('Information for ' + artist_obj['name'] + ' was successfully fetched!')
        return artist_obj

    except Exception as e:
        print('Artist information ERROR!')
        print(e)

def get_album(album_id):
    try:
        print('Album information for ' + album_id + ' was requested!')
        album_obj = sp.album(album_id)

        if (album_obj == None):
            print('Album information returned NULL!')
            return None

        print('Information for ' + album_obj['name'] + ' was successfully fetched!')
        return album_obj

    except Exception as e:
        print('Artist information ERROR!')
        print(e)

def get_albums_by_artist(artist_id):
    try:
        print('Album information for ' + artist_id + ' was requested!')
        album_obj = sp.artist_albums(artist_id, album_type='album', limit=50)

        if (album_obj == None):
            print('Album information returned NULL!')
            return None
        
        for single_album in album_obj['items']:
            print('Information for ' + single_album['name'] + ' was successfully fetched!')
            
        return album_obj

    except Exception as e:
        print('Album information by artist ERROR!')
        print(e)

def get_songs_by_album(album_id):
    try:
        print('Song information for ' + album_id + ' was requested!')
        song_obj = sp.album_tracks(album_id, limit=50)

        if (song_obj == None):
            print('Song information returned NULL!')
            return None

        for single_song in song_obj['items']:
            print('Information for ' + single_song['name'] + ' was successfully fetched!')

        return song_obj
    
    except Exception as e:
        print('Song information ERROR!')
        print(e)

def get_song_features(song_id):
    try:
        audio_features = {}
        print('Song features for ' + song_id + ' was requested!')
        audio_obj = sp.audio_features(song_id)

        if (audio_obj == None):
            print('Song features returned NULL!')
            return None

        audio_features['acousticness'] = audio_obj[0]['acousticness']
        audio_features['instrumentalness'] = audio_obj[0]['instrumentalness']
        audio_features['valence'] = audio_obj[0]['valence']
        audio_features['loudness'] = audio_obj[0]['loudness']
        audio_features['energy'] = audio_obj[0]['energy']
        audio_features['liveness'] = audio_obj[0]['liveness']
        audio_features['danceability'] = audio_obj[0]['danceability']
        audio_features['tempo'] = audio_obj[0]['tempo']
        audio_features['speechiness'] = audio_obj[0]['speechiness']
        audio_features['mode'] = audio_obj[0]['mode']
        audio_features['duration_ms'] = audio_obj[0]['duration_ms']
        audio_features['time_signature'] = audio_obj[0]['time_signature']
        audio_features['key'] = audio_obj[0]['key']

        print('Song features for ' + song_id + ' was successfully fetched!')
        return audio_features

    except Exception as e:
        print('Song features ERROR!')
        print(e)

def get_artists_by_recommendation_genre(seeder):
    results = sp.recommendations(seed_genres=seeder, limit=50)
    results = results['tracks']
    results_pot = []

    for result in results:
        if (len(result['artists']) > 1):
            for single_artist in result['artists']:
                spotify_id = single_artist['id']
                lock.acquire()
                cur.execute("SELECT COUNT(*) FROM artists WHERE id=(%s);", (spotify_id, ))

                if (cur.fetchone()[0] == 1):
                    print(spotify_id + ' artist is already in DB.')
                    lock.release()
                    continue
                else:
                    lock.release()

                artist_obj = get_artist(spotify_id)
                if (not artist_obj):
                    print('Artist object is NULL!')
                    continue

                popularity = artist_obj['popularity']
                genres = artist_obj['genres']

                if (popularity < config.ENV['MIN_ARTIST_POP'] or (len(genres) == 0) or (genres is None)):
                    print('Not enough popularity or genre not found!')
                    continue

                name = single_artist['name']
                results_pot.append((spotify_id, name, genres, popularity))
                
        else:
            single_artist = result['artists'][0]
            spotify_id = single_artist['id']
            lock.acquire()
            cur.execute("SELECT COUNT(*) FROM artists WHERE id=(%s);", (spotify_id, ))

            if (cur.fetchone()[0] == 1):
                print(spotify_id + ' artist is already in DB.')
                lock.release()
                continue
            else:
                lock.release()

            artist_obj = get_artist(spotify_id)
            popularity = artist_obj['popularity']
            if (not artist_obj):
                print('Artist object is NULL!')
                continue
            if (popularity < config.ENV['MIN_ARTIST_POP']):
                continue

            name = single_artist['name']
            genres = artist_obj['genres']
            results_pot.append((spotify_id, name, genres, popularity))

    return results_pot

def insert_artists_by_genres(combinated_genre):
    try:
        seeder = combinated_genre
        artists = get_artists_by_recommendation_genre(seeder)
            
        for artist in artists:
            try:
                lock.acquire()
                cur.execute("SELECT COUNT(*) FROM artists WHERE id=(%s);", (artist[0], ))

                if ((len(artist[2]) == 0) or (artist[2] is None)):
                    print(artist[0] + ' artist genre is NOT FOUND!')
                    lock.release()
                elif (cur.fetchone()[0] == 1):
                    print(artist[0] + ' artist is already in DB.')
                    lock.release()
                    continue
                else:
                    lock.release()

                lock.acquire()
                cur.execute("""INSERT INTO artists (
                    id, name, genres, popularity, created_at) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (artist[0], artist[1], artist[2], artist[3], datetime.datetime.utcnow()))
                lock.release()

            except psycopg2.IntegrityError as e:
                print('Exception was captured but program is still in progress.')  # Mostly to prevent DB from duplicated PKs.
                print(e)
                lock.release()
                continue

            except Exception as e:
                print(e)
                continue

    except KeyboardInterrupt:
        print('Process was interrupted!')
        return

def get_and_insert_artists(combinated_genres):
    try:
        num_active_processes = 0
        for single_combinated_genre in combinated_genres:
            concatenated_genre = ("-".join(single_combinated_genre))
            lock.acquire()
            cur.execute("SELECT COUNT(*) FROM combinated_genres WHERE name=(%s);", (concatenated_genre, ))

            if (cur.fetchone()[0] == 1):
                print("-".join(single_combinated_genre) + ' combinated genre was already fetched!')
                lock.release()
                continue
            else:
                lock.release()

            if (num_active_processes < config.ENV['NUM_PROCESSES']):
                p = multiprocessing.Process(target=insert_artists_by_genres, args=(single_combinated_genre,))
                p.daemon = True
                p.start()
                num_active_processes += 1
            else:
                insert_artists_by_genres(single_combinated_genre)
                time.sleep(config.ENV['MULTIPROCESS_SLEEP'])
                num_active_processes = 0

            lock.acquire()
            cur.execute("""INSERT INTO combinated_genres (
                    name, created_at) 
                    VALUES (%s, %s)""",
                    (concatenated_genre, datetime.datetime.utcnow()))
            print("-".join(single_combinated_genre) + ' combinated genre was written in DB!')
            lock.release()

    except KeyboardInterrupt:
        print('User interrupted the process!')

    except Exception as e:
        print(e)

def insert_albums(artist):
    try:
        for album in get_albums_by_artist(artist[0])['items']:
            if (album == None):
                continue

            album_obj = get_album(album['id'])

            if (album_obj == None):
                continue

            album_id = album_obj['id']
            lock.acquire()
            cur.execute("SELECT COUNT(*) FROM albums WHERE id=(%s);", (album_id, ))

            if (cur.fetchone()[0] == 1):
                print(album_id + ' album is already in DB.')
                lock.release()
                continue
            else:
                lock.release()

            album_name = album_obj['name']
            # album_genres = album_obj['genres']
            total_tracks = album_obj['total_tracks']
            artist_id = artist[0]
            artist_name = artist[1]

            lock.acquire()
            cur.execute("""INSERT INTO albums (
                    id, name, total_tracks, artist_id, artist_name, created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (album_id, album_name, total_tracks, artist_id, artist_name, datetime.datetime.utcnow()))
            print(album_id + ' album was written in DB.')
            lock.release()

    except KeyboardInterrupt:
        print('User interrupted the process!')

    except Exception as e:
        print(e)

def insert_songs(album):
    try:
        for song in get_songs_by_album(album[0])['items']:

            if (song == None):
                continue

            song_id = song['id']
            lock.acquire()
            cur.execute("SELECT COUNT(*) FROM songs WHERE id=(%s);", (song_id, ))

            if (cur.fetchone()[0] == 1):
                print(song_id + ' song is already in DB.')
                lock.release()
                continue
            else:
                lock.release()

            song_name = song['name']
            song_feature_obj = get_song_features(song_id)

            if (song_feature_obj == None):
                continue

            acousticness = song_feature_obj['acousticness']
            instrumentalness = song_feature_obj['instrumentalness']
            valence = song_feature_obj['valence']
            loudness = song_feature_obj['loudness']
            energy = song_feature_obj['energy']
            liveness = song_feature_obj['liveness']
            danceability = song_feature_obj['danceability']
            tempo = song_feature_obj['tempo']
            speechiness = song_feature_obj['speechiness']
            mode = song_feature_obj['mode']
            duration_ms = song_feature_obj['duration_ms']
            time_signature = song_feature_obj['time_signature']
            key = song_feature_obj['key']

            artist_id = album[3]
            artist_name = album[4]
            album_id = album[0]
            album_name = album[1]

            lock.acquire()
            cur.execute("""INSERT INTO songs (
                    id, name, 
                    acousticness, instrumentalness, valence, loudness, energy, liveness, danceability, tempo, speechiness,
                    mode, duration_ms, time_signature, key,
                    artist_id, artist_name, album_id, album_name, 
                    created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (song_id, song_name, 
                    acousticness, instrumentalness, valence, loudness, energy, liveness, danceability, tempo, speechiness, 
                    mode, duration_ms, time_signature, key,
                    artist_id, artist_name, album_id, album_name,
                    datetime.datetime.utcnow()))
            print(song_id + ' song was written in DB.')
            lock.release()

    except KeyboardInterrupt:
        print('User interrupted the process!')

    except Exception as e:
        print(e)

def insert_predictions(prediction):
    try:
        if (prediction == None):
            print('Prediction is NONE!')
            return

        song_id = prediction['id']
        song_name = prediction['name']
        r_b = float(prediction['probs'][0][0])
        rap = float(prediction['probs'][0][1])
        electronic = float(prediction['probs'][0][2])
        rock = float(prediction['probs'][0][3])
        new_age = float(prediction['probs'][0][4])
        classical = float(prediction['probs'][0][5])
        reggae = float(prediction['probs'][0][6])
        blues = float(prediction['probs'][0][7])
        country = float(prediction['probs'][0][8])
        world = float(prediction['probs'][0][9])
        folk = float(prediction['probs'][0][10])
        easy_listening = float(prediction['probs'][0][11])
        jazz = float(prediction['probs'][0][12])
        vocal = float(prediction['probs'][0][13])
        punk = float(prediction['probs'][0][14])
        alternative = float(prediction['probs'][0][15])
        pop = float(prediction['probs'][0][16])
        heavy_metal = float(prediction['probs'][0][17])

        lock.acquire()
        cur.execute("""INSERT INTO song_genre_predictions (
                    id, name, r_b, rap, electronic, rock, new_age, classical, reggae, blues, country, world, folk, easy_listening, jazz, vocal, punk, alternative, pop, heavy_metal, created_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (song_id, song_name, r_b, rap, electronic, rock, new_age, classical, reggae, blues, country, world, folk, easy_listening, jazz, vocal, punk, alternative, pop, heavy_metal, datetime.datetime.utcnow()))
        print(song_id + ' song was written in DB.')
        lock.release()

    except KeyboardInterrupt:
        print('User interrupted the process!')

    except Exception as e:
        print(e)

def plt_predictions():
    # Sample prediction bar charts for genre classifier model results.
    # Save results as 'png' in 'figures' folder.
    # Radiohead - Alternative/Rock
    # Justin Bieber - Pop
    # Nirvana - Rock
    # 6ix9ine - Rap

    genres = ['r_b', 'rap', 'electronic', 'rock', 'new_age', 'classical', 'reggae', 'blues', 'country',
    'world', 'folk', 'easy_listening', 'jazz', 'vocal', 'punk', 'alternative', 'pop', 'heavy_metal']
    artist_names = ['radiohead', 'justin_bieber', 'nirvana', '6ix9ine']
    artist_id = {
        'radiohead': '4Z8W4fKeB5YxbusRsdQVPb',
        'justin_bieber': '1uNFoZAHBGtllmzznpCI3s',
        'nirvana': '6olE6TJLqED3rqDCT0FyPh',
        '6ix9ine': '7gZfnEnfiaHzxARJ2LeXrf'
    }

    for artist_name in artist_names:
        songs = get_songs_of_artist_from_db(artist_id[artist_name])
        song_ids = [x[0] for x in songs]
        for song_id in song_ids:
            prediction = get_genre_predictions_from_db(song_id)
            song_name = prediction[0][1].replace('/', '_').replace('.', '_')
            prediction = [[x[2:20] for x in prediction]]
            prediction = prediction[0][0]
            plt.subplots(num=None, figsize=(18, 10), dpi=60, facecolor='w', edgecolor='k')
            plt.xlabel('Genre Correlation Value')
            plt.ylabel('Genres')
            plt.barh(genres, prediction)
            plt.title(song_name)
            plt.savefig('figures/' + artist_name + '/' + song_name + '-' + song_id)
            # plt.show()
            plt.clf()
            plt.close()

def get_artists_from_db():
    cur.execute("SELECT * FROM artists ORDER BY RANDOM()")
    return cur.fetchall()

def get_albums_from_db():
    cur.execute("SELECT * FROM albums ORDER BY RANDOM()")
    return cur.fetchall()

def get_songs_from_db():
    cur.execute("SELECT * FROM songs ORDER BY RANDOM()")
    return cur.fetchall()

def get_count_songs_from_db():
    cur.execute("SELECT COUNT(*) FROM songs")
    return cur.fetchall()[0][0]

def artists_genre_occurrences():
    cur.execute("SELECT genres, COUNT(genres) FROM artists GROUP BY genres ORDER BY COUNT(genres) DESC")
    return cur.fetchall()

def get_genre_predictions_from_db(song_id):
    cur.execute("SELECT * FROM song_genre_predictions WHERE id=%s", (song_id,))
    return cur.fetchall()

def get_songs_of_artist_from_db(artist_id):
    cur.execute("SELECT * FROM songs WHERE artist_id=%s", (artist_id,))
    return cur.fetchall()