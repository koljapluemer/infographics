import json
from collections import defaultdict

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Load the geo.json file
with open('data/full/worldmap.geo.json', 'r') as f:
    geo_data = json.load(f)

# Create a mapping of country names to their regions
country_to_regions = {}
for feature in geo_data['features']:
    country_name = feature['properties']['name']
    region_un = feature['properties']['region_un']
    subregion = feature['properties']['subregion']
    country_to_regions[country_name] = (region_un, subregion)

# Initialize counters for each country
country_stats = defaultdict(lambda: {'total': 0, 'wrong': 0})

# Process each entry
for entry in data.values():
    country = entry['country']
    country_stats[country]['total'] += 1
    if entry['numberOfClicksNeeded'] > 1:
        country_stats[country]['wrong'] += 1

# Calculate percentages and group by regions
region_stats = defaultdict(lambda: defaultdict(list))
for country, stats in country_stats.items():
    if stats['total'] >= 5:  # Only consider countries with at least 5 attempts
        percentage_wrong = (stats['wrong'] / stats['total']) * 100
        regions = country_to_regions.get(country, ('Unknown', 'Unknown'))
        region_un, subregion = regions
        region_stats[region_un][subregion].append({
            'country': country,
            'percentage_wrong': percentage_wrong,
            'total_attempts': stats['total'],
            'wrong_attempts': stats['wrong']
        })

# Find worst performing country per subregion
worst_per_subregion = {}
for region_un, subregions in region_stats.items():
    worst_per_subregion[region_un] = {}
    for subregion, countries in subregions.items():
        if countries:  # Only process subregions that have countries with enough attempts
            worst_country = max(countries, key=lambda x: x['percentage_wrong'])
            worst_per_subregion[region_un][subregion] = worst_country

# Sort regions and subregions alphabetically
sorted_regions = sorted(worst_per_subregion.items())

# Print text output
print("\nMost Often Clicked Wrong Per Region")
print("----------------------------------")
for region_un, subregions in sorted_regions:
    print(f"\n{region_un}:")
    for subregion, stats in sorted(subregions.items()):
        print(f"  {subregion}: {stats['country']} ({stats['percentage_wrong']:.1f}%)")

# Save LaTeX table
with open('plots/error_rates_by_region.tex', 'w') as f:
    f.write("\\begin{table}[h]\n")
    f.write("\\centering\n")
    f.write("\\caption{Countries with Highest Error Rates by Region and Subregion}\n")
    f.write("\\label{tab:error_rates}\n")
    f.write("\\begin{tabular}{lll}\n")
    f.write("\\toprule\n")
    f.write("Region & Subregion & Country (Error Rate) \\\\\n")
    f.write("\\midrule\n")

    for region_un, subregions in sorted_regions:
        # Print region name only once for the first subregion
        first_subregion = True
        for subregion, stats in sorted(subregions.items()):
            if first_subregion:
                f.write(f"{region_un} & {subregion} & {stats['country']} ({stats['percentage_wrong']:.1f}\\%) \\\\\n")
                first_subregion = False
            else:
                f.write(f" & {subregion} & {stats['country']} ({stats['percentage_wrong']:.1f}\\%) \\\\\n")
        
        # Add a small space between regions
        if region_un != sorted_regions[-1][0]:  # If not the last region
            f.write("\\midrule\n")

    f.write("\\bottomrule\n")
    f.write("\\end{tabular}\n")
    f.write("\\end{table}\n")
