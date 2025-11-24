import json
import requests

def load_tokens():
    with open("tokens.json") as f:
        return json.load(f)

def get_activities(access_token):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None

if __name__ == "__main__":
    tokens = load_tokens()
    print("🔍 Fetching your Strava activities...")
    activities = get_activities(tokens["access_token"])

    if activities:
        print(f"📊 You have {len(activities)} recent activities.\n")
        for activity in activities[:5]:
            print(f"{activity['name']} | Distance: {activity['distance']:.0f}m | "
                  f"Moving Time: {activity['moving_time']}s")
