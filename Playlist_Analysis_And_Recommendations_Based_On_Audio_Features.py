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

client_id = '4de970f6c75349e8a2006f4ab92bc13d'
client_secret= '95d83665a4b748d4ae3da433c00f4737'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

playlist_link = "https://open.spotify.com/playlist/5U5NTDZO124ou257m6780o?si=7e2d285331e74db8"
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

#playlist_data.info()
#playlist_data.head()

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

#playlist_data.head(30)

# Checks for any duplicates
#duplicates = playlist_data['id'].duplicated()
#duplicate_songs = playlist_data[duplicates]
#if len(duplicate_songs) == 0:
    #print("There are no duplicate songs in the playlist.")
#else:
    #for index, row in duplicate_songs.iterrows():
        #print(row)

        

        
        
# DATA ANALYSIS AND GRAPHICAL VISUALIZATIONS      
        
# Identifying the top genres
genre_counts = playlist_data["track_artist_genres"].value_counts()
#print(genre_counts) # The results show repeating genres within the lists 

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
#print(genres_in_order)

top10genres = dict(list(genres_in_order.items())[:10])

# Plot the genre counts as a horizontal bar graph
plt.barh(list(top10genres.keys()), list(top10genres.values()))
plt.xlabel("Genre Count")
plt.ylabel("Genre")
plt.title("Top 10 Genres in the Playlist")
plt.show()

# Finding the top albums
album_counts = playlist_data["track_album"].value_counts()
#print(album_counts)

# Graphing the top 5 albums
top_albums = album_counts.head()
top_albums.plot(kind = 'barh')
plt.title('Top 5 Albums in the Playlist')
plt.xlabel('Count')
plt.ylabel('Album')
plt.show()

# Finding the average of each column from audio data
columns_to_average = ['danceability', 'energy', 'speechiness',
                      'acousticness', 'instrumentalness', 'liveness', 'valence']

means = playlist_data[columns_to_average].mean()

#print("Mean values for each section:")
#print(means)

# plotting the mean for each audio feature column
audio_plot = plt.figure(figsize=(20, 20))
colors = ['green', 'blue', 'red', 'orange', 'pink', 'olive', 'cyan', 'purple', 'peachpuff', 'crimson', 'lime']

for i in range (7):
    plt.bar(columns_to_average[i], means[i], color=colors[i])
plt.title('Average Audio Features', fontsize=16)
plt.xlabel('Audio Features', fontsize = 14)
plt.ylabel('Average Value', fontsize=14)
plt.show()

# Finding the top artists
artist_count = playlist_data['track_artist'].value_counts()

artist_plot = plt.figure(figsize=(20, 20))
artist_count.plot(kind = 'bar', color = 'red')
plt.title('Frequency of Artists', fontsize = 16)
plt.xlabel('Artists', fontsize = 14)
plt.ylabel('Number of Songs', fontsize = 14)
plt.show()





# PART ONE OF RECOMMENDATION ENGINE: FINDING THE TOP 30 SONGS THAT HAVE THE MOST SIMILAR AUDIO FEATURES TO THE SONGS FROM A POOL

# Second dataset from Kaggle
pool_songs = pd.read_csv('spotify_songs.csv')
#pool_songs.head()
#pool_songs.info()

# Clean datasets so the same types of features are compared between the two playlists

playlist_data = playlist_data.drop('track_artist_popularity', axis = 1)
playlist_data = playlist_data.drop('track_album', axis = 1)
playlist_data = playlist_data.drop('track_artist_genres', axis = 1)

pool_songs.drop_duplicates(subset=['track_name', 'track_artist'], keep='first', inplace=True)
pool_songs = pool_songs.drop(columns = ["track_popularity", "track_album_id", "track_album_name", "playlist_genre", "track_album_release_date", "playlist_name", "playlist_id", "playlist_subgenre", "duration_ms", "language"])
pool_songs = pool_songs.rename(columns={"track_id":"id"})
lyric_column = pool_songs.pop("lyrics") # save lyrics later on for lyrical filtering 

#pool_songs.head()

# Since the audio features of the songs in both datasets will be compared to each other, merge pool_songs and playlist_data into one dataframe to appropriately scale the numerical values using min-max normalization; it doesn't make sense to compare scaled data from separate dataframes in this case.
merge_df = pd.concat([playlist_data, pool_songs], axis=0, ignore_index = True)
#merge_df.head(99)

# One-hot encoding for categorical data (key column)
key_OHE = pd.get_dummies(merge_df.key, prefix='key')

# Min-max normalization for numerical values
scaled_attributes = MinMaxScaler().fit_transform([
    merge_df['danceability'].values,
    merge_df['energy'].values,
    merge_df['loudness'].values,
    merge_df['speechiness'].values,
    merge_df['acousticness'].values,
    merge_df['instrumentalness'].values,
    merge_df['liveness'].values,
    merge_df['valence'].values,
    merge_df['tempo'].values
])

# alter dataframe
merge_df[['danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness','valence', 'tempo']] = scaled_attributes.T
merge_df = merge_df.drop('key', axis = 1)
merge_df = merge_df.join(key_OHE)
#merge_df.head()

# separate the merged dataframe back to separate songs from playlist and pool
playlist_data = merge_df.iloc[:97]
pool_songs = merge_df.iloc[97:]
playlist_data.reset_index(drop=True, inplace=True)
pool_songs.reset_index(drop=True, inplace=True)
pool_songs['lyrics'] = lyric_column
#pool_songs.head()

# Remove songs from pool_songs that are already in playlist_data
pool_songs = pool_songs[~pool_songs['id'].isin(playlist_data['id'].values)]
backup = (pool_songs['track_name'].isin(playlist_data['track_name'].values)) & (pool_songs['track_artist'].isin(playlist_data['track_artist'].values))
pool_songs = pool_songs[~backup]

# Create a matrix of cosine similarity scores in which the rows represent the songs from pool_songs and the columns represent songs from playlist_data.
cos_sim_matrix = cosine_similarity(pool_songs.drop(columns=['id', 'track_name', 'track_artist', 'lyrics']), playlist_data.drop(columns=['id', 'track_name', 'track_artist']))
#print(cos_sim_matrix)
#print(cos_sim_matrix.shape)

# Each song in pool_songs is compared to every song in playlist_data. For each song in pool_songs, i.e. each row, keep the maximum similarity score
sim_scores = cos_sim_matrix.max(axis=1)  

# Create a new column in pool_songs containing the similarity scores 
pool_songs['similarity_score'] = sim_scores

# Sort based on highest similarity scores
sorted_pool_songs = pool_songs.sort_values(by='similarity_score', ascending=False)

# Choose top 30 songs to recommend
top_30_audio_recs = sorted_pool_songs.head(30)
top_30_audio_recs

# Check: Compare the first recommendation to the song "Difficult" by Gracie Abrams in my playlist; check similarity score
#check1 = top_30_recs.iloc[0:1].copy()
#check2 = playlist_data.iloc[93:94].copy()
#check_cos = cosine_similarity(check2.drop(columns=['id','track_name', 'track_artist']), check1.drop(columns=['id','track_name', 'track_artist', 'similarity_score', 'lyrics']))
#print(check_cos)

# Save top 30 songs based on audio features as csv
#from IPython.display import FileLink, FileLinks
#top30_audio_recs = top_30_audio_recs.to_csv('Top30_audio_recs.csv', index = False)
#FileLink('C:/Users/kristinekong/Desktop/Top30audio_recs.csv')
