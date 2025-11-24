import requests
import sqlite3
import time

# -----------------------------
# STEP 1: Configure Strava API
# -----------------------------
ACCESS_TOKEN = "8547e29d4ce35919018000849714cf877b269373"  # Replace with your Strava access token
PER_PAGE = 200  # Max activities per request

# -----------------------------
# STEP 2: Setup SQLite database
# -----------------------------
conn = sqlite3.connect('strava.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    name TEXT,
    type TEXT,
    distance REAL,
    moving_time REAL,
    elapsed_time REAL,
    total_elevation_gain REAL,
    start_time TEXT,
    average_speed REAL,
    max_speed REAL,
    average_heartrate REAL,
    max_heartrate REAL,
    average_cadence REAL,
    calories REAL
)
''')

conn.commit()

# -----------------------------
# STEP 3: Fetch activities
# -----------------------------
def fetch_activities(page=1):
    url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    params = {'per_page': PER_PAGE, 'page': page}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching activities: {response.status_code}")
        return []
    return response.json()

page = 1
while True:
    activities = fetch_activities(page)
    if not activities:
        break
    
    # -----------------------------
    # STEP 4: Insert into SQLite
    # -----------------------------
    for a in activities:
        cur.execute('''
        INSERT OR REPLACE INTO activities (
            id, name, type, distance, moving_time, elapsed_time,
            total_elevation_gain, start_time, average_speed, max_speed, average_heartrate, max_heartrate, average_cadence, calories
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            a.get('id'),
            a.get('name'),
            a.get('type'),
            a.get('distance'),
            a.get('moving_time'),
            a.get('elapsed_time'),
            a.get('total_elevation_gain'),
            a.get('start_date'),
            a.get('average_speed'),
            a.get('max_speed'),
            a.get('average_heartrate'),
            a.get('max_heartrate'),
            a.get('average_cadence'),
            a.get('calories')
            ))
    conn.commit()
    print(f"Page {page} done, {len(activities)} activities inserted.")
    
    page += 1
    time.sleep(1)  # avoid hitting rate limits

conn.close()
print("All activities fetched and saved to strava.db")