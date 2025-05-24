import json
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
from collections import defaultdict
import numpy as np

def load_data(filepath: str) -> Dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def convert_timestamp_to_unix(timestamp: str) -> int:
    """Convert ISO timestamp to UNIX timestamp."""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return int(dt.timestamp())

def process_data(data: Dict) -> pd.DataFrame:
    """Process the data and create a DataFrame with required columns."""
    # Initialize data structures
    user_country_data = defaultdict(list)
    user_total_guesses = defaultdict(int)
    country_attempts = defaultdict(lambda: defaultdict(list))
    
    # First pass: collect all data
    for entry_id, entry in data.items():
        device_id = entry['deviceId']
        country = entry['country']
        timestamp = convert_timestamp_to_unix(entry['timestamp'])
        is_correct = entry['numberOfClicksNeeded'] == 1
        
        # Store entry
        user_country_data[(device_id, country)].append({
            'timestamp': timestamp,
            'is_correct': is_correct
        })
        
        # Update user total guesses
        user_total_guesses[device_id] += 1
        
        # Store country attempt data
        country_attempts[country][device_id].append(is_correct)
    
    # Prepare DataFrame rows
    rows = []
    
    for (device_id, country), attempts in user_country_data.items():
        # Sort attempts by timestamp
        attempts.sort(key=lambda x: x['timestamp'])
        
        # Calculate metrics
        total_guesses = len(attempts)
        last_guess_timestamp = attempts[-1]['timestamp']
        
        # Calculate streak
        current_streak = 0
        for attempt in reversed(attempts):
            if attempt['is_correct']:
                current_streak += 1
            else:
                break
        
        # Calculate correct guess percentage
        correct_guesses = sum(1 for a in attempts if a['is_correct'])
        correct_guess_percentage = correct_guesses / total_guesses if total_guesses > 0 else -1
        
        # Calculate country success rates
        first_attempts = []
        third_attempts = []
        fifth_attempts = []
        
        for user_attempts in country_attempts[country].values():
            if len(user_attempts) >= 1:
                first_attempts.append(user_attempts[0])
            if len(user_attempts) >= 3:
                third_attempts.append(user_attempts[2])
            if len(user_attempts) >= 5:
                fifth_attempts.append(user_attempts[4])
        
        first_guess_success_rate = sum(first_attempts) / len(first_attempts) if first_attempts else 0
        third_guess_success_rate = sum(third_attempts) / len(third_attempts) if third_attempts else 0
        fifth_guess_success_rate = sum(fifth_attempts) / len(fifth_attempts) if fifth_attempts else 0
        
        # Create row
        row = {
            'deviceId_country': f"{device_id}_{country}",
            'total_guesses': total_guesses,
            'user_total_guesses': user_total_guesses[device_id],
            'last_guess_timestamp': last_guess_timestamp,
            'current_streak': current_streak,
            'correct_guess_percentage': correct_guess_percentage,
            'first_guess_success_rate': first_guess_success_rate,
            'third_guess_success_rate': third_guess_success_rate,
            'fifth_guess_success_rate': fifth_guess_success_rate
        }
        rows.append(row)
    
    # Create DataFrame and sort by compound key
    df = pd.DataFrame(rows)
    df = df.sort_values('deviceId_country')
    
    return df

def main():
    # Process full dataset
    data = load_data('data/full/learning_data_after_cutoff.json')
    df_full = process_data(data)
    df_full.to_csv('data/csv/predictor_data_full.csv', index=False)
    
    # Create demo version (first 200 rows)
    df_demo = df_full.head(200)
    df_demo.to_csv('data/csv/predictor_data_demo.csv', index=False)

if __name__ == "__main__":
    main()
