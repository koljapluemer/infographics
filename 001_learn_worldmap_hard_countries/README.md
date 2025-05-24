# What is the Hardest Country to Find on the World Map

ECGBL 2025 poster submission (insha'allah), based on learning data from my [learn-the-world-map game](https://github.com/koljapluemer/learn-worldmap).


## Tech

- `js` is used only for the inital download of my data from firebase, because that just appeared way less bothersame than python
- `python` is used for subsequent data cleaning and plotting

## Scripts

### 00

Download the data from the firebase store that I used to track learning events of the map learning game in its entirety, as a JSON.

### 01

First Python script. Since the map game switched datasets (i.e. country names and border definitions) at some point, we're making sure to only analyze data after this point, otherwise we'd have weird semi-duplication.

## Predictor CSV Files

The script `09_make_predictor_csv.py` generates two CSV files in `data/csv/`:
- `predictor_data_full.csv`: Complete dataset
- `predictor_data_demo.csv`: First 200 rows of the full dataset

### Columns

- `deviceId_country`: Compound key combining user ID and country name
- `total_guesses`: Number of times this user has attempted this country
- `user_total_guesses`: Total number of guesses made by this user across all countries
- `last_guess_timestamp`: UNIX timestamp of the user's last attempt for this country
- `current_streak`: Number of consecutive correct guesses for this country (0 if never seen or last guess was wrong)
- `correct_guess_percentage`: Percentage of correct guesses for this user-country combination (-1 if no previous guesses)
- `first_guess_success_rate`: Global success rate for first attempts at this country
- `first_guess_sample_size`: Number of users who have attempted this country at least once
- `third_guess_success_rate`: Global success rate for third attempts at this country
- `third_guess_sample_size`: Number of users who have attempted this country at least three times
- `fifth_guess_success_rate`: Global success rate for fifth attempts at this country
- `fifth_guess_sample_size`: Number of users who have attempted this country at least five times

Note: Success rates are calculated only from users who have made the required number of attempts (e.g., third_guess_success_rate only considers users who have attempted the country at least three times).

## Alternative Predictor CSV Files

The script `10_make_alt_predictor_csv.py` generates four CSV files in `data/csv/`:
- `predictor_data_alt_full.csv`: Complete dataset
- `predictor_data_alt_train.csv`: Training set (50% of data)
- `predictor_data_alt_val.csv`: Validation set (50% of data)
- `predictor_data_alt_demo.csv`: First 200 rows of the full dataset

### Columns

- `deviceId_country_timestamp`: Compound key combining user ID, country name, and timestamp
- `deviceId`: User identifier
- `country`: Country name
- `current_guess_timestamp`: UNIX timestamp of the current guess
- `previous_guess_timestamp`: UNIX timestamp of the previous guess for this country
- `total_guesses`: Number of times this user has attempted this country
- `user_total_guesses`: Total number of guesses made by this user across all countries
- `current_streak`: Number of consecutive correct guesses for this country
- `correct_guess_percentage`: Percentage of correct guesses for this user-country combination (-1 if no previous guesses)
- `time_since_last_country_guess`: Time in seconds since the last guess for this country
- `time_since_last_user_guess`: Time in seconds since the user's last guess
- `countries_attempted_since_last`: Number of unique countries attempted since the last guess
- `is_first_guess_of_day`: Boolean indicating if this is the user's first guess of the day
- `is_correct`: Boolean indicating if the guess was correct
- `first_guess_success_rate`: Global success rate for first attempts at this country
- `first_guess_sample_size`: Number of users who have attempted this country at least once
- `third_guess_success_rate`: Global success rate for third attempts at this country
- `third_guess_sample_size`: Number of users who have attempted this country at least three times
- `fifth_guess_success_rate`: Global success rate for fifth attempts at this country
- `fifth_guess_sample_size`: Number of users who have attempted this country at least five times

Note: The alternative format provides more detailed temporal information and features for each individual guess, rather than aggregating at the user-country level.