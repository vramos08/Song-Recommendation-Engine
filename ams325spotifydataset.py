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

#these are for the visualization section
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

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
playlist_data = playlist_data.drop(columns = ["mode", "key", "type", "uri", "track_href", "analysis_url", "duration_ms", "time_signature"])
playlist_data.head()

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






#                                     Getting the albums/artists info
albums_info = {}

#loop through each track in the playlist
for track in sp.playlist_tracks(playlist_URI)["items"]:
    track_name = track["track"]["name"]
    album_name = track["track"]["album"]["name"]
    
    if album_name not in albums_info:
        album_info = sp.album(track["track"]["album"]["id"])
        albums_info[album_name] = album_info
    
#putting it all together for the dataframe
all_album_info = []

for album_name, album_info in albums_info.items():
    all_album_info.append(album_info)

# Create a DataFrame
album_data = pd.DataFrame(all_album_info)

#                         Making a DataFrame with only the album names and image
two_columns = ['name', 'images']
album_images = album_data[two_columns]

#getting the first part of the url only to generate the image url
album_images['images'] = album_images['images'].apply(lambda x: x[0]['url'] if x else None)




#artist info 
artists_info = {}
for track in sp.playlist_tracks(playlist_URI)["items"]:
    track_name = track["track"]["name"]
    artists = [artist["name"] for artist in track["track"]["artists"]]
    
    artist_name = artists[0]

    if artist_name not in artists_info:
        artist_info = sp.artist(track["track"]["artists"][0]["id"])
        artists_info[artist_name] = artist_info

#putting it all together for the dataframe
all_artist_info = []

for artist_name, artist_info in artists_info.items():
    all_artist_info.append(artist_info)

#create a dataFrame
artist_data = pd.DataFrame(all_artist_info)

#making a DataFrame with only the artist names and image
two_columns_artist = ['name', 'images']
artist_images = artist_data[two_columns_artist]

#getting the first part of the URL only to generate the image URL
artist_images['images'] = artist_images['images'].apply(lambda x: x[0]['url'] if x else None)





#                               FURTHER VISUALIZATION
#displaying the top 5 albums images
#                                   Your Top Albums
album1_name = top_albums.index[0]
image1_url = album_images.loc[album_images['name'] == album1_name, 'images'].values[0]
im1 = Image.open(BytesIO(requests.get(image1_url).content))

album2_name = top_albums.index[1]
image2_url = album_images.loc[album_images['name'] == album2_name, 'images'].values[0]
im2 = Image.open(BytesIO(requests.get(image2_url).content))

album3_name = top_albums.index[2]
image3_url = album_images.loc[album_images['name'] == album3_name, 'images'].values[0]
im3 = Image.open(BytesIO(requests.get(image3_url).content))

album4_name = top_albums.index[3]
image4_url = album_images.loc[album_images['name'] == album4_name, 'images'].values[0]
im4 = Image.open(BytesIO(requests.get(image4_url).content))

album5_name = top_albums.index[4]
image5_url = album_images.loc[album_images['name'] == album5_name, 'images'].values[0]
im5 = Image.open(BytesIO(requests.get(image5_url).content))

#creating a illicit green from iColorPallette
background = Image.new("RGB", (500, 700), (71, 249, 184))

#resizing the images to be small around 100by100
resize1 = im1.resize((100, 100), Image.ANTIALIAS) 
resize2 = im2.resize((100, 100), Image.ANTIALIAS) 
resize3 = im3.resize((100, 100), Image.ANTIALIAS) 
resize4 = im4.resize((100, 100), Image.ANTIALIAS) 
resize5 = im5.resize((100, 100), Image.ANTIALIAS)  

background.paste(resize1, (70, 100))
background.paste(resize2, (70, 220))
background.paste(resize3, (70, 340))
background.paste(resize4, (70, 460))
background.paste(resize5, (70, 580))

#This is the part for Your Top Albums
title = "Your Top Albums"
draw = ImageDraw.Draw(background)
font = ImageFont.truetype("arial.ttf", 25)
font1 = ImageFont.truetype("arial.ttf", 30 )
font2 = ImageFont.truetype("arial.ttf", 20)
font3 = ImageFont.truetype("arial.ttf", 16)
draw.text((10, 40), title, font=font, fill=(0, 0, 128))

#displaying the numebers
draw.text((20, 120), "#1", font=font1, fill=(0,0,128))
draw.text((20, 240), "#2", font=font1, fill=(0,0,128))
draw.text((20, 360), "#3", font=font1, fill=(0,0,128))
draw.text((20, 480), "#4", font=font1, fill=(0,0,128))
draw.text((20, 600), "#5", font=font1, fill=(0,0,128))

#displaying the title of the albums
draw.text((200, 130), resize1, font=font2, fill=(0,0,128))
draw.text((200, 250), resize2, font=font2, fill=(0,0,128))
draw.text((200, 370), resize3, font=font2, fill=(0,0,128))
draw.text((200, 490), resize4, font=font2, fill=(0,0,128))
draw.text((200, 610), resize5, font=font2, fill=(0,0,128))



#displaying the top 5 artists
#     Your Top Artists
top_artists = artist_count.head()

artist1_name = top_artists.index[0]
Aimage1_url = artist_images.loc[artist_images['name'] == artist1_name, 'images'].values[0]
im1_artist = Image.open(BytesIO(requests.get(Aimage1_url).content))

artist2_name = top_artists.index[1]
Aimage2_url = artist_images.loc[artist_images['name'] == artist2_name, 'images'].values[0]
im2_artist = Image.open(BytesIO(requests.get(Aimage2_url).content))

artist3_name = top_artists.index[2]
Aimage3_url = artist_images.loc[artist_images['name'] == artist3_name, 'images'].values[0]
im3_artist = Image.open(BytesIO(requests.get(Aimage3_url).content))

artist4_name = top_artists.index[3]
Aimage4_url = artist_images.loc[artist_images['name'] == artist4_name, 'images'].values[0]
im4_artist = Image.open(BytesIO(requests.get(Aimage4_url).content))

artist5_name = top_artists.index[4]
Aimage5_url = artist_images.loc[artist_images['name'] == artist5_name, 'images'].values[0]
im5_artist = Image.open(BytesIO(requests.get(Aimage5_url).content))

background2 = Image.new("RGB", (500, 700), (71, 249, 184))

#resizing the images to be small around 100by100
resize1a = im1_artist.resize((100, 100), Image.ANTIALIAS) 
resize2a = im2_artist.resize((100, 100), Image.ANTIALIAS) 
resize3a = im3_artist.resize((100, 100), Image.ANTIALIAS) 
resize4a = im4_artist.resize((100, 100), Image.ANTIALIAS) 
resize5a = im5_artist.resize((100, 100), Image.ANTIALIAS)  

background2.paste(resize1a, (70, 100))
background2.paste(resize2a, (70, 220))
background2.paste(resize3a, (70, 340))
background2.paste(resize4a, (70, 460))
background2.paste(resize5a, (70, 580))

#                                    This is the part for Your Top Artists
title2 = "Your Top Artists"
draw2 = ImageDraw.Draw(background2)
draw2.text((10, 40), title2, font=font, fill=(0, 0, 128))

#displaying the numebers
draw2.text((20, 120), "#1", font=font1, fill=(0,0,128))
draw2.text((20, 240), "#2", font=font1, fill=(0,0,128))
draw2.text((20, 360), "#3", font=font1, fill=(0,0,128))
draw2.text((20, 480), "#4", font=font1, fill=(0,0,128))
draw2.text((20, 600), "#5", font=font1, fill=(0,0,128))

#displaying the title of the songs
draw2.text((200, 130), resize1a, font=font2, fill=(0,0,128))
draw2.text((200, 250), resize2a, font=font2, fill=(0,0,128))
draw2.text((200, 370), resize3a, font=font2, fill=(0,0,128))
draw2.text((200, 490), resize4a, font=font2, fill=(0,0,128))
draw2.text((200, 610), resize5a, font=font2, fill=(0,0,128))



#this part will be used when taking the all in one card
image_combine = Image.open(r"C:\Users\viann\Pictures\SpotifyTemplate.jpg")
sizeAgain = im1.resize((300, 230), Image.ANTIALIAS)
together = image_combine.resize((500, 700))
together.paste(sizeAgain, (95,72))


#                THIS PART NEEDS TO GET FIXED


top_genre = genres_in_order.index[0]

# displaying the names 
draw_together = ImageDraw.Draw(together)
draw_together.text((60, 395), artist1_name, font=font3, fill=(0,0,0))
draw_together.text((60, 421), artist2_name, font=font3, fill=(0,0,0))
draw_together.text((60, 446), artist3_name, font=font3, fill=(0,0,0))
draw_together.text((60, 470), artist4_name, font=font3, fill=(0,0,0))
draw_together.text((60, 492), artist5_name, font=font3, fill=(0,0,0))

#displaying the album names
draw_together = ImageDraw.Draw(together)
draw_together.text((300, 395), album1_name, font=font3, fill=(0,0,0))
draw_together.text((300, 421), album1_name, font=font3, fill=(0,0,0))
draw_together.text((300, 446), album1_name, font=font3, fill=(0,0,0))
draw_together.text((300, 470), album1_name, font=font3, fill=(0,0,0))
draw_together.text((300, 492), album1_name, font=font3, fill=(0,0,0))

#displaying the genre
draw_together.text((280,550), top_genre, font=font1, fill=(0,0,0))
together.show()






# RECOMMENDATION ENGINE
# AFTER DATA ANALYSIS + VISUALIZATION, PREPARE DATAFRAME FOR RECOMMENDATION MACHINE (ALTER DATAFRAME)

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
playlist_data = playlist_data.drop('track_artist_popularity', axis = 1)
playlist_data = playlist_data.drop('track_album', axis = 1)
playlist_data = playlist_data.drop('track_artist_genres', axis = 1)
playlist_data.head()

# PREPARING THE SECOND PLAYLIST- THE POOL OF SONGS WE ARE GOING TO RECOMMEND FROM

pool_songs = pd.read_csv('spotify_songs.csv')
pool_songs.info()

# clean dataset so the same types of features are compared between the two playlists
pool_songs = pool_songs.drop(columns = ["lyrics", "track_popularity", "track_album_id", "track_album_name", "playlist_genre", "track_album_release_date", "playlist_name", "playlist_id", "playlist_subgenre", "duration_ms", "language", "key", "mode"])
pool_songs = pool_songs.rename(columns={"track_id":"id"})
pool_songs.head()

# max-min normalization for numerical values
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

# alter dataframe
pool_songs[['danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness','valence', 'tempo']] = pool_scaled_attributes.T
pool_songs.head()

# Remove songs from pool_songs that are already in playlist_data
pool_songs = pool_songs[~pool_songs['id'].isin(playlist_data['id'].values)]

# Create a matrix of cosine similarity scores in which the rows represent the songs from pool_songs and the columns represent songs from playlist_data.
cos_sim_matrix = cosine_similarity(t.drop(columns=['id', 'track_name', 'track_artist']), pool_songs.drop(columns=['id', 'track_name', 'track_artist']))

# Each song in pool_song is compared to every song in playlist_data. For each song in pool_songs, i.e. each row, keep the maximum similarity score.
sim_scores = cos_sim_matrix.max(axis=0)  

# Create a new column in pool_songs containing the similarity scores 
pool_songs['similarity_score'] = sim_scores

# Sort based on highest similarity scores
pool_songs = pool_songs.sort_values(by='similarity_score', ascending=False)

# Choose top 10 songs to recommend
top_recs = pool_songs.head(10)
top_recs
