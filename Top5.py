# Student ID- F415563
# As per the coursework requirement we have tried to create a program using which we can analyze the top 5 artist as per the defined period.
# We have ranked them on basis of number of songs and popularity.
# For better visualization we have shown result in table and line chart format.
# By entering the start and end year we will be able to get the required table and the graph accordingly.
# We have also used a formula ,Rank Value=(Number of Songs×0.7)+(Average Popularity×0.3) for song quality and qualtity.
# In order to make this work we need to make sure we have SQLite database in the same directory and it has artist and song tables.
# We need to run this program in python environment. Once we will run this we will be asked for start year and end year.
# We can choose any year between 1998-2020. Once we will give the input in text boxes it will display the result  in table and line chart format.
# In table we will get rows and columns which will contain the artist name, year and their average rank.
# In line chart we will get individual rank for artist and yearly average rank will be displayed by a red line.

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate  # Install via `pip install tabulate`

# Constants used for ranking weights
WEIGHT_X = 0.7  # Weight for number of songs
WEIGHT_Y = 0.3  # Weight for average popularity

class TopArtistsAnalyzer:
    """
    Class to identify and analyze the top 5 artists within a user-specified range of years
    based on a ranking formula that uses the number of songs and their average popularity.
    """

    def __init__(self, db_path):
        """Initialize with the database path."""
        self.db_path = db_path

    def connect_db(self):
        """Establish a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def fetch_top_artists(self, start_year, end_year):
        """
        Fetch the top 5 artists based on the ranking formula within the specified year range.

        Parameters:
            start_year (int): Start year for the analysis.
            end_year (int): End year for the analysis.

        Returns:
            list: Query results containing artist name, year, total songs, average popularity,
                  and rank value.
        """
        conn = self.connect_db()
        cursor = conn.cursor()

        query = """
            SELECT a.Name AS ArtistName,
                   COUNT(s.ID) AS TotalSongs,
                   AVG(s.Popularity) AS AvgPopularity,
                   (COUNT(s.ID) * ? + AVG(s.Popularity) * ?) AS RankValue,
                   s.Year
            FROM artist a
            JOIN song s ON a.ID = s.Artist
            WHERE s.Year BETWEEN ? AND ?
            GROUP BY a.Name, s.Year
            ORDER BY RankValue DESC
            LIMIT 5;
        """

        cursor.execute(query, (WEIGHT_X, WEIGHT_Y, start_year, end_year))
        data = cursor.fetchall()
        conn.close()
        return data

    def display_results(self, start_year, end_year, data):
        """
        Display the top 5 artists in a properly formatted tabular form using `tabulate`.

        Parameters:
            start_year (int): Start year for the analysis.
            end_year (int): End year for the analysis.
            data (list): Query results from fetch_top_artists.
        """
        if not data:
            print(f"No data found for the specified range {start_year}-{end_year}.")
            return

# organising the data for better processing
        
        artist_data = {}
        for row in data:
            artist, total_songs, avg_popularity, rank_value, year = row
            if artist not in artist_data:
                artist_data[artist] = {"rank_values": {}, "total_rank": 0, "years_count": 0}
            artist_data[artist]["rank_values"][year] = rank_value
            artist_data[artist]["total_rank"] += rank_value
            artist_data[artist]["years_count"] += 1

# calculating overall avg rank for each artist
        
        for artist in artist_data:
            artist_data[artist]["avg_rank"] = artist_data[artist]["total_rank"] / artist_data[artist]["years_count"]

        # Preparing data for the table
        years = list(range(start_year, end_year + 1))
        rows = []
        for artist, data in artist_data.items():
            row = [artist] + [f"{data['rank_values'].get(year, 0.0):.2f}" for year in years] + [f"{data['avg_rank']:.2f}"]
            rows.append(row)

        # Generating column headers
        headers = ["Artist"] + [f"Year {year}" for year in years] + ["Average"]

        # Displaying the table
        print("\nTop Artists Table:")
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

        # Generating the line chart
        plt.figure(figsize=(12, 8))
        for artist, data in artist_data.items():
            rank_values = [data["rank_values"].get(year, None) for year in years]
            plt.plot(years, rank_values, marker="o", label=artist, linestyle="-", linewidth=1.5)

        # Adding an average rank line
        avg_yearly_rank = []
        for year in years:
            year_values = [data["rank_values"].get(year) for artist, data in artist_data.items() if year in data["rank_values"]]
            avg_yearly_rank.append(np.mean(year_values) if year_values else None)

        plt.plot(years, avg_yearly_rank, color="red", linestyle="--", marker="D", label="Yearly Average", linewidth=2)

        plt.title(f"Top 5 Artists' Rank Values ({start_year}-{end_year})")
        plt.xlabel("Year")
        plt.ylabel("Rank Value")
        plt.legend()
        plt.grid(True)
        plt.show()

    @staticmethod
    def get_year_range():
        """
        Prompt the user to input a valid year range.

        Returns:
            tuple: Start and end years.
        """
        while True:
            try:
                start_year = int(input("Enter the start year (1998-2020): "))
                end_year = int(input("Enter the end year (1998-2020): "))

                if 1998 <= start_year <= 2020 and 1998 <= end_year <= 2020 and start_year <= end_year:
                    return start_year, end_year
                else:
                    print("Invalid range. Please enter years between 1998 and 2020, ensuring start year <= end year.")
            except ValueError:
                print("Invalid input. Please enter numerical values for the years.")

# main execution of the program
if __name__ == "__main__":
    print("Top Artists Ranking Program")
    db_path = "CWDatabase.db"  
    analyzer = TopArtistsAnalyzer(db_path)

    # taking user input for year range
    start_year, end_year = analyzer.get_year_range()

    # results
    data = analyzer.fetch_top_artists(start_year, end_year)
    analyzer.display_results(start_year, end_year, data)
