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
playlist_data = playlist_data.drop(columns = ["mode", "type", "id", "uri", "track_href", "analysis_url", "duration_ms", "time_signature"])
playlist_data.head()

# Checks for any duplicates
duplicates = playlist_data['track_name'].duplicated()
duplicate_songs = playlist_data[duplicates]
if len(duplicate_songs) == 0:
    print("There are no duplicate songs in the playlist.")
else:
    for index, row in duplicate_songs.iterrows():
        print(row)

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



# finding the average of each column from audio data
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

artist_count = playlist_data['track_artist'].value_counts()

artist_plot = plt.figure(figsize=(20, 20))
artist_count.plot(kind = 'bar', color = 'red')
plt.title('Frequency of Artists', fontsize = 16)
plt.xlabel('Artists', fontsize = 14)
plt.ylabel('Number of Songs', fontsize = 14)





# AFTER DATA ANALYSIS + VISUALIZATION, PREPARE DATAFRAME FOR RECOMMENDATION MACHINE (ALTER DATAFRAME)

# one hot encoding for categorical variables
artist_OHE = pd.get_dummies(playlist_data.track_artist)
album_OHE = pd.get_dummies(playlist_data.track_album)
key_OHE = pd.get_dummies(playlist_data.key)

# max-min normalization for numerical values
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

# alter dataframe
playlist_data[['danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness','valence', 'tempo']] = scaled_attributes.T
playlist_data = playlist_data.drop('track_name', axis = 1)
playlist_data = playlist_data.drop('track_artist_popularity', axis = 1)
playlist_data = playlist_data.drop('key', axis = 1)
playlist_data = playlist_data.drop('track_artist', axis = 1)
playlist_data = playlist_data.drop('track_album', axis = 1)
playlist_data = playlist_data.join(artist_OHE)
playlist_data = playlist_data.join(album_OHE)
playlist_data = playlist_data.join(key_OHE)
playlist_data.drop('track_artist_genres', 1).join(playlist_data.track_artist_genres.str.join('|').str.get_dummies()) # OHE for genre (different because values were in lists)
playlist_data.head()
playlist_data.info()

