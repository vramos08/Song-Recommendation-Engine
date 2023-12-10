import sys
sys.path.append('/opt/anaconda3/lib/python3.9/site-packages')

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity


# RETRIEVING PERSONAL PLAYLIST FROM SPOTIFY API

client_id = 'b1e54575ac274390a4be1f2e837bb764'
client_secret= 'e21f4bb168eb48f1812e79cd46f06e83'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

playlist_link = "https://open.spotify.com/playlist/2VfkXEJGepE5U4rlCHdNX8?si=4672296c998f4010"
playlist_URI = playlist_link.split("/")[-1].split("?")[0]
track_uris = [x["track"]["uri"] for x in sp.playlist_tracks(playlist_URI)["items"]]

tracks_uri = {}
tracks_artist_name = {}
tracks_artist_pop = {}
tracks_artist_genres = {}
tracks_album = {}

for track in sp.playlist_tracks(playlist_URI)["items"]:
    #URI
    track_uri = track["track"]["uri"]
    
    #Track name
    track_name = track["track"]["name"]
    
    #Main Artist
    artist_uri = track["track"]["artists"][0]["uri"]
    artist_info = sp.artist(artist_uri)
    
    #Name, popularity, genre
    artist_name = track["track"]["artists"][0]["name"]
    artist_pop = artist_info["popularity"]
    artist_genres = artist_info["genres"]
    
    #Album
    album = track["track"]["album"]["name"]
    
    tracks_uri[track_name] = track_uri
    tracks_artist_name[track_name] = track["track"]["artists"][0]["name"]
    tracks_artist_pop[track_name] = artist_info["popularity"]
    tracks_artist_genres[track_name] = artist_info["genres"]
    tracks_album[track_name] = track["track"]["album"]["name"]

# Putting it all together for the dataframe
all_track_info = []

for track in tracks_uri:
    track_features = sp.audio_features(tracks_uri[track])[0]
    track_features['track_name'] = track
    track_features['track_artist'] = tracks_artist_name[track]
    
    track_features['track_artist_popularity'] = tracks_artist_pop[track]
    track_features['track_artist_genres'] = tracks_artist_genres[track]
    track_features['track_album'] = tracks_album[track]
    
    all_track_info.append(track_features)

playlist_data = pd.DataFrame(all_track_info)

playlist_data.info()
playlist_data.head()

# Clean data
# Drop unnecessary columns
playlist_data = playlist_data.drop(columns = ["type", "uri", "track_href", "analysis_url", "duration_ms", "time_signature"])

# Move id, track_name, and track_artist to the front
first_column = playlist_data.pop('id')
playlist_data.insert(0, 'id', first_column)
second_column = playlist_data.pop('track_name')
playlist_data.insert(1, 'track_name', second_column)
third_column = playlist_data.pop('track_artist')
playlist_data.insert(2, 'track_artist', third_column)

# Checks for any duplicates
duplicates = playlist_data['track_name'].duplicated()
duplicate_songs = playlist_data[duplicates]
if len(duplicate_songs) == 0:
    print("There are no duplicate songs in the playlist.")
else:
    for index, row in duplicate_songs.iterrows():
        print(row)



# DATA ANALYSIS AND VISUALIZATIONS 

# Identifying the top genres
genre_counts = playlist_data["track_artist_genres"].value_counts()
print(genre_counts) # The results show repeating genres within the lists 

# Splitting the lists such that each individual genre element is its own separate category
genre_count = {}
for arr in playlist_data['track_artist_genres']:
    for genre in arr:
        genre = genre.strip()
        if genre in genre_count:
            genre_count[genre] += 1
        else:
            genre_count[genre] = 1

# Sort genres from highest count to lowest count
genres_in_order = dict(sorted(genre_count.items(), key = lambda item: item[1], reverse=True))
print(genres_in_order)

# Plot the genre counts as a horizontal bar graph
plt.barh(list(genres_in_order.keys()), list(genres_in_order.values()))
plt.xlabel("Genre Count")
plt.ylabel("Genre")
plt.title("Genres in the Playlist")
plt.show()

# Finding the top albums
album_counts = playlist_data["track_album"].value_counts()
print(album_counts)

# Graphing the top 5 albums
top_albums = album_counts.head()
top_albums.plot(kind = 'barh')
plt.title('Top 5 Albums in the Playlist')
plt.xlabel('Count')
plt.ylabel('Album')
plt.show()

# Finding the average of each column from audio data
columns_to_average = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
                      'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

means = playlist_data[columns_to_average].mean()

print("Mean values for each section:")
print(means)
#plotting the mean for each column
audio_plot = plt.figure(figsize=(20, 20))
colors = ['green', 'blue', 'red', 'orange', 'pink', 'olive', 'cyan', 'purple', 'peachpuff', 'crimson', 'lime']

for i in range (11):
    plt.bar(columns_to_average[i], means[i], color=colors[i])
plt.title('Average Audio Features', fontsize=16)
plt.xlabel('Audio Features', fontsize = 14)
plt.ylabel('Average Value', fontsize=14)

# Finding the top artists
artist_count = playlist_data['track_artist'].value_counts()

artist_plot = plt.figure(figsize=(20, 20))
artist_count.plot(kind = 'bar', color = 'red')
plt.title('Frequency of Artists', fontsize = 16)
plt.xlabel('Artists', fontsize = 14)
plt.ylabel('Number of Songs', fontsize = 14)



# RECOMMENDATION ENGINE

# Prepare playlist_data
# One hot encoding for key (categorical variable)
key_OHE = pd.get_dummies(playlist_data.key, prefix='key')

# Max-min normalization for audio features (numerical variables)
scaled_attributes = MinMaxScaler().fit_transform([
    playlist_data['danceability'].values,
    playlist_data['energy'].values,
    playlist_data['loudness'].values,
    playlist_data['speechiness'].values,
    playlist_data['acousticness'].values,
    playlist_data['instrumentalness'].values,
    playlist_data['liveness'].values,
    playlist_data['valence'].values,
    playlist_data['tempo'].values
])

# Alter dataframe
playlist_data[['danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness','valence', 'tempo']] = scaled_attributes.T
playlist_data = playlist_data.drop('track_artist_popularity', axis = 1)
playlist_data = playlist_data.drop('track_album', axis = 1)
playlist_data = playlist_data.drop('track_artist_genres', axis = 1)
playlist_data = playlist_data.drop('key', axis = 1)
playlist_data = playlist_data.join(key_OHE)
playlist_data.head()

# PREPARING THE SECOND PLAYLIST- THE POOL OF SONGS WE ARE GOING TO RECOMMEND FROM

pool_songs = pd.read_csv('spotify_songs.csv')
pool_songs.info()
pool_songs.head()

# clean dataset so the same types of features are compared between the two playlists
pool_songs.drop_duplicates(subset=['track_name', 'track_artist'], keep='first', inplace=True) # some songs have different ids but are the same songs (have the same title and artist)
pool_songs = pool_songs.drop(columns = ["lyrics", "track_popularity", "track_album_id", "track_album_name", "playlist_genre", "track_album_release_date", "playlist_name", "playlist_id", "playlist_subgenre", "duration_ms", "language"])
pool_songs = pool_songs.rename(columns={"track_id":"id"})
pool_songs.head()

# One hot encoding for key
pool_key_OHE = pd.get_dummies(pool_songs.key, prefix='key')

# Max-min normalization for numerical values
pool_scaled_attributes = MinMaxScaler().fit_transform([
    pool_songs['danceability'].values,
    pool_songs['energy'].values,
    pool_songs['loudness'].values,
    pool_songs['speechiness'].values,
    pool_songs['acousticness'].values,
    pool_songs['instrumentalness'].values,
    pool_songs['liveness'].values,
    pool_songs['valence'].values,
    pool_songs['tempo'].values
])

# Alter dataframe
pool_songs[['danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness','valence', 'tempo']] = pool_scaled_attributes.T
pool_songs = pool_songs.drop('key', axis = 1)
pool_songs = pool_songs.join(pool_key_OHE)
pool_songs.head()

# GENERATING RECOMMENDATIONS USING COSINE SIMILARITY
# Remove songs from pool_songs that are already in playlist_data
pool_songs = pool_songs[~pool_songs['id'].isin(playlist_data['id'].values)]
backup = (pool_songs['track_name'].isin(playlist_data['track_name'].values)) & (pool_songs['track_artist'].isin(playlist_data['track_artist'].values))
pool_songs = pool_songs[~backup]

# Create a matrix of cosine similarity scores in which the rows represent the songs from pool_songs and the columns represent songs from playlist_data.
cos_sim_matrix = cosine_similarity(pool_songs.drop(columns=['id', 'track_name', 'track_artist']), playlist_data.drop(columns=['id', 'track_name', 'track_artist']))

# Each song in pool_song is compared to every song in playlist_data. For each song in pool_songs, i.e. each row, keep the maximum similarity score.
sim_scores = cos_sim_matrix.max(axis=1)

# Create a new column in pool_songs containing the similarity scores 
pool_songs['similarity_score'] = sim_scores

# Sort based on highest similarity scores
sorted_pool_songs = pool_songs.sort_values(by='similarity_score', ascending=False)

# Choose top 30 songs to recommend
top_30_recs = sorted_pool_songs.head(30)
top_30_recs

# CHECK: Compare the first recommendation to the song "Difficult" by Gracie Abrams in my playlist; check similarity score
check1 = top_30_recs.iloc[0:1].copy()
check2 = playlist_data.iloc[93:94].copy()
check_cos = cosine_similarity(check1.drop(columns=['id','track_name', 'track_artist', 'similarity_score']), check2.drop(columns=['id','track_name', 'track_artist']))
print(check_cos)
