# Interactive Music Analytics Dashboard

**Explore music genres, benchmark artist popularity, and compare artist-year performance with Python and SQL.**

A Jupyter dashboard that turns a music CSV into a relational SQLite database and exposes analysis through sliders, text inputs, tables, and charts. Developed as a coursework project and maintained as a data analytics portfolio example.

## What you can explore

| Question | Method | Output |
| --- | --- | --- |
| How do genres compare in a selected year? | SQL joins and grouped averages | Danceability, song counts, popularity, and a genre distribution chart |
| How does an artist compare with their genres? | Artist averages against genre benchmarks | Comparison table and bar chart |
| Which artist-year combinations score highest in a period? | Weighted score, sorted across the selected range | Top five artist-year records and a trend chart |

**Stack:** Python · pandas · SQLite · NumPy · Matplotlib · ipywidgets · Jupyter

## Quick start

Use Python 3.11 or newer. Run these commands from the repository root:

```bash
git clone https://github.com/Shailesh14-spec/interactive-music-analytics-dashboard-python.git
cd interactive-music-analytics-dashboard-python
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Supply the dataset and build the database

The source CSV and generated database are **not included**. Provide your own compatible `songs_normalize.csv`; the original dataset's source and redistribution terms have not yet been documented.

Required columns:

```text
artist,song,duration_ms,explicit,year,popularity,danceability,speechiness,genre
```

Use numeric values for duration, year, popularity, danceability, and speechiness. Genres are comma-separated strings. Explicit values should be booleans or 0/1.

```bash
python Preprocessing.py /path/to/songs_normalize.csv
python -m notebook menu.ipynb
```

Run the notebook cells, then use the controls. Keep the notebook's working directory at the repository root. Preprocessing creates `filtered_Songs.csv` and `CWDatabase.db` there, replacing existing analysis tables in that database.

## Analysis pipeline

1. Read the input CSV and convert duration from milliseconds to rounded seconds.
2. Retain songs with popularity **> 50**, speechiness **0.33–0.66 inclusive**, and danceability **> 0.20**.
3. Populate artist, song, genre, and song–genre tables in SQLite.
4. Query the database using parameterised SQL.
5. Display results through notebook widgets and Matplotlib.

## Repository guide

| File | Purpose |
| --- | --- |
| [menu.ipynb](menu.ipynb) | Interactive notebook and callbacks |
| [Preprocessing.py](Preprocessing.py) | Portable CSV-to-database entry point |
| [Artist.py](Artist.py) | Artist popularity and genre benchmarks |
| [Genre.py](Genre.py) | Genre statistics for a selected year |
| [Top5.py](Top5.py) | Ranked artist-year analysis |
| [requirements.txt](requirements.txt) | Runtime dependencies |
| `*-2.py` files | Original coursework versions retained for reference |

## Interpretation and limitations

- Results describe the **filtered dataset**, not the whole music market.
- The notebook controls cover **1998–2020**; actual coverage depends on your CSV.
- The ranking score is `0.7 × song count + 0.3 × average popularity`. These measures have different scales; the weights do not establish a 70/30 contribution after normalisation.
- The query selects the five highest-scoring **artist-year combinations** across the range. It can return the same artist in multiple years and does not necessarily identify five distinct artists.
- Tracks can belong to multiple genres, so genre counts overlap.
- Chart gaps represent years absent from the selected top-five results. Zero-filled table cells should not be interpreted as observed zero scores.
- Popularity is a dataset field, not revenue, listener retention, or a causal measure of success.

## Skills demonstrated

Relational data modelling · SQL joins and aggregation · data preprocessing · exploratory analysis · interactive visualisation · modular Python

## Next improvements

- Document the dataset source, licence, and data dictionary.
- Add screenshots using the original dataset once it is available.
- Validate input schemas and missing values before loading.
- Compare normalised ranking methods and support five distinct artists.

## Licence

Code is available under the [MIT licence](LICENSE). Any externally supplied dataset remains subject to its own terms.
