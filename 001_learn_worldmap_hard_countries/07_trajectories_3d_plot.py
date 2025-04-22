import json
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from mpl_toolkits.mplot3d import Axes3D

# Configuration
MAX_ATTEMPTS = 10  # Maximum number of attempts to analyze

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Group attempts by country and deviceId
country_attempts = defaultdict(lambda: defaultdict(list))

# Process each entry
for entry in data.values():
    country = entry['country']
    device_id = entry['deviceId']
    timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
    country_attempts[country][device_id].append({
        'timestamp': timestamp,
        'incorrect': entry['numberOfClicksNeeded'] > 1
    })

# Sort attempts by timestamp for each user and country
for country in country_attempts:
    for device_id in country_attempts[country]:
        country_attempts[country][device_id].sort(key=lambda x: x['timestamp'])

# Calculate percentage incorrect for each attempt number for each country
country_stats = {}

for country, user_attempts in country_attempts.items():
    attempt_incorrect = defaultdict(lambda: {'total': 0, 'incorrect': 0})
    
    for attempts in user_attempts.values():
        for i, attempt in enumerate(attempts, 1):
            if i <= MAX_ATTEMPTS:
                attempt_incorrect[i]['total'] += 1
                if attempt['incorrect']:
                    attempt_incorrect[i]['incorrect'] += 1
    
    # Only include countries with enough data
    if attempt_incorrect[1]['total'] >= 5:  # At least 5 users
        percentages = []
        for attempt_num in range(1, MAX_ATTEMPTS + 1):
            if attempt_incorrect[attempt_num]['total'] > 0:
                percentage = (attempt_incorrect[attempt_num]['incorrect'] / 
                            attempt_incorrect[attempt_num]['total']) * 100
                percentages.append(percentage)
            else:
                percentages.append(np.nan)
        
        country_stats[country] = {
            'first_attempt_percentage': percentages[0],
            'percentages': percentages
        }

# Sort countries by their first attempt performance (descending order - best to worst)
sorted_countries = sorted(country_stats.items(), 
                        key=lambda x: x[1]['first_attempt_percentage'],
                        reverse=True)  # Sort from best to worst

# Prepare data for 3D plot
countries = [country for country, _ in sorted_countries]
attempts = range(1, MAX_ATTEMPTS + 1)
X, Y = np.meshgrid(range(len(countries)), attempts)

# Create Z matrix (percentages)
Z = np.array([stats['percentages'] for _, stats in sorted_countries]).T

# Create 3D plot
fig = plt.figure(figsize=(15, 10))
ax = fig.add_subplot(111, projection='3d')

# Create surface plot
surf = ax.plot_surface(X, Y, Z, cmap='viridis_r', edgecolor='none', alpha=0.8)

# Customize the plot
ax.set_xlabel('Countries (sorted by first attempt performance)')
ax.set_ylabel('Attempt Number')
ax.set_zlabel('Percentage Incorrect (%)')
ax.set_title('Learning Trajectories Across Countries')

# Add colorbar
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Percentage Incorrect (%)')

# Set x-axis ticks to show country names
ax.set_xticks(range(len(countries)))
ax.set_xticklabels(countries, rotation=45, ha='right')

# Adjust layout
plt.tight_layout()

# Save plot
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/learning_trajectories_3d.png', bbox_inches='tight', dpi=300)
plt.close()

# Print summary statistics
print("\nSummary Statistics:")
print("------------------")
print(f"Total countries analyzed: {len(countries)}")
print("\nTop 5 countries (best first attempt):")
for country, stats in sorted_countries[:5]:
    print(f"{country}: {stats['first_attempt_percentage']:.1f}% incorrect")

print("\nBottom 5 countries (worst first attempt):")
for country, stats in sorted_countries[-5:]:
    print(f"{country}: {stats['first_attempt_percentage']:.1f}% incorrect")

print(f"\nPlot saved to: plots/learning_trajectories_3d.png")
