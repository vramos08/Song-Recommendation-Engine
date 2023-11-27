#The purpose of this script is to clean the dataset
#Since we are using content-based filtering, we will be taking lyrics of the dataset and obtaining frequent words using the TF-IDF statistic. 
#Then we will use cosine similarity to compare the current playlist to our TF-IDF statistic to recommend songs.


import pandas as pd
import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



songs = pd.read_csv('songs.csv')
#Extends the width of the column so we can see the actual lyrics.
pd.set_option('display.max_colwidth', 1000)
#Cleans up the beginning of the lyrics portion as it does not include the actual lyrics to the song/
songs['Lyrics'] = songs['Lyrics'].apply(lambda x: x.split("Lyrics", 1)[-1].lstrip())
#We also see \n present in the lyrics which indicates a new line but we will be replacing it with a space.
songs['Lyrics'] = songs['Lyrics'].str.replace(r'\n', ' ')



#Used for content-based filtering (Work in progress)

#TF-IDF is used to calculate the originality of a word by comparing the number of times the word appears in a document
#with the number of documents the word appears in. This means that we are calculating the frequency of the word. 
tfidf = TfidfVectorizer(analyzer='word', stop_words='english')
lyrics_matrix = tfidf.fit_transform(songs['Lyrics'])
#Content-based filtering uses cosine similarity for recommendation
cosine_similarities = cosine_similarity(lyrics_matrix) 
#Similar words will be stored in a dictionary which we will then use to recommend songs.
similarities = {}




songs.head()