import json
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
from collections import defaultdict
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm

def load_data(filepath: str) -> Dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def convert_timestamp_to_unix(timestamp: str) -> int:
    """Convert ISO timestamp to UNIX timestamp."""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return int(dt.timestamp())

def is_same_day(timestamp1: int, timestamp2: int) -> bool:
    """Check if two timestamps are from the same day."""
    dt1 = datetime.fromtimestamp(timestamp1)
    dt2 = datetime.fromtimestamp(timestamp2)
    return dt1.date() == dt2.date()

def process_data(data: Dict) -> pd.DataFrame:
    """Process the data and create a DataFrame with required columns."""
    # First, convert all entries to a list of dictionaries and sort by timestamp
    entries = []
    for entry_id, entry in tqdm(data.items(), desc="Converting entries"):
        entries.append({
            'deviceId': entry['deviceId'],
            'country': entry['country'],
            'timestamp': convert_timestamp_to_unix(entry['timestamp']),
            'is_correct': entry['numberOfClicksNeeded'] == 1
        })
    
    # Sort entries by timestamp
    entries.sort(key=lambda x: x['timestamp'])
    
    # Calculate global success rates for each country
    country_stats = defaultdict(lambda: {'first': [], 'third': [], 'fifth': []})
    for entry in tqdm(entries, desc="Calculating global stats"):
        country = entry['country']
        device_id = entry['deviceId']
        is_correct = entry['is_correct']
        
        # Get the attempt number for this user-country combination
        attempt_num = len([e for e in entries if e['deviceId'] == device_id and e['country'] == country and e['timestamp'] <= entry['timestamp']])
        
        # Store in appropriate list
        if attempt_num == 1:
            country_stats[country]['first'].append(is_correct)
        elif attempt_num == 3:
            country_stats[country]['third'].append(is_correct)
        elif attempt_num == 5:
            country_stats[country]['fifth'].append(is_correct)
    
    # Calculate success rates
    global_stats = {}
    for country, stats in tqdm(country_stats.items(), desc="Computing success rates"):
        global_stats[country] = {
            'first_guess_success_rate': sum(stats['first']) / len(stats['first']) if stats['first'] else 0,
            'first_guess_sample_size': len(stats['first']),
            'third_guess_success_rate': sum(stats['third']) / len(stats['third']) if stats['third'] else 0,
            'third_guess_sample_size': len(stats['third']),
            'fifth_guess_success_rate': sum(stats['fifth']) / len(stats['fifth']) if stats['fifth'] else 0,
            'fifth_guess_sample_size': len(stats['fifth'])
        }
    
    # Process each entry to create rows
    rows = []
    user_country_history = defaultdict(list)  # (deviceId, country) -> list of (timestamp, is_correct)
    user_last_guess = {}  # deviceId -> timestamp
    user_country_last_guess = {}  # (deviceId, country) -> timestamp
    
    for entry in tqdm(entries, desc="Creating rows"):
        device_id = entry['deviceId']
        country = entry['country']
        timestamp = entry['timestamp']
        is_correct = entry['is_correct']
        
        # Get historical data
        history = user_country_history[(device_id, country)]
        total_guesses = len(history)
        
        # Calculate user's total guesses
        user_total_guesses = sum(len(h) for h in user_country_history.values() if h[0][0] == device_id)
        
        # Calculate streak
        current_streak = 0
        for prev_guess in reversed(history):
            if prev_guess[1]:  # if correct
                current_streak += 1
            else:
                break
        
        # Calculate correct guess percentage
        correct_guesses = sum(1 for g in history if g[1])
        correct_guess_percentage = correct_guesses / total_guesses if total_guesses > 0 else -1
        
        # Calculate time-based features
        time_since_last_country = timestamp - user_country_last_guess.get((device_id, country), timestamp)
        time_since_last_user = timestamp - user_last_guess.get(device_id, timestamp)
        
        # Calculate countries attempted since last
        countries_since_last = set()
        if device_id in user_last_guess:
            last_timestamp = user_last_guess[device_id]
            for e in entries:
                if e['deviceId'] == device_id and last_timestamp < e['timestamp'] < timestamp:
                    countries_since_last.add(e['country'])
        
        # Check if first guess of day
        is_first_guess_of_day = True
        if device_id in user_last_guess:
            is_first_guess_of_day = not is_same_day(user_last_guess[device_id], timestamp)
        
        # Create row
        row = {
            'deviceId_country_timestamp': f"{device_id}_{country}_{timestamp}",
            'deviceId': device_id,
            'country': country,
            'timestamp': timestamp,
            'total_guesses': total_guesses,
            'user_total_guesses': user_total_guesses,
            'previous_guess_timestamp': user_country_last_guess.get((device_id, country), timestamp),
            'current_guess_timestamp': timestamp,
            'current_streak': current_streak,
            'correct_guess_percentage': correct_guess_percentage,
            'time_since_last_country_guess': time_since_last_country,
            'time_since_last_user_guess': time_since_last_user,
            'countries_attempted_since_last': len(countries_since_last),
            'is_first_guess_of_day': is_first_guess_of_day,
            'is_correct': int(is_correct)
        }
        
        # Add global statistics
        row.update(global_stats[country])
        
        rows.append(row)
        
        # Update history
        history.append((timestamp, is_correct))
        user_last_guess[device_id] = timestamp
        user_country_last_guess[(device_id, country)] = timestamp
    
    # Create DataFrame and sort by compound key
    df = pd.DataFrame(rows)
    df = df.sort_values('deviceId_country_timestamp')
    
    return df

def main():
    # Process full dataset
    data = load_data('data/full/learning_data_after_cutoff.json')
    df_full = process_data(data)
    
    # Split into train/val sets
    df_train, df_val = train_test_split(df_full, test_size=0.5, random_state=42)
    
    # Create demo version (first 200 rows)
    df_demo = df_full.head(200)
    
    # Save all versions
    df_full.to_csv('data/csv/predictor_data_alt_full.csv', index=False)
    df_train.to_csv('data/csv/predictor_data_alt_train.csv', index=False)
    df_val.to_csv('data/csv/predictor_data_alt_val.csv', index=False)
    df_demo.to_csv('data/csv/predictor_data_alt_demo.csv', index=False)

if __name__ == "__main__":
    main()
