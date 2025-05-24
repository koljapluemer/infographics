import json
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
TARGET_COUNTRY = "Dominica"  # Change this to analyze different countries
MAX_ATTEMPTS = 10  # Maximum number of attempts to analyze

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Group attempts by deviceId
user_attempts = defaultdict(list)

# Process each entry
for entry in data.values():
    if entry['country'] == TARGET_COUNTRY:
        # Convert timestamp to datetime for sorting
        timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
        user_attempts[entry['deviceId']].append({
            'timestamp': timestamp,
            'distance': entry['distanceOfFirstClickToCenterOfCountry']
        })

# Sort attempts by timestamp for each user
for device_id in user_attempts:
    user_attempts[device_id].sort(key=lambda x: x['timestamp'])

# Calculate average distances for each attempt number (only up to attempt 10)
attempt_distances = defaultdict(list)

for attempts in user_attempts.values():
    for i, attempt in enumerate(attempts, 1):
        if i <= MAX_ATTEMPTS:  # Only include attempts up to 10
            attempt_distances[i].append(attempt['distance'])

# Calculate statistics
results = []
for attempt_num in range(1, MAX_ATTEMPTS + 1):
    distances = attempt_distances[attempt_num]
    if distances:  # Only include attempt numbers that have data
        q1, median, q3 = np.percentile(distances, [25, 50, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Find whiskers (non-outlier min/max)
        whisker_min = min(d for d in distances if d >= lower_bound)
        whisker_max = max(d for d in distances if d <= upper_bound)
        
        # Find outliers
        outliers = [d for d in distances if d < lower_bound or d > upper_bound]
        
        results.append({
            'attempt_number': attempt_num,
            'q1': q1,
            'median': median,
            'q3': q3,
            'whisker_min': whisker_min,
            'whisker_max': whisker_max,
            'outliers': outliers,
            'n_attempts': len(distances)
        })

# Print results to terminal
print(f"\nLearning Trajectory for {TARGET_COUNTRY}")
print("----------------------------------------")
print(f"{'Attempt #':<10} {'Median':<15} {'Q1':<15} {'Q3':<15} {'N':<10}")
print("-" * 65)
for result in results:
    print(f"{result['attempt_number']:<10} {result['median']:.2f}{'':<5} {result['q1']:.2f}{'':<5} {result['q3']:.2f}{'':<5} {result['n_attempts']:<10}")

# Generate LaTeX table
latex_table = """\\begin{table}[htbp]
\\centering
\\caption{Learning Trajectory for """ + TARGET_COUNTRY + """}
\\label{tab:learning-trajectory}
\\begin{tabular}{rrrrr}
\\toprule
Attempt & Median & Q1 & Q3 & N \\\\
\\midrule
"""

# Add data rows
for result in results:
    latex_table += f"{result['attempt_number']} & {result['median']:.2f} & {result['q1']:.2f} & {result['q3']:.2f} & {result['n_attempts']} \\\\\n"

# Close the table
latex_table += """\\bottomrule
\\end{tabular}
\\end{table}"""

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)

# Save LaTeX table to file
table_filename = f'plots/learning_trajectory_{TARGET_COUNTRY.lower().replace(" ", "_")}_table.tex'
with open(table_filename, 'w') as f:
    f.write(latex_table)

# Create box plot
plt.figure(figsize=(10, 6))

# Prepare data for boxplot
box_data = [attempt_distances[i] for i in range(1, MAX_ATTEMPTS + 1) if attempt_distances[i]]

# Define boxplot properties
boxprops = dict(facecolor='white', color='black', linewidth=1.5)
whiskerprops = dict(color='black', linewidth=1.5)
capprops = dict(color='black', linewidth=1.5)
medianprops = dict(color='black', linewidth=2)
flierprops = dict(marker='o', markerfacecolor='none', markeredgecolor='black', markersize=6, alpha=0.6)

# Create boxplot with properties
boxplot = plt.boxplot(box_data, 
                     positions=range(1, len(box_data) + 1),
                     widths=0.6,
                     patch_artist=True,
                     showfliers=True,
                     boxprops=boxprops,
                     whiskerprops=whiskerprops,
                     capprops=capprops,
                     medianprops=medianprops,
                     flierprops=flierprops)

plt.title(f'Learning Trajectory for {TARGET_COUNTRY}')
plt.xlabel('Attempt Number')
plt.ylabel('Distance from Country Center (pixels)')
plt.grid(True, linestyle='--', alpha=0.7, axis='y')

# Set x-axis ticks to match attempt numbers
plt.xticks(range(1, len(box_data) + 1))

# Save plot
plot_filename = f'plots/learning_trajectory_{TARGET_COUNTRY.lower().replace(" ", "_")}.png'
plt.savefig(plot_filename, bbox_inches='tight', dpi=300)
plt.close()

print(f"\nResults saved to:")
print(f"- Table: {table_filename}")
print(f"- Plot: {plot_filename}")
