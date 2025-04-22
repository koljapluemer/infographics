import json
from collections import defaultdict

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Load the geo.json file
with open('data/full/worldmap.json', 'r') as f:
    geo_data = json.load(f)

# Create a mapping of country names to their regions
country_to_region = {}
for feature in geo_data['features']:
    country_name = feature['properties']['name']
    region = feature['properties']['subregion']
    country_to_region[country_name] = region

# Initialize counters for each country
country_stats = defaultdict(lambda: {'total': 0, 'wrong': 0})

# Process each entry
for entry in data.values():
    country = entry['country']
    country_stats[country]['total'] += 1
    if entry['numberOfClicksNeeded'] > 1:
        country_stats[country]['wrong'] += 1

# Calculate percentages and group by region
region_stats = defaultdict(list)
for country, stats in country_stats.items():
    if stats['total'] >= 5:  # Only consider countries with at least 5 attempts
        percentage_wrong = (stats['wrong'] / stats['total']) * 100
        region = country_to_region.get(country, 'Unknown')
        region_stats[region].append({
            'country': country,
            'percentage_wrong': percentage_wrong,
            'total_attempts': stats['total'],
            'wrong_attempts': stats['wrong']
        })

# Find worst performing country per region
worst_per_region = {}
for region, countries in region_stats.items():
    if countries:  # Only process regions that have countries with enough attempts
        worst_country = max(countries, key=lambda x: x['percentage_wrong'])
        worst_per_region[region] = worst_country

# Sort regions alphabetically
sorted_regions = sorted(worst_per_region.items())

# Print results
print("\nMost Often Clicked Wrong Per Region")
print("----------------------------------")
for region, stats in sorted_regions:
    print(f"{region}: {stats['country']} ({stats['percentage_wrong']:.1f}%)")
