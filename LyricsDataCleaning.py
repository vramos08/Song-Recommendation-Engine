#The purpose of this script is to clean the dataset
#Since we are using content-based filtering, we will be taking lyrics of the dataset and obtaining frequent words using the TF-IDF statistic. 
#Then we will use cosine similarity to compare the current playlist to our TF-IDF statistic to recommend songs.


import pandas as pd
import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



songs = pd.read_csv('spotify_songs.csv')

filtered_songs = songs[songs['language'] == 'en']
sort_song = filtered_songs.sort_values(by='track_popularity', ascending=False)
#TODO - Remove all of the songs in the test playlist from this data set


pd.set_option('display.max_colwidth', 100)
columns_to_remove = [
    'track_album_id', 'track_album_name', 'track_album_release_date',
    'playlist_id', 'mode', 'speechiness', 'acousticness',
    'instrumentalness', 'duration_ms', 'playlist_subgenre', 'key', 'liveness',
    'valence'
]
cleaned_song = sort_song.drop(columns=columns_to_remove, errors='ignore')


#Filter song to top 10000 songs
pd.set_option('display.max_rows', 20)
cleaned_song.head(10000)



#Used for content-based filtering (Work in progress)

#TF-IDF is used to calculate the originality of a word by comparing the number of times the word appears in a document
#with the number of documents the word appears in. This means that we are calculating the frequency of the word. 

tfidf = TfidfVectorizer(analyzer='word', stop_words='english')
lyrics_matrix = tfidf.fit_transform(songs['Lyrics'])

#Content-based filtering uses cosine similarity for recommendation
cosine_similarities = cosine_similarity(lyrics_matrix) 
#Similar words will be stored in a dictionary which we will then use to recommend songs.
similarities = {}



#How I will approach the recommendation of the songs.
#Lyrical recommendations requires a specific song to compare lyrics to.
#As a result, I will be taking the the 10 most popular song from the most popular genre and recommending 3 songs each.
#Each song will also have a similarity score.
#Then I will sort the songs based on how often they appeared in the recommendation and they will be recommended.
