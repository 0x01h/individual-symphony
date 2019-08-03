# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Albums(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    total_tracks = models.IntegerField()
    artist_id = models.TextField()
    artist_name = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'albums'
        unique_together = (('id', 'name'),)


class Artists(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    genres = models.TextField()  # This field type is a guess.
    popularity = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'artists'
        unique_together = (('id', 'name'),)


class CombinatedGenres(models.Model):
    name = models.TextField(primary_key=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'combinated_genres'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class GenreSuggestions(models.Model):
    recommendation_id = models.IntegerField()
    r_b = models.IntegerField()
    rap = models.IntegerField()
    electronic = models.IntegerField()
    rock = models.IntegerField()
    new_age = models.IntegerField()
    classical = models.IntegerField()
    reggae = models.IntegerField()
    blues = models.IntegerField()
    country = models.IntegerField()
    world = models.IntegerField()
    folk = models.IntegerField()
    easy_listening = models.IntegerField()
    jazz = models.IntegerField()
    vocal = models.IntegerField()
    punk = models.IntegerField()
    alternative = models.IntegerField()
    pop = models.IntegerField()
    heavy_metal = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'genre_suggestions'


class RecommendationResults(models.Model):
    song1_id = models.TextField()
    song1_feedback = models.BooleanField()
    song2_id = models.TextField()
    song2_feedback = models.BooleanField()
    song3_id = models.TextField()
    song3_feedback = models.BooleanField()
    song4_id = models.TextField()
    song4_feedback = models.BooleanField()
    song5_id = models.TextField()
    song5_feedback = models.BooleanField()
    song6_id = models.TextField()
    song6_feedback = models.BooleanField()
    song7_id = models.TextField()
    song7_feedback = models.BooleanField()
    song8_id = models.TextField()
    song8_feedback = models.BooleanField()
    song9_id = models.TextField()
    song9_feedback = models.BooleanField()
    song10_id = models.TextField()
    song10_feedback = models.BooleanField()
    age_group = models.TextField()
    openness = models.FloatField()
    conscientiousness = models.FloatField()
    extraversion = models.FloatField()
    agreeableness = models.FloatField()
    neuroticism = models.FloatField()
    r_b = models.FloatField()
    rap = models.FloatField()
    electronic = models.FloatField()
    rock = models.FloatField()
    new_age = models.FloatField()
    classical = models.FloatField()
    reggae = models.FloatField()
    blues = models.FloatField()
    country = models.FloatField()
    world = models.FloatField()
    folk = models.FloatField()
    easy_listening = models.FloatField()
    jazz = models.FloatField()
    vocal = models.FloatField()
    punk = models.FloatField()
    alternative = models.FloatField()
    pop = models.FloatField()
    heavy_metal = models.FloatField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'recommendation_results'


class SongGenrePredictions(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    r_b = models.FloatField()
    rap = models.FloatField()
    electronic = models.FloatField()
    rock = models.FloatField()
    new_age = models.FloatField()
    classical = models.FloatField()
    reggae = models.FloatField()
    blues = models.FloatField()
    country = models.FloatField()
    world = models.FloatField()
    folk = models.FloatField()
    easy_listening = models.FloatField()
    jazz = models.FloatField()
    vocal = models.FloatField()
    punk = models.FloatField()
    alternative = models.FloatField()
    pop = models.FloatField()
    heavy_metal = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'song_genre_predictions'


class SongGenreSuggestion(models.Model):
    song_id = models.TextField()
    genre = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'song_genre_suggestion'


class Songs(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    valence = models.FloatField()
    loudness = models.FloatField()
    energy = models.FloatField()
    liveness = models.FloatField()
    danceability = models.FloatField()
    tempo = models.FloatField()
    speechiness = models.FloatField()
    mode = models.IntegerField()
    duration_ms = models.IntegerField()
    time_signature = models.IntegerField()
    key = models.IntegerField()
    artist_id = models.TextField()
    artist_name = models.TextField()
    album_id = models.TextField()
    album_name = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'songs'
        unique_together = (('id', 'name'),)
