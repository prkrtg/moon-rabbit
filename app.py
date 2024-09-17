from flask import Flask, send_from_directory, jsonify, request
import requests
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()  

app = Flask(__name__)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('static', 'moon.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# Helper function to convert UTC time to server local time
def convert_utc_to_local(utc_time_str, timezone_str):
    utc_time = datetime.strptime(utc_time_str, "%H:%M")
    utc_time = pytz.utc.localize(utc_time)  # Localize the time to UTC
    local_tz = pytz.timezone(timezone_str)
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime("%H:%M")

@app.route('/api/moon-phase', methods=['GET'])
def get_moon_phase():
    # Coordinates for Pasadena, CA
    coords = "34.1478,-118.1445"

    # Get date from query parameters, default to today's date if not provided
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')  # Default to current date

    try:
        # Construct the API URL
        api_url = f"https://aa.usno.navy.mil/api/rstt/oneday?date={date_str}&coords={coords}"
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Define the server's timezone
        server_timezone = 'America/Los_Angeles'  # Pasadena is in this timezone

        # Extract and convert times
        moon_data = data["properties"]["data"]["moondata"]
        moon_phase = {
            "current_phase": data["properties"]["data"]["curphase"],
            "fractional_illumination": data["properties"]["data"]["fracillum"],
            "moon_rise_time": next((convert_utc_to_local(item["time"], server_timezone) for item in moon_data if item["phen"] == "Rise"), "Not available"),
            "moon_set_time": next((convert_utc_to_local(item["time"], server_timezone) for item in moon_data if item["phen"] == "Set"), "Not available"),
            "moon_transit_time": next((convert_utc_to_local(item["time"], server_timezone) for item in moon_data if item["phen"] == "Upper Transit"), "Not available"),
        }

        # Fetch the APOD image URL using the API key from .env
        api_key = os.getenv('NASA_API_KEY')  # Get API key from environment variable
        moon_phase['image_url'] = fetch_apod_image(api_key)

        return jsonify(moon_phase)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500
    
# Fetch APOD image from NASA
def fetch_apod_image(api_key):
    try:
        response = requests.get(f'https://api.nasa.gov/planetary/apod?api_key={api_key}')
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data.get('url', 'https://via.placeholder.com/100')  # Default to placeholder image
    except requests.RequestException as e:
        print(f"Error fetching APOD image: {e}")
        return 'https://via.placeholder.com/100'  # Default to placeholder image on error


if __name__ == '__main__':
    app.run(debug=True)
