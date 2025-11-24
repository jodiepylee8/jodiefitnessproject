import os
import json
from stravalib import Client
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN_FILE = "strava_refresh_token.txt"  # file to store refresh token
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost")

client = Client()

# ---------------------------
# Step 1: Get refresh token
# ---------------------------
def get_refresh_token():
    if os.path.exists(REFRESH_TOKEN_FILE):
        with open(REFRESH_TOKEN_FILE, "r") as f:
            return f.read().strip()
    else:
        # First time setup: authorize app
        auth_url = client.authorization_url(
            client_id=CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            scope=['activity:read_all'],
            approval_prompt='force'
        )
        print("Go to this URL in your browser and authorize the app:")
        print(auth_url)
        code = input("Paste the code parameter from the redirected URL here: ").strip()

        token = client.exchange_code_for_token(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            code=code
        )

        # Save refresh token
        with open(REFRESH_TOKEN_FILE, "w") as f:
            f.write(token['refresh_token'])
        print("Refresh token saved!")

        return token['refresh_token']

# ---------------------------
# Step 2: Refresh access token
# ---------------------------
def refresh_access_token(refresh_token):
    token_response = client.refresh_access_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=refresh_token
    )
    # Save new refresh token
    with open(REFRESH_TOKEN_FILE, "w") as f:
        f.write(token_response['refresh_token'])
    client.access_token = token_response['access_token']
    return token_response

# ---------------------------
# Step 3: Pull activities
# ---------------------------
def format_pace(min_per_km):
    """Convert decimal minutes to MM:SS string."""
    if min_per_km is None:
        return None
    minutes = int(min_per_km)
    seconds = int(round((min_per_km - minutes) * 60))
    return f"{minutes}:{seconds:02d}"

def get_activities(limit=50):
    activities = client.get_activities(limit=limit)
    data = []
    for activity in activities:
        if activity.type != 'Run':
            continue  # Skip anything that is not a run

        avg_speed_m_s = activity.average_speed if activity.average_speed else None
        avg_speed_kmh = (avg_speed_m_s * 3.6) if avg_speed_m_s else None
        avg_pace_min_per_km = 16.6667 / avg_speed_m_s if avg_speed_m_s else None  # m/s → min/km
        avg_pace_mmss = format_pace(avg_pace_min_per_km)
        
        data.append({
            'name': activity.name,
            'type': activity.type if activity.type else None,
            'elapsed_time': activity.elapsed_time if activity.elapsed_time else None,
            'distance_km': activity.distance / 1000 if activity.distance else None,
            'average_HR': activity.average_heartrate if activity.average_heartrate else None,
            'average_speed_kmh': avg_speed_kmh,
            'average_pace_min_per_km': avg_pace_min_per_km,
            'average_pace_mmss': avg_pace_mmss,
            'average_pace': (1000/60)/activity.average_speed if activity.average_speed else None,
            'average_cadence': activity.average_cadence if activity.average_cadence else None,
            'start_date': activity.start_date,
        })
    return pd.DataFrame(data)

# ---------------------------
# Main workflow
# ---------------------------
def load_tokens():
    with open("tokens.json") as f:
        return json.load(f)

def main():
    refresh_token = get_refresh_token()
    token_response = refresh_access_token(refresh_token)
    print("Access token refreshed!")

    df = get_activities(limit=300)  # Pull last 100 activities
    df['start_date'] = pd.to_datetime(df['start_date'])
    print(df[['name', 'distance_km', 'average_HR','average_pace_min_per_km','average_pace_mmss']].head(10))

    df['date'] = pd.to_datetime(df['start_date']).dt.date

    # --- STEP 1: Create a training load metric  ---
    if 'suffer_score' in df.columns:
        df['training_load'] = df['suffer_score']
    else:
        df['training_load'] = (df['distance_km']*100) + (df['elapsed_time'] / 60)

    # --- STEP 2: Group by day ---
    daily_load = df.groupby('date')['training_load'].sum().reset_index()

    # --- STEP 3: Group by day ---
    daily_load = df.groupby('date')['training_load'].sum().reset_index()

    # --- STEP 4: Create full year date range ---
    start_date = pd.to_datetime(daily_load['date'].min())
    end_date = pd.to_datetime('today')

    all_dates = pd.DataFrame({'date': pd.date_range(start_date, end_date)})

    all_dates['date'] = pd.to_datetime(all_dates['date']).dt.date
    daily_load['date'] = pd.to_datetime(daily_load['date']).dt.date

    calendar_df = pd.merge(all_dates, daily_load, on='date', how='left').fillna(0)
    calendar_df['date'] = pd.to_datetime(calendar_df['date'])

    # --- STEP 5: Pivot for heatmap (Calendar Style) ---
    calendar_df['year'] = calendar_df['date'].dt.year
    calendar_df['month'] = calendar_df['date'].dt.month
    calendar_df['day'] = calendar_df['date'].dt.day
    calendar_df['weekday'] = calendar_df['date'].dt.weekday
    calendar_df['week'] = calendar_df['date'].dt.isocalendar().week

    heatmap_data = calendar_df.pivot_table(index='weekday',
                                       columns='week',
                                       values='training_load',
                                       aggfunc='sum')

    # ---------------------------
    # Plot pace and HR over time
    # ---------------------------
    fig, ax1 = plt.subplots(figsize=(10,5))

    line1, = ax1.plot(df['start_date'], df['average_pace_min_per_km'], marker='o', color='green', label='Pace (min/km)')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Pace (min/km)', color='green')
    ax1.tick_params(axis='y', labelcolor='green')
    ax1.grid(True)

    ax2 = ax1.twinx()

    line2, = ax2.plot(df['start_date'], df['average_HR'], marker='x', color='red', label='Average HR')
    ax2.set_ylabel('Average Heart Rate (bpm)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    ax1.invert_yaxis()  # Faster pace = lower value

    plt.title('Average Running Pace and HR Over Time')
  
    plt.xticks(rotation=90)

    lines = [line1, line2]
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left')

    plt.figure(figsize=(10, 5))
    sns.heatmap(heatmap_data,
            cmap='YlOrRd',
            linewidths=0.5,
            linecolor='gray',
            cbar_kws={'label': 'Training Load (Intensity & Frequency)'})
    
    plt.title("Training Intensity Heatmap - Past Year")
    plt.ylabel("Day of Week (0=Mon)")
    plt.xlabel("Week Number")

    plt.show()

if __name__ == "__main__":
    main()