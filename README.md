# Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

A multi-page Streamlit application that combines live cricket data from the Cricbuzz API with a relational SQL database. It lets users follow matches, explore player statistics, run 25 analytical SQL queries and manage player records through a CRUD interface.

**Domain:** Sports analytics | **Stack:** Python, Streamlit, REST API, MySQL, SQL, pandas

---

## Features

| Page | What it does |
|---|---|
| **Home** | Project overview, tools used, setup instructions and links to the documentation |
| **Live Matches** | Ongoing and recent matches with scorecards, teams, venue and match status |
| **Top Player Stats** | Most runs, highest scores, most wickets, with clean tables and charts |
| **SQL Queries & Analytics** | 25 SQL questions (beginner, intermediate, advanced) with results shown as tables |
| **CRUD Operations** | Form-based add, update and delete of player records, with validation |
| **Status** | Remaining API calls and database connection check |

## Tech stack

- **Python 3.12**
- **Streamlit** for the multi-page web interface
- **requests** for REST API calls
- **pandas** for data handling
- **SQLAlchemy + PyMySQL** for database access (MySQL 8+)
- **python-dotenv** for keeping secrets out of the code
- **Plotly** for charts
- **pytest** for tests

## Architecture

The code is split into layers. Each layer only talks to the layer below it, and pages never touch SQL or the API directly.

```
            User (browser)
                  |
   Frontend: Streamlit  (main.py, pages/)
                  |
   Services: business logic, validation, refresh rules
          |                         |
   API layer (api/)         Database layer (database/, utils/db_connection.py)
          |                         |
   Cricbuzz REST API         MySQL database  +  sql/ (25 analytical queries)
```

**Key design decisions**

- **The database is the source of truth.** The free API plan allows only 200 requests per month, so pages read from the database and the API is called only when the user presses a refresh button.
- **Raw API responses are saved to `data/` before parsing**, so a parsing bug never costs another API call.
- **API IDs are used as primary keys**, so re-importing a match updates the existing row instead of creating a duplicate.
- **Every imported row has a `data_source` column** (`api` or `sample`), so real and sample data are never mixed up silently.
- **Bowling is stored in balls, not decimal overs**, because "4.3 overs" cannot be added or averaged correctly as a number.
- **Derived values such as averages and economy rates are calculated in queries or views**, not stored, so they can never disagree with the base data.

## Project structure

```
cricbuzz-livestats/
|-- main.py                 # Home page and application entry point
|-- config.py               # Settings, reads environment variables from .env
|-- requirements.txt
|-- README.md
|-- .env                    # Secrets (never committed to Git)
|-- api/                    # Cricbuzz API client (requests, retries, timeouts)
|-- services/               # Business logic between pages, API and database
|-- database/               # Schema and database helpers
|-- pages/                  # One Streamlit file per page
|-- sql/                    # Schema and the 25 analytical queries
|-- utils/                  # db_connection.py, validators, logging helpers
|-- tests/                  # pytest test cases
|-- data/                   # Saved API responses and sample data
|-- assets/                 # Screenshots and images
`-- docs/                   # Extra documentation
```

## Database design

The database is normalized (3rd normal form) and uses primary keys, foreign keys, CHECK constraints and indexes.

Main tables: `countries`, `formats`, `teams`, `venues`, `players`, `series`, `matches`, `innings`, `batting_scorecards`, `bowling_scorecards`, `player_career_stats` and `api_call_log`. Foreign keys protect match history: a player who has scorecard records cannot be deleted by accident, and the CRUD page explains why when you try.

The full table definitions are in the `sql/` folder.

## Setup

### Prerequisites

- Python 3.12 or newer
- MySQL Server 8 or newer
- A free RapidAPI account subscribed to the **Cricbuzz Cricket** API
- Git

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd cricbuzz-livestats
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 3. Configure your API key and database

Create a file named `.env` in the project root:

```
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com
LIVE_MATCHES_URL=https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=cricbuzz_livestats
```

Never commit `.env`. It is listed in `.gitignore`.

### 4. Create the database

Run the SQL files in the `sql/` folder in order, starting with the schema file:

```bash
mysql -u root -p < sql/schema.sql
```

### 5. Run the app

```bash
streamlit run main.py
```

The app opens at http://localhost:8501.

## API usage and limits

The free Basic plan allows **200 requests per month** (a hard limit) and 1,000 requests per hour. To stay within this quota the app:

- reads from the database by default and calls the API only on an explicit refresh,
- saves every raw response in `data/` for reuse,
- logs each call in the `api_call_log` table and shows the remaining quota on the Status page.

## SQL analytics

The `sql/` folder contains 25 queries that answer business questions about players, teams, matches and venues:

- **Beginner (8):** basic SELECT, WHERE, GROUP BY and ORDER BY
- **Intermediate (8):** JOINs, subqueries and aggregate functions
- **Advanced (9):** window functions, CTEs and complex analytical calculations

Each query is also available on the **SQL Queries & Analytics** page.

## Testing

```bash
pytest
```

Tests cover input validation, database helpers and API response parsing.

## Screenshots

Add your screenshots to the `assets/` folder and link them here.

| Page | Screenshot |
|---|---|
| Home | `assets/home.png` |
| Live Matches | `assets/live_matches.png` |
| Top Player Stats | `assets/top_players.png` |
| SQL Analytics | `assets/sql_analytics.png` |
| CRUD | `assets/crud.png` |

## Limitations

- The free API plan is limited to 200 requests per month, so only a small amount of data is imported from the API.
- Some data needed by the analytical queries (for example toss details, partnerships and fielding statistics) is not available from the API at this quota and is supplied as sample data. Such rows are marked with `data_source = 'sample'`.
- Live data depends on what is being played when the data is refreshed.

## Future improvements

- Login and user roles to protect the CRUD page
- Scheduled data refresh
- Match outcome prediction
- Deployment on Streamlit Community Cloud or Docker

## Security

API keys and database passwords are read from environment variables and are never stored in the code or in Git. If a key is ever exposed, regenerate it in the RapidAPI dashboard and update `.env`.

## Author

**Disha**
