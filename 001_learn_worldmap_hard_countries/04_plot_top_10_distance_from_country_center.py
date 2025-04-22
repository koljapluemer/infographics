import json
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import os

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Initialize data structure to store distances for each country
country_distances = defaultdict(list)

# Process each entry
for entry in data.values():
    country = entry['country']
    distance = entry['distanceOfFirstClickToCenterOfCountry']
    country_distances[country].append(distance)

# Calculate average distances and prepare data for plotting
results = []
for country, distances in country_distances.items():
    if len(distances) >= 5:  # Only consider countries with at least 5 attempts
        avg_distance = np.mean(distances)
        results.append({
            'country': country,
            'distances': distances,
            'avg_distance': avg_distance
        })

# Sort by average distance (descending) and get top 10
top_10 = sorted(results, key=lambda x: x['avg_distance'], reverse=True)[:10]

# Prepare data for box plot
countries = [entry['country'] for entry in top_10]
distances_data = [entry['distances'] for entry in top_10]

# Create the box plot
plt.figure(figsize=(12, 6))
box = plt.boxplot(distances_data, labels=countries, patch_artist=True)

# Customize the plot
plt.title('Distribution of Distances from Country Center for Top 10 Most Challenging Countries')
plt.xlabel('Country')
plt.ylabel('Distance from Country Center (pixels)')
plt.xticks(rotation=45, ha='right')
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Color the boxes
for patch in box['boxes']:
    patch.set_facecolor('lightblue')

# Add average distance markers
for i, entry in enumerate(top_10):
    plt.plot([i+1], [entry['avg_distance']], 'r_', markersize=15, markeredgewidth=2)

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)

# Save the plot
plt.savefig('plots/top_10_distance_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()
