import json
from collections import defaultdict

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Initialize counters for each country
country_stats = defaultdict(lambda: {'total': 0, 'wrong': 0})

# Process each entry
for entry in data.values():
    country = entry['country']
    country_stats[country]['total'] += 1
    if entry['numberOfClicksNeeded'] > 1:
        country_stats[country]['wrong'] += 1

# Calculate percentages and prepare results
results = []
for country, stats in country_stats.items():
    if stats['total'] >= 5:  # Only consider countries with at least 5 attempts
        percentage_wrong = (stats['wrong'] / stats['total']) * 100
        results.append({
            'country': country,
            'percentage_wrong': percentage_wrong,
            'total_attempts': stats['total'],
            'wrong_attempts': stats['wrong']
        })

# Sort by percentage wrong (descending) and get top 10
top_10 = sorted(results, key=lambda x: x['percentage_wrong'], reverse=True)[:10]

# Print results
print("\nTop 10 Countries Most Often Guessed Wrong:")
print("----------------------------------------")
print(f"{'Country':<25} {'% Wrong':<10} {'Total Attempts':<15} {'Wrong Attempts':<15}")
print("-" * 65)
for entry in top_10:
    print(f"{entry['country']:<25} {entry['percentage_wrong']:.1f}%{'':<5} {entry['total_attempts']:<15} {entry['wrong_attempts']:<15}")
