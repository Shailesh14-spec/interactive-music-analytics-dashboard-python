# Student ID- F415563
# Here we have tried to generate artist popularity across different genres.
# Results are visible in table format as well as a bar chart format.
# We can get the results once we will enter the artist name in the box.

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate  # Importing tabulate for better table formatting

def display_artist_statistics(artist_name, conn):
    """
    Display the popularity statistics of the given artist across genres and overall genre popularity.

    Parameters:
        artist_name (str): The name of the artist to analyze.
        conn (sqlite3.Connection): The database connection object.
    """
    cursor = conn.cursor()

    # Validate if the artist exists
    query = "SELECT ID FROM artist WHERE LOWER(Name) = LOWER(?);"
    cursor.execute(query, (artist_name,))
    artist_result = cursor.fetchone()

    if not artist_result:
        print(f"No data found for the artist '{artist_name}'.")
        return

    artist_id = artist_result[0]

    # Fetch artist statistics
    query = """
        SELECT g.Genre, 
               AVG(s.Popularity) AS ArtistPopularity, 
               (SELECT AVG(s2.Popularity)
                FROM song s2
                JOIN song_genre sg2 ON s2.ID = sg2.SongID
                WHERE sg2.GenreID = sg.GenreID) AS OverallGenrePopularity
        FROM song s
        JOIN song_genre sg ON s.ID = sg.SongID
        JOIN genre g ON sg.GenreID = g.ID
        WHERE s.Artist = ?
        GROUP BY sg.GenreID;
    """
    cursor.execute(query, (artist_id,))
    artist_data = cursor.fetchall()

    if not artist_data:
        print(f"No data available for the artist '{artist_name}'.")
        return

    # Convert data to a DataFrame for display and analysis
    df = pd.DataFrame(artist_data, columns=["Genre", "ArtistPopularity", "OverallGenrePopularity"])
    df["AboveAverage"] = df["ArtistPopularity"] > df["OverallGenrePopularity"]

    # Display the results in a tabular format using tabulate with grid style
    print(f"\nPopularity Table for {artist_name}:\n")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))  # Using grid format for better table lines

    # Plot results
    genres = df["Genre"]
    artist_popularity = df["ArtistPopularity"]
    overall_popularity = df["OverallGenrePopularity"]
    x = range(len(genres))

    plt.figure(figsize=(10, 6))
    plt.bar(x, artist_popularity, width=0.4, label=f"{artist_name} Popularity", align="center")
    plt.bar(x, overall_popularity, width=0.4, label="Overall Genre Popularity", align="edge")

    plt.xlabel("Genres")
    plt.ylabel("Popularity")
    plt.title(f"Popularity of {artist_name} Across Genres")
    plt.xticks(x, genres, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    """
    Main program to prompt the user for an artist's name and display their statistics.
    """
    print("Artist Popularity Analysis")
    artist_name = input("Enter the artist's name: ").strip()

    # Connect to the database
    conn = sqlite3.connect("CWDatabase.db")
    try:
        display_artist_statistics(artist_name, conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
