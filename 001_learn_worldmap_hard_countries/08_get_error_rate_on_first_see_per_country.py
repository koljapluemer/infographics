# for each country, calculate the error rate on first see
# to validate that something is first see, we need to see that the device_id
# never interacted with that country before

import json
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Initialize data structures
country_first_attempts: Dict[str, List[bool]] = defaultdict(list)  # List of success/failure for first attempts
user_country_history: Dict[str, Set[str]] = defaultdict(set)  # Track which countries each user has seen

# Sort entries by timestamp to process in chronological order
sorted_entries = sorted(
    data.values(),
    key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00'))
)

# Process each entry chronologically
for entry in sorted_entries:
    country = entry['country']
    device_id = entry['deviceId']
    
    # Check if this is the user's first interaction with this country
    if country not in user_country_history[device_id]:
        # Record the attempt (True if correct on first try, False if not)
        is_correct = entry['numberOfClicksNeeded'] == 1
        country_first_attempts[country].append(is_correct)
        
        # Mark this country as seen by this user
        user_country_history[device_id].add(country)

# Calculate statistics for each country
results = []
for country, attempts in country_first_attempts.items():
    if len(attempts) >= 5:  # Only consider countries with at least 5 first attempts
        error_rate = (1 - sum(attempts) / len(attempts)) * 100
        results.append({
            'country': country,
            'error_rate': error_rate,
            'total_first_attempts': len(attempts),
            'successful_first_attempts': sum(attempts)
        })

# Sort by error rate (descending)
results.sort(key=lambda x: x['error_rate'], reverse=True)

# Print results
print("\nError Rate on First See per Country:")
print("----------------------------------------")
print(f"{'Country':<25} {'Error Rate':<10} {'Total First Attempts':<20} {'Successful First Attempts':<25}")
print("-" * 80)
for entry in results:
    print(f"{entry['country']:<25} {entry['error_rate']:.1f}%{'':<5} {entry['total_first_attempts']:<20} {entry['successful_first_attempts']:<25}")

# Generate LaTeX table
latex_table = """\\begin{table}[htbp]
\\centering
\\caption{Error Rate on First See per Country}
\\label{tab:first-see-error-rates}
\\begin{tabular}{lrrr}
\\toprule
Country & \\% Error Rate & N & Successful \\\\
\\midrule
"""

# Add data rows
for entry in results:
    latex_table += f"{entry['country']} & {entry['error_rate']:.1f} & {entry['total_first_attempts']} & {entry['successful_first_attempts']} \\\\\n"

# Close the table
latex_table += """\\bottomrule
\\end{tabular}
\\end{table}"""

# Save the LaTeX table to a file
import os
os.makedirs('plots', exist_ok=True)
with open('plots/first_see_error_rates_table.tex', 'w') as f:
    f.write(latex_table)