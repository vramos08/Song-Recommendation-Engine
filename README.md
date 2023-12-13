# Song-Recommendation-Engine
This project aims to replicate the "Spotify Wrapped" feature which visualizes the user's top genre, 5 artists, and albums. We also aim to create a personalized recommendation playlist from a separate playlist that contains various artists and genres.

# Data Extraction
We accessed the playlist data using Spotify Web API and the spotipy library. It is important to first make an app through the Web API and provide the "client id" and "client secret" for this code to run. A data frame was created which extracted the track audio features, name, artists, genre, popularity, and album. A total of 97 rows and 23 columns were created for this data frame.

# Data Analysis and Visualization
A total of 3 libraries were used for this section, excluding spotipy. The main library used was Pillow, which gave us access to the image processing, followed by IO (BytesIO) and Requests, to be able to access the image URL, process the URL into pixels, and store it as an image. For this section, two data frames were created including all the album and artist information. Specifically, we wanted to access the name of the album/artist and the URL associated with the cover image. We then found the top 5 albums and artist and stored each of their corresponding URLs in Pillows images. Using Pillow's resize( ), text ( ), Image.new( ), and paste( ), we created two different background and coordinated the images of the top albums/artists so that it resembles the wrapped feature. We also found a template and photoshopped it so that it displayed the information we had access to. As a result, three different images have been created, one for the top 5 albums with the album covers, the top 5 artists and their covers, and a mixture of the two including the top genre and an image of only the top artist.



How to Run: 
1. The file Playlist_Analysis_And_Recommendations_Based_On_Audio_Features.py should first be run with the spotify_songs.csv installed. This would give you the dataset seen in Top30_audio_recs.csv (the top 30 song recommendations based on audio features). 
2. The file spotifyTemplate.jpg should be downloaded before running the visualization_wrapped_feature.py file. 
3. LyricDataCleaning.py should be run last with spotify_songs.csv and Top30_audio_recs.csv downloaded. This will return LyricRecommendation.csv. 
