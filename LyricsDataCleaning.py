#The purpose of this script is to clean the dataset
#Since we are using content-based filtering, we will be taking lyrics of the dataset and obtaining frequent words using the TF-IDF statistic. 
#Then we will use cosine similarity to compare the current playlist to our TF-IDF statistic to recommend songs.


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt


songs = pd.read_csv('spotify_songs.csv')
#There are non-english songs in the playlist, we will be filtering those songs out.
#We are also going to sort the dataset by popularity with the most popular songs at the top.
filtered_songs = songs[songs['language'] == 'en']
sort_song = filtered_songs.sort_values(by='track_popularity', ascending=False)


#We are going to remove columns that are not relevant in lyric-based recommendation.
pd.set_option('display.max_colwidth', 100)
columns_to_remove = ['track_album_id', 'track_album_name', 'track_album_release_date',
    'playlist_id', 'mode', 'speechiness', 'acousticness',
    'instrumentalness', 'duration_ms', 'playlist_subgenre', 'key', 'liveness',
    'valence', 'track_id', 'playlist_name', 'playlist_genre', 'energy',
    'loudness', 'tempo']
cleaned_song = sort_song.drop(columns=columns_to_remove, errors='ignore')
cleaned_song = cleaned_song.reset_index(drop=True)
print(cleaned_song.head(10000))


#Used for content-based filtering
#Use the Top30_audio_recs dataset of 30 recommended songs based off of audio metrics.
playlist_songs = pd.read_csv('Top30_audio_recs.csv')

recommendations = []

#TF-IDF for lyric frequency analysis
#Limits the words to 500 words max to prevent overload and very long run times.
tfidf = TfidfVectorizer(analyzer='word', stop_words='english', max_features=500)
lyrics_matrix = tfidf.fit_transform(cleaned_song['lyrics'])
print(lyrics_matrix)

#Content-based filtering using cosine similarity
cosine_similarities = cosine_similarity(lyrics_matrix)
similarities = {}

#Obtained from content-based recommendation system (github link provided in resources)
for i in range(len(cosine_similarities)):
    similar_index = cosine_similarities[i].argsort()[:-50:-1]
    similarities[cleaned_song['track_name'].iloc[i]] = [
        (cosine_similarities[i][x], cleaned_song['track_name'].iloc[x], cleaned_song['track_artist'].iloc[x])
        for x in similar_index
    ][1:]


class ContentBasedRecommender:
    def __init__(self, matrix):
        self.matrix_similar = matrix

    def recommend(self, song, artist, number_of_songs):
        """Creates recommendations based off of the cosine similiarity score.
        Args:
        song(str): song name
        artist(str): artist name
        number_of_songs(int): number of songs to recommend
        
        returns(df): dataframe including original song, original artist, similarity score, recommended song, recommended artist
        """
        #Check if the key exists in the matrix_similar dictionary [Used chatgpt for coding help]
        if song in self.matrix_similar:
            #Retrieve recommended songs excluding the original song
            recommended_songs = [(similarity, rec_song, rec_artist)
            for similarity, rec_song, rec_artist in self.matrix_similar[song]
            #We want to make sure that songs with similarity scores equal to 1.0 are not included because that's the song itself.
            if rec_song != song and similarity < 1.0][:number_of_songs]
            #We are also slicing the recommended_songs to only return the top number_of_songs which in this case is one each. 

            #Prints the recommended songs for each of the songs
            rec_items = len(recommended_songs)
            print(f'The {rec_items} recommended songs for {song} are:')
            #Prints out 
            for i in range(rec_items):
                print(f"Song {i + 1}:")
                print(f"{recommended_songs[i][1]} by {recommended_songs[i][2]} with {round(recommended_songs[i][0], 3)} similarity score")

            columns = ['Similarity', 'Recommended Song', 'Recommended Artist']
            df = pd.DataFrame(recommended_songs, columns=columns)
            df.insert(0, 'Original Song', song)
            df.insert(1, 'Original Artist', artist)
            return df
        else:
            print(f"No recommendations available for {song}")
            
#Creates the recommendation using the ContentBasedRecommender function using the cosine similarity metric.
#Recommends a song for every row in playlist_songs(dataset of 30 recommended songs based off of audio metrics)
for _, row in playlist_songs.iterrows():
    recommendation = {'track_name': row['track_name'],
    'track_artist': row['track_artist'],
    'number_of_songs': 1}

    recommender = ContentBasedRecommender(similarities)
    recommendations_df = recommender.recommend(recommendation['track_name'], recommendation['track_artist'], recommendation['number_of_songs'])
    recommendations.append(recommendations_df)

#Concatenate all given recommendations into a single DataFrame
all_recommendations_df = pd.concat(recommendations, ignore_index=True)

#Sort the recommendation by similarity score
all_recommendations_df.sort_values(by='Similarity', ascending=False, inplace=True)
#Exports the recommendation as a csv file
all_recommendations_df.to_csv('LyricRecommendation.csv', index=False)

#Display the recommendations
print(all_recommendations_df.head(30))

#Plot based off of similiarity score and recommended song
plt.figure(figsize=(10, 6))
top_15_recommendations_df = all_recommendations_df.head(15)
plt.bar(top_15_recommendations_df['Recommended Song'], top_15_recommendations_df['Similarity'], color='blue')
plt.xlabel('Recommended Song')
plt.ylabel('Similarity Score')
plt.title('Top 15 Recommended Songs and Their Similarity Scores')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
