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
    
    #Popularity of the track
    track_pop = track["track"]["popularity"]
    
    tracks_uri[track_name] = track_uri
    tracks_artist_name[track_name] = track["track"]["artists"][0]["name"]

    all_track_info = []

for track in tracks_uri:
    track_features = sp.audio_features(tracks_uri[track])[0]
    track_features['track_name'] = track
    track_features['track_artist'] = tracks_artist_name[track]
    all_track_info.append(track_features)


pd.DataFrame(all_track_info)

#finding the average of each column from audio data
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


