import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Parameters
num_days = 365 * 3  # 3 years of data
start_date = datetime(2020, 1, 1)
locations = {
    "Mumbai": (19.0760, 72.8777),
    "Goa": (15.2993, 74.1240),
    "Kochi": (9.9312, 76.2673)
}

# Generate hourly timestamps
timestamps = [start_date + timedelta(hours=h) for h in range(num_days * 24)]

data = []
for ts in timestamps:
    for loc, (lat, lon) in locations.items():
        # Base seasonal signal (day of year)
        day_of_year = ts.timetuple().tm_yday
        season = 1 + np.sin(2 * np.pi * day_of_year / 365)  # Seasonal oscillation
        
        # --- Temperature (Air & Sea) ---
        base_temp = 28 + 5 * np.sin(2 * np.pi * day_of_year / 365)  # Annual cycle
        diurnal_temp = 3 * np.sin(2 * np.pi * ts.hour / 24)  # Daily cycle
        air_temp = base_temp + diurnal_temp + np.random.normal(0, 1)
        sea_temp = air_temp - 1 + np.random.normal(0, 0.5)  # Sea is cooler
        
        # --- Wind & Waves ---
        # Monsoon effect (June-Sept: strong SW winds)
        if 6 <= ts.month <= 9:
            wind_speed = np.random.weibull(2) * 15  # Higher winds during monsoon
            wind_dir = np.random.normal(225, 20)  #~Southwest direction
            wave_height = 2.5 + 0.5 * np.random.weibull(1.5)
            swell_period = 8 + np.random.normal(0, 2)
        else:
            wind_speed = np.random.weibull(1.5) * 8
            wind_dir = np.random.normal(180, 90)  # Variable direction
            wave_height = 1.0 + 0.3 * np.random.weibull(1.2)
            swell_period = 5 + np.random.normal(0, 2)
        
        # --- Precipitation & Humidity ---
        if 6 <= ts.month <= 9:
            precip = np.random.exponential(2) if np.random.rand() > 0.8 else 0  # Monsoon showers
        else:
            precip = np.random.exponential(0.5) if np.random.rand() > 0.95 else 0
        humidity = 80 + 10 * np.sin(2 * np.pi * ts.hour / 24) + np.random.normal(0, 5)
        
        # --- Pressure ---
        pressure = 1010 + 10 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 2)
        
        data.append([
            ts, lat, lon, air_temp, sea_temp, wind_speed, wind_dir,
            wave_height, swell_period, humidity, pressure, precip
        ])

# Create DataFrame
columns = [
    "Timestamp", "Latitude", "Longitude", "AirTemp (°C)", "SeaTemp (°C)",
    "WindSpeed (km/h)", "WindDir (°)", "WaveHeight (m)", "SwellPeriod (s)",
    "Humidity (%)", "Pressure (hPa)", "Precipitation (mm)"
]
df = pd.DataFrame(data, columns=columns)

# Add lagged temperature (24-hour lag)
df["AirTemp_Lag24h"] = df.groupby("Latitude")["AirTemp (°C)"].shift(24)

# Save to CSV
df.to_csv("western_coast_weather_hourly.csv", index=False)
print("Synthetic data generated!")