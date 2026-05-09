# Student ID- F415563
# Below codes we have used to display genre statistics which includes average danceability, total songs, and average popularity for specific year between 1998-2020.
# As per the requirement we have also formed a pie chart to display how songs are distributed accross genres for that particular year.
# We have set the parameteres and also used cursor.execute to execute the SQL commands.
# Here we have imported tabulate for better table formatting.
# We can check the result by entering different year in the box.

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate 

def fetch_genre_statistics(year, conn):
    """
    Fetch genre statistics from the database for a given year.

    Parameters:
        year (int): The year for which genre statistics are to be retrieved.
        conn (sqlite3.Connection): The database connection object.

    Returns:
        list: A list of tuples containing genre statistics.
    """
    cursor = conn.cursor()

    query = """
    SELECT g.Genre, 
           AVG(s.Danceability) AS avg_danceability, 
           COUNT(*) AS total_songs, 
           AVG(s.Popularity) AS avg_popularity
    FROM song s
    JOIN song_genre sg ON s.ID = sg.SongID
    JOIN genre g ON sg.GenreID = g.ID
    WHERE s.Year = ?
    GROUP BY g.Genre;
    """
    cursor.execute(query, (year,))
    return cursor.fetchall()

def display_genre_statistics(year, conn):
    """
    Display the genre statistics for the given year and visualize them.

    Parameters:
        year (int): The year for which genre statistics are to be displayed.
        conn (sqlite3.Connection): The database connection object.
    """
    data = fetch_genre_statistics(year, conn)

    if not data:
        print(f"No data available for the year {year}.")
        return

    # Converting the data into a dataframe
    df = pd.DataFrame(data, columns=["Genre", "AvgDanceability", "TotalSongs", "AvgPopularity"])

    # Displaying the statistics in tabular form using tabulate
    print(f"\nGenre Statistics for the Year {year}:\n")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))  # Using grid format for better table lines

    # Pie chart for total songs by genre
    genres = df["Genre"]
    total_songs = df["TotalSongs"]

    plt.figure(figsize=(8, 6))
    plt.pie(total_songs, labels=genres, autopct='%1.1f%%', startangle=140)
    plt.title(f"Total Songs by Genre ({year})")
    plt.axis('equal')  # Equal aspect ratio makes sure the pie is drawn as a circle
    plt.show()

def main():
    """
    Main program to prompt the user for a year and display genre statistics.
    """
    print("Genre Statistics Analysis")

    # taking year input
    while True:
        try:
            year = int(input("Enter a year (1998–2020): "))
            if 1998 <= year <= 2020:
                break
            else:
                print("Year out of range. Please enter a year between 1998 and 2020.")
        except ValueError:
            print("Invalid input. Please enter a valid year.")

    # Connecting to the database
    conn = sqlite3.connect("CWDatabase.db")
    try:
        display_genre_statistics(year, conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
