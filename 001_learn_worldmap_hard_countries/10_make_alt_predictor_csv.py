import json
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm

def load_data(filepath: str) -> Dict:
    """Load JSON data from file."""
    print("Loading JSON data...")
    with open(filepath, 'r') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} entries")
    return data

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
    print("Converting data to DataFrame...")
    # Convert to DataFrame for vectorized operations
    entries_df = pd.DataFrame([
        {
            'deviceId': entry['deviceId'],
            'country': entry['country'],
            'timestamp': convert_timestamp_to_unix(entry['timestamp']),
            'is_correct': entry['numberOfClicksNeeded'] == 1
        }
        for entry in tqdm(data.values(), desc="Converting entries")
    ])
    
    print("Sorting and calculating attempt numbers...")
    # Sort by timestamp
    entries_df = entries_df.sort_values('timestamp')
    
    # Calculate attempt numbers using cumcount
    tqdm.pandas(desc="Calculating attempt numbers")
    entries_df['attempt_num'] = entries_df.groupby(['deviceId', 'country']).cumcount() + 1
    
    print("Calculating global statistics...")
    # Calculate global stats using vectorized operations
    tqdm.pandas(desc="Processing first attempts")
    first_attempts = entries_df[entries_df['attempt_num'] == 1].groupby('country')['is_correct'].progress_apply(list)
    
    tqdm.pandas(desc="Processing third attempts")
    third_attempts = entries_df[entries_df['attempt_num'] == 3].groupby('country')['is_correct'].progress_apply(list)
    
    tqdm.pandas(desc="Processing fifth attempts")
    fifth_attempts = entries_df[entries_df['attempt_num'] == 5].groupby('country')['is_correct'].progress_apply(list)
    
    print("Computing success rates...")
    global_stats = pd.DataFrame({
        'first_guess_success_rate': first_attempts.apply(lambda x: sum(x) / len(x) if x else 0),
        'first_guess_sample_size': first_attempts.apply(len),
        'third_guess_success_rate': third_attempts.apply(lambda x: sum(x) / len(x) if x else 0),
        'third_guess_sample_size': third_attempts.apply(len),
        'fifth_guess_success_rate': fifth_attempts.apply(lambda x: sum(x) / len(x) if x else 0),
        'fifth_guess_sample_size': fifth_attempts.apply(len)
    }).fillna(0)
    
    print("Calculating user statistics...")
    # Calculate user-country histories
    tqdm.pandas(desc="Building user-country histories")
    user_country_history = entries_df.groupby(['deviceId', 'country']).progress_apply(
        lambda x: list(zip(x['timestamp'], x['is_correct']))
    ).to_dict()
    
    # Calculate user total guesses up to each timestamp
    tqdm.pandas(desc="Calculating user total guesses")
    entries_df['user_total_guesses'] = entries_df.groupby('deviceId').cumcount() + 1
    
    print("Calculating streaks and time-based features...")
    # Calculate streaks using vectorized operations
    tqdm.pandas(desc="Calculating streaks")
    entries_df['streak'] = entries_df.groupby(['deviceId', 'country'])['is_correct'].transform(
        lambda x: x[::-1].cumsum()[::-1] * x[::-1].cumprod()[::-1]
    )
    
    # Calculate time-based features
    tqdm.pandas(desc="Calculating country time differences")
    entries_df['prev_timestamp'] = entries_df.groupby(['deviceId', 'country'])['timestamp'].transform('shift')
    entries_df['time_since_last_country'] = entries_df['timestamp'] - entries_df['prev_timestamp'].fillna(entries_df['timestamp'])
    
    tqdm.pandas(desc="Calculating user time differences")
    entries_df['prev_user_timestamp'] = entries_df.groupby('deviceId')['timestamp'].transform('shift')
    entries_df['time_since_last_user'] = entries_df['timestamp'] - entries_df['prev_user_timestamp'].fillna(entries_df['timestamp'])
    
    print("Calculating countries attempted since last...")
    # Calculate countries attempted since last
    def get_countries_since_last(group):
        timestamps = group['timestamp'].values
        countries = group['country'].values
        result = np.zeros(len(group))
        
        for i in tqdm(range(1, len(group)), desc="Processing user entries", leave=False):
            mask = (timestamps[:i] > timestamps[i-1]) & (timestamps[:i] < timestamps[i])
            result[i] = len(np.unique(countries[:i][mask]))
        
        return pd.Series(result, index=group.index)
    
    tqdm.pandas(desc="Calculating countries attempted")
    entries_df['countries_attempted_since_last'] = entries_df.groupby('deviceId').progress_apply(
        get_countries_since_last
    ).reset_index(level=0, drop=True)
    
    print("Calculating day-based features...")
    # Calculate if first guess of day
    tqdm.pandas(desc="Calculating day-based features")
    entries_df['prev_day'] = entries_df.groupby('deviceId')['timestamp'].transform(
        lambda x: pd.Series(x).apply(lambda t: datetime.fromtimestamp(t).date())
    ).shift(1)
    entries_df['current_day'] = entries_df['timestamp'].apply(lambda t: datetime.fromtimestamp(t).date())
    entries_df['is_first_guess_of_day'] = entries_df['prev_day'] != entries_df['current_day']
    
    print("Calculating correct guess percentages...")
    # Calculate correct guess percentage
    tqdm.pandas(desc="Calculating correct guesses")
    entries_df['correct_guesses'] = entries_df.groupby(['deviceId', 'country'])['is_correct'].transform('cumsum')
    entries_df['correct_guess_percentage'] = entries_df['correct_guesses'] / (entries_df['attempt_num'] - 1)
    entries_df['correct_guess_percentage'] = entries_df['correct_guess_percentage'].fillna(-1)
    
    print("Creating final DataFrame...")
    # Create final DataFrame
    tqdm.pandas(desc="Merging with global stats")
    result_df = entries_df.merge(
        global_stats,
        on='country',
        how='left'
    )
    
    # Create compound key before renaming columns
    result_df['deviceId_country_timestamp'] = result_df['deviceId'] + '_' + result_df['country'] + '_' + result_df['timestamp'].astype(str)
    
    # Select and rename columns
    final_columns = {
        'deviceId': 'deviceId',
        'country': 'country',
        'timestamp': 'current_guess_timestamp',
        'attempt_num': 'total_guesses',
        'user_total_guesses': 'user_total_guesses',
        'prev_timestamp': 'previous_guess_timestamp',
        'streak': 'current_streak',
        'correct_guess_percentage': 'correct_guess_percentage',
        'time_since_last_country': 'time_since_last_country_guess',
        'time_since_last_user': 'time_since_last_user_guess',
        'countries_attempted_since_last': 'countries_attempted_since_last',
        'is_first_guess_of_day': 'is_first_guess_of_day',
        'is_correct': 'is_correct',
        'deviceId_country_timestamp': 'deviceId_country_timestamp'
    }
    
    # Add global stats columns
    for col in global_stats.columns:
        final_columns[col] = col
    
    result_df = result_df[list(final_columns.keys())].rename(columns=final_columns)
    
    # Sort by compound key
    print("Sorting final DataFrame...")
    result_df = result_df.sort_values('deviceId_country_timestamp')
    
    return result_df

def main():
    print("Loading data...")
    # Process full dataset
    data = load_data('data/full/learning_data_after_cutoff.json')
    df_full = process_data(data)
    
    print("Splitting data...")
    # Split into train/val sets
    df_train, df_val = train_test_split(df_full, test_size=0.5, random_state=42)
    
    # Create demo version (first 200 rows)
    df_demo = df_full.head(200)
    
    print("Saving files...")
    # Save all versions with progress bars
    for name, df in tqdm([
        ('predictor_data_alt_full.csv', df_full),
        ('predictor_data_alt_train.csv', df_train),
        ('predictor_data_alt_val.csv', df_val),
        ('predictor_data_alt_demo.csv', df_demo)
    ], desc="Saving files"):
        df.to_csv(f'data/csv/{name}', index=False)
    
    print("Done!")

if __name__ == "__main__":
    main()
