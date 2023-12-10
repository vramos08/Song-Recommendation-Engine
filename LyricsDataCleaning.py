#The purpose of this script is to clean the dataset
#Since we are using content-based filtering, we will be taking lyrics of the dataset and obtaining frequent words using the TF-IDF statistic. 
#Then we will use cosine similarity to compare the current playlist to our TF-IDF statistic to recommend songs.


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import matplotlib.pyplot as plt


songs = pd.read_csv('spotify_songs.csv')
#There are non-english songs in the playlist, we will be filtering those songs out.
#We are also going to sort the dataset by popularity with the most popular songs at the top.
filtered_songs = songs[songs['language'] == 'en']
sort_song = filtered_songs.sort_values(by='track_popularity', ascending=False)


#We are going to remove columns that are not relevant in lyric-based recommendation.
pd.set_option('display.max_colwidth', 100)
columns_to_remove = [
    'track_album_id', 'track_album_name', 'track_album_release_date',
    'playlist_id', 'mode', 'speechiness', 'acousticness',
    'instrumentalness', 'duration_ms', 'playlist_subgenre', 'key', 'liveness',
    'valence', 'track_id', 'playlist_name', 'playlist_genre', 'energy',
    'loudness', 'tempo'
]
cleaned_song = sort_song.drop(columns=columns_to_remove, errors='ignore')
cleaned_song = cleaned_song.reset_index(drop=True)
print(cleaned_song.head(10000))



#Used for content-based filtering

playlist_data = pd.read_csv('AMS325SpotifyPlaylist.csv')
playlist_songs = playlist_data[['Track name', 'Artist name']].drop_duplicates()

selected_songs = []
#Number of songs we want to get from the original playlist.
target_songs = 10

# Keep selecting random songs until we get 10 songs that are also in cleaned_song
while len(selected_songs) < target_songs:
    # Randomly select a song from playlist_data
    random_song = playlist_songs.sample().iloc[0]
    
    # Check if the selected song is in cleaned_song
    if (cleaned_song['track_name'] == random_song['Track name']).any():
        selected_songs.append(random_song)

recommendations = []

#TF-IDF is used to calculate the originality of a word by comparing the number of times the word appears in a document
#with the number of documents the word appears in. This means that we are calculating the frequency of the word. 

tfidf = TfidfVectorizer(analyzer='word', stop_words='english', max_features = 500)
lyrics_matrix = tfidf.fit_transform(cleaned_song['lyrics'])
print(lyrics_matrix)

#Content-based filtering uses cosine similarity for recommendation
cosine_similarities = cosine_similarity(lyrics_matrix) 
#Similar words will be stored in a dictionary which we will then use to recommend songs.
similarities = {}

for i in range(len(cosine_similarities)):
    similar_index = cosine_similarities[i].argsort()[:-50:-1]
    similarities[cleaned_song['track_name'].iloc[i]] = [
        (cosine_similarities[i][x], cleaned_song['track_name'].iloc[x], cleaned_song['track_artist'].iloc[x]) for x in similar_index][1:]
    
#Function class to recommend a song based off cosine similarity
class ContentBasedRecommender:
    def __init__(self, matrix):
        self.matrix_similar = matrix

    def recommend(self, song, artist, number_of_songs):
        # Retrieve recommended songs excluding the original song (Meaning the original song cannot be part of the recommendation)
        recommended_songs = [
            (similarity, rec_song, rec_artist)
            for similarity, rec_song, rec_artist in self.matrix_similar[song]
            if rec_song != song
        ][:number_of_songs]

        # Prints the recommended songs for each of the songs we are randomly choosing.
        rec_items = len(recommended_songs)
        print(f'The {rec_items} recommended songs for {song} are:')
        for i in range(rec_items):
            print(f"Song {i + 1}:")
            print(f"{recommended_songs[i][1]} by {recommended_songs[i][2]} with {round(recommended_songs[i][0], 3)} similarity score")

        columns = ['Similarity', 'Recommended Song', 'Recommended Artist']
        df = pd.DataFrame(recommended_songs, columns=columns)
        df.insert(0, 'Original Song', song)
        df.insert(1, 'Original Artist', artist)

        return df

#Creates the recommendation using the ContentBasedRecommender function using the cosine similarity metric.
for song in selected_songs:
    recommendation = {
        'track_name': song['Track name'],
        'track_artist': song['Artist name'],
        'number_of_songs': 3
    }

    recommender = ContentBasedRecommender(similarities)
    recommendations_df = recommender.recommend(
        recommendation['track_name'],
        recommendation['track_artist'],
        recommendation['number_of_songs']
    )
    recommendations.append(recommendations_df)



all_recommendations_df = pd.concat(recommendations, ignore_index=True)
# Sorts the recommendation by similarity score
all_recommendations_df.sort_values(by='Similarity', ascending=False, inplace=True)
# get the top 30 most similar recommendation
top_30_recommendations_df = all_recommendations_df.head(30)
all_recommendations_df.to_csv('recommendations.csv', index=False)
    
# Displays the recommendations in a dataframe.
print(top_30_recommendations_df)
    
# A plot for similarity score
plt.figure(figsize=(10, 6))
plt.bar(top_30_recommendations_df['Recommended Song'], top_30_recommendations_df['Similarity'], color='blue')
plt.xlabel('Recommended Song')
plt.ylabel('Similarity Score')
plt.title('Top 30 Recommended Songs and Their Similarity Scores')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Display the plot
plt.show()

