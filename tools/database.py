def create_tables(cur):
    try:
        print('Database relations are being establishing...')

        cur.execute("""CREATE TABLE IF NOT EXISTS artists (
                        id text NOT NULL,
                        name text NOT NULL,
                        genres text[] NOT NULL,
                        popularity int NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (id, name)
                        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS albums (
                        id text NOT NULL,
                        name text NOT NULL,
                        total_tracks int NOT NULL,
                        artist_id text NOT NULL,
                        artist_name text NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (id, name)
                        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS songs (
                        id text NOT NULL,
                        name text NOT NULL,
                        acousticness float NOT NULL,
                        instrumentalness float NOT NULL,
                        valence float NOT NULL,
                        loudness float NOT NULL,
                        energy float NOT NULL,
                        liveness float NOT NULL,
                        danceability float NOT NULL,
                        tempo float NOT NULL,
                        speechiness float NOT NULL,
                        mode int NOT NULL,
                        duration_ms int NOT NULL,
                        time_signature int NOT NULL,
                        key int NOT NULL,
                        artist_id text NOT NULL,
                        artist_name text NOT NULL,
                        album_id text NOT NULL,
                        album_name text NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (id, name)
                        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS combinated_genres (
                        name text NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (name)
                        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS song_genre_predictions (
                        id text NOT NULL,
                        name text NOT NULL,
                        r_b float NOT NULL,
                        rap float NOT NULL,
                        electronic float NOT NULL,
                        rock float NOT NULL,
                        new_age float NOT NULL,
                        classical float NOT NULL,
                        reggae float NOT NULL,
                        blues float NOT NULL,
                        country float NOT NULL,
                        world float NOT NULL,
                        folk float NOT NULL,
                        easy_listening float NOT NULL,
                        jazz float NOT NULL,
                        vocal float NOT NULL,
                        punk float NOT NULL,
                        alternative float NOT NULL,
                        pop float NOT NULL,
                        heavy_metal float NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (id)
                        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS recommendation_results (
                        id SERIAL NOT NULL,
                        song1_id text NOT NULL,
                        song1_feedback bool NOT NULL,
                        song2_id text NOT NULL,
                        song2_feedback bool NOT NULL,
                        song3_id text NOT NULL,
                        song3_feedback bool NOT NULL,
                        song4_id text NOT NULL,
                        song4_feedback bool NOT NULL,
                        song5_id text NOT NULL,
                        song5_feedback bool NOT NULL,
                        song6_id text NOT NULL,
                        song6_feedback bool NOT NULL,
                        song7_id text NOT NULL,
                        song7_feedback bool NOT NULL,
                        song8_id text NOT NULL,
                        song8_feedback bool NOT NULL,
                        song9_id text NOT NULL,
                        song9_feedback bool NOT NULL,
                        song10_id text NOT NULL,
                        song10_feedback bool NOT NULL,
                        age_group text NOT NULL,
                        openness float NOT NULL,
                        conscientiousness float NOT NULL,
                        extraversion float NOT NULL,
                        agreeableness float NOT NULL,
                        neuroticism float NOT NULL,
                        r_b float NOT NULL,
                        rap float NOT NULL,
                        electronic float NOT NULL,
                        rock float NOT NULL,
                        new_age float NOT NULL,
                        classical float NOT NULL,
                        reggae float NOT NULL,
                        blues float NOT NULL,
                        country float NOT NULL,
                        world float NOT NULL,
                        folk float NOT NULL,
                        easy_listening float NOT NULL,
                        jazz float NOT NULL,
                        vocal float NOT NULL,
                        punk float NOT NULL,
                        alternative float NOT NULL,
                        pop float NOT NULL,
                        heavy_metal float NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (id)
                        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS genre_suggestions (
                        id SERIAL NOT NULL,
                        recommendation_id int NOT NULL,
                        r_b int NOT NULL,
                        rap int NOT NULL,
                        electronic int NOT NULL,
                        rock int NOT NULL,
                        new_age int NOT NULL,
                        classical int NOT NULL,
                        reggae int NOT NULL,
                        blues int NOT NULL,
                        country int NOT NULL,
                        world int NOT NULL,
                        folk int NOT NULL,
                        easy_listening int NOT NULL,
                        jazz int NOT NULL,
                        vocal int NOT NULL,
                        punk int NOT NULL,
                        alternative int NOT NULL,
                        pop int NOT NULL,
                        heavy_metal int NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (id)
                        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS song_genre_suggestion (
                        id SERIAL NOT NULL,
                        song_id text NOT NULL,
                        genre text NOT NULL,
                        created_at timestamp NOT NULL,
                        PRIMARY KEY (id)
                        );""")

        print('Database relations successfully established!')
    
    except Exception as e:
        print('Database relation generator ERROR!')
        print(e)