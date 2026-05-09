# Student ID- F415563
# Below i have imported pandas,numpy,matplotlib.pyplot and seaborn library.
# Pandas library help us to handle csv files efficiently and process the data in better way.
# Numpy library help us to handle large data in a better way. It works best fast with large dataset.
# Matplotlib.pyplot we have used here as it allows us to create a better visualization and plots.
# We have called seaborn library as well because it is good for statical plots, default themes and mostly it works well with pandas.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Here by using the pandas library in Python we have extracted the data using the file path. 
# pd.read_csv is used to read a CSV (Comma-Separated Values) file and converts it into a DataFrame.
# Below data was saved in the mentioned path in .csv format.
# we will create a dataframe named dfsongs after extracting the csv file.

dfSongs = pd.read_csv('/Users/shaileshmishra1422/Downloads/songs_normalize.csv')
dfSongs

# As we can see after reading the .csv file we have 2000 rows and 18 columns with the song data in dfsongs.
# We will be using this data to create our coursework
# As asked in the coursework , we have renamed the column duration_ms to duration.

dfSongs.rename(columns={'duration_ms' :'duration'}, inplace = True)
dfSongs

# After making the changes we can see that duration_ms has been changed to duration.
# Below we have changed the duration from milliseconds to seconds, rounding to the nearest whole number.

dfSongs['duration'] =(dfSongs['duration'] /1000).round().astype(int)
dfSongs 

# As per the requirement we have filtered the songs with the popularity value greater than 50, ensuring focus on widely recognised tracks, 
# Filtered the song with the speechiness values between 0.33 and 0.66 and finally songs with danceability values greater than 0.20.

dfSongs = dfSongs[(dfSongs['popularity'] > 50) & 
            (dfSongs['speechiness'].between(0.33, 0.66)) & 
            (dfSongs['danceability'] > 0.20)]
filteredSongs = dfSongs
filteredSongs

# As we can see after filtering and cleaning the data we are left with 82 rows and 18 columns.
# Here we have downloaded the filtered data in csv format and named it as filtered_Songs.csv using the below codes.

filteredSongs.to_csv('filtered_Songs.csv', index=False)

# Reads the CSV file of songs.
# Below we have called the Pandas Library used for working with CSV files.

import pandas as pd

# Here we have specified the file path which  sets the location of a CSV file, filtered_Songs.csv, in a variable called file_path. 
# Using this we can manage the file location.
# pd.read_csv() is used to load the CSV file into a pandas DataFrame named filtered_Songs. 
# We have organised this dataframe in rows and columns.

file_path = '/Users/shaileshmishra1422/Downloads/filtered_Songs.csv'
filtered_Songs = pd.read_csv('/Users/shaileshmishra1422/Downloads/filtered_Songs.csv')

# We have used  the below codes to display first five rows of the data and details about dataset.
filtered_Songs.head(), filtered_Songs.info()

# Below we have called the pandas library again and also imported sqlite3.
# We will be creating a SQL database names CWDatabase.db

import pandas as pd
import sqlite3

# Loading the CSV file
songs_df = pd.read_csv('/Users/shaileshmishra1422/Downloads/filtered_Songs.csv')

# Connecting to a new database (creating it if it doesn't exist)
connection = sqlite3.connect('CWDatabase.db')
c = connection.cursor()

# Dropping the tables if they exist (for creating new ones)
c.execute("DROP TABLE IF EXISTS song;")
c.execute("DROP TABLE IF EXISTS genre;")
c.execute("DROP TABLE IF EXISTS artist;")
c.execute("DROP TABLE IF EXISTS song_genre;")

# Genre table
c.execute("""
    CREATE TABLE genre (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Genre VARCHAR(250) UNIQUE
    );
""")

# Artist table
c.execute("""
    CREATE TABLE artist (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name VARCHAR(250) UNIQUE
    );
""")

# Song table
c.execute("""
    CREATE TABLE song (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Song VARCHAR(250),
        Duration INTEGER,
        Explicit BOOLEAN,
        Year INTEGER,
        Popularity INTEGER,
        Danceability REAL,
        Speechiness REAL,
        Artist INTEGER,
        FOREIGN KEY (Artist) REFERENCES artist(ID)
    );
""")

# song-genre table
c.execute("""
    CREATE TABLE song_genre (
        SongID INTEGER,
        GenreID INTEGER,
        FOREIGN KEY (SongID) REFERENCES song(ID),
        FOREIGN KEY (GenreID) REFERENCES genre(ID)
    );
""")

# Inserting various genres into the genre table
genres = set(genre.strip() for sublist in songs_df['genre'].str.split(',') for genre in sublist)
for genre in genres:
    c.execute("INSERT OR IGNORE INTO genre (Genre) VALUES (?);", (genre,))

# Inserting vaarious artists into the artist table
artists = songs_df['artist'].unique()
for artist in artists:
    c.execute("INSERT OR IGNORE INTO artist (Name) VALUES (?);", (artist,))

# Inserting songs into the song table and connecting genres to them
for _, row in songs_df.iterrows():
    # Insert a song and get its ID
    c.execute("""
        INSERT INTO song (Song, Duration, Explicit, Year, Popularity, Danceability, Speechiness, Artist)
        VALUES (?, ?, ?, ?, ?, ?, ?, (SELECT ID FROM artist WHERE Name = ?));
    """, (row['song'], row['duration'], row['explicit'], row['year'], row['popularity'], 
          row['danceability'], row['speechiness'], row['artist']))
    song_id = c.lastrowid

    # Linking songs to genres
    song_genres = [g.strip() for g in row['genre'].split(',')]
    for genre in song_genres:
        c.execute("""
            INSERT INTO song_genre (SongID, GenreID)
            VALUES (?, (SELECT ID FROM genre WHERE Genre = ?));
        """, (song_id, genre))

connection.commit()
connection.close()

print("Database populated successfully!")
