import ast
import functions
import numpy as np
import pandas as pd
import random as rn
import tensorflow as tf

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from main import cur

inp_filename = '../datasets/labeled_songs.csv'
print('Start labeling.')
# functions.genre_song_label()  # Export to CSV all songs with genre labels.
print('Finish labeling.')
num_samples = functions.get_count_songs_from_db()
scaler = MinMaxScaler()

# One hot encoding to each class.
genre_to_ohe = {
  'r&b': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'rap': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'electronic': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'rock': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'new_age': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'classical': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'reggae': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'blues': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'country': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], \
  'world': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], \
  'folk': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], \
  'easy_listening': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], \
  'jazz': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], \
  'vocal': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], \
  'punk': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], \
  'alternative': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], \
  'pop': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], \
  'heavy_metal': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
}

# Map sub-genres to general genres.
# "alternative" will be dominant if sub-genres not mapped well.
genre_generalization = {
  'pop': 'pop', \
  'r&b': 'r&b', \
  'hardstyle': 'electronic', \
  'hollywood': 'easy_listening', \
  'grunge': 'heavy_metal', \
  'garage': 'rock', \
  'jazz': 'jazz', 'blues': 'blues', 'country': 'country', \
  'rock': 'rock', 'indie': 'rock', 'singer-songwriter': 'rock', 'lo-fi': 'rock', \
  'rap': 'rap', 'hip hop': 'rap', \
  'singing': 'vocal', 'vocal': 'vocal', 'choral': 'vocal', 'choir': 'vocal', 'opera': 'vocal', 'choro': 'folk', \
  'world': 'world', 'christian': 'world', \
  'new_age': 'new_age', 'ambient': 'new_age', \
  'metal': 'heavy_metal', 'punk': 'punk', \
  'classical': 'classical', 'orchestra': 'classical', 'broadway': 'classical', 'ensemble': 'classical', \
  'ska': 'reggae', 'reggae': 'reggae', 'fusion': 'reggae', 'funk': 'blues', 'soul': 'blues', \
  'outlaw': 'country', 'texas': 'country', \
  'house': 'electronic', 'tech': 'electronic', 'edm': 'electronic', 'trance': 'electronic', \
  'folk': 'folk', 'mexican': 'world', 'latin': 'world', 'bolero': 'folk', 'tango': 'folk', \
  'tropical': 'world', 'traditional': 'folk', 'flamenco': 'folk', \
  'electro': 'electronic', 'disco': 'electronic', \
  'soundtrack': 'easy_listening', 'downtempo': 'easy_listening', \
  'altenative rock': 'rock', 'emo': 'rock', 'surf': 'rock', \
  'hi-nrg': 'electronic', 'wave': 'electronic', 'violin': 'classical', 'dreamo': 'classical', \
  'dance': 'electronic', 'deep': 'electronic', \
  'anime': 'new_age', 'spanish': 'world', 'meditation': 'new_age', \
  'hardcore': 'punk', 'skate': 'punk', 'noise': 'punk', 'glam': 'heavy_metal', \
  'game music': 'easy_listening', 'movie': 'easy_listening', 'monastic': 'easy_listening', \
  'harmony': 'easy_listening', 'mambo': 'folk', 'melancholia': 'new_age', 'alternative': 'alternative', \
  'art': 'rock', 'brutal': 'heavy_metal', 'teen': 'pop', 'gospel': 'country', 'comedy': 'easy_listening'
}

labels = ['genre','id', 'name',
'acousticness', 'instrumentalness',	'valence', 'loudness', 'energy', 
'liveness', 'danceability', 'tempo', 'speechiness', 'mode', 'duration_ms', 'time_signature', 'key']

features = ['acousticness', 'instrumentalness',	'valence', 'loudness', 'energy', 
'liveness', 'danceability', 'tempo', 'speechiness', 'mode', 'time_signature', 'key']

num_inputs = len(features)
normalized_genres = []

# Skip first row, because it's header.
dataframe = pd.read_csv(inp_filename, names=labels, skiprows=1, nrows=num_samples, usecols=labels)
# dataframe = dataframe[dataframe['genre'].notnull()]  # Filter NULL genres.
# dataframe = dataframe[dataframe['genre'] != '[]']  # Filter NULL genres.

# If keyword not found, map to "alternative".
for genre in dataframe['genre']:
  found = False
  array_genres = ast.literal_eval(genre)

  for array_genre in array_genres:
    for key, value in genre_generalization.items():
      if (key in array_genre):
        normalized_genres.append(value)
        found = True
        break
        
    if (found):
      break

  if (not found):
    normalized_genres.append('alternative')

label_data = np.array(normalized_genres)

label_ohe_data = []
for data in label_data:
  for key, value in genre_to_ohe.items():  
    if (key == data):
      label_ohe_data.append(value)
      break

label_data = np.array(label_ohe_data)

dataframe = pd.read_csv(inp_filename, names=labels, skiprows=1, nrows=num_samples, usecols=features)
feature_data = dataframe.values

dataframe = pd.read_csv(inp_filename, names=labels, skiprows=1, nrows=num_samples, usecols=['id', 'name'])
song_info = dataframe.values

scaler.fit(feature_data)
scaler.transform(feature_data)

X_train, X_test, y_train, y_test = train_test_split(feature_data, label_data, test_size=0.1, random_state=rn.randint(0, 99))

model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(input_shape=(num_inputs, )),
  tf.keras.layers.Dense(64, activation=tf.nn.relu, kernel_initializer='random_uniform'),
  tf.keras.layers.Dense(128, activation=tf.nn.relu),
  tf.keras.layers.Dense(256, activation=tf.nn.relu),
  tf.keras.layers.Dense(512, activation=tf.nn.relu),
  tf.keras.layers.Dense(256, activation=tf.nn.relu),
  tf.keras.layers.Dense(128, activation=tf.nn.relu),
  tf.keras.layers.Dense(64, activation=tf.nn.relu),
  tf.keras.layers.Dropout(0.1),
  tf.keras.layers.Dense(18, activation=tf.nn.softmax)
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# model.fit(X_train, y_train, batch_size=512, epochs=50, validation_split=0.1)
# model.save("model.h5")

model = tf.keras.models.load_model('model.h5')

results = model.evaluate(X_test, y_test)

print(model.metrics_names, results)

"""
# Delete all old genre predictions and insert new ones.
cur.execute('DELETE FROM song_genre_predictions;')
for selected_num in range(0, len(feature_data)):
  print('Remaining number of predictions:', len(feature_data)-selected_num, end='\r')

  selected_candidate = np.array([feature_data[selected_num]])
  prediction = model.predict_classes(selected_candidate)
  prediction_probs = model.predict(selected_candidate)

  predict_dict = {}
  predict_dict['id'] = song_info[selected_num][0]
  predict_dict['name'] = song_info[selected_num][1]
  predict_dict['probs'] = prediction_probs

  functions.insert_predictions(predict_dict)

for _ in range(0, 100):
  selected_num = rn.randint(0, num_samples)
  selected_candidate = np.array([feature_data[selected_num]])

  print(selected_num)
  print(selected_candidate)

  prediction = model.predict_classes(selected_candidate)
  prediction_probs = model.predict(selected_candidate)

  print(prediction)
  print(prediction_probs)
"""

"""
for selected_num in range(0, len(feature_data)):
  print(selected_num)

  selected_candidate = np.array([feature_data[selected_num]])
  prediction = model.predict_classes(selected_candidate)
  prediction_probs = model.predict(selected_candidate)

  print(selected_candidate)
  print(prediction)

  predict_dict = {}
  predict_dict['id'] = song_info[selected_num][0]
  predict_dict['name'] = song_info[selected_num][1]
  predict_dict['probs'] = prediction_probs

  functions.insert_predictions(predict_dict)

  print(predict_dict)
  """
