import json

# Load worldmap data to get valid countries
with open('data/full/worldmap.geo.json', 'r') as f:
    worldmap_data = json.load(f)

# Create set of valid country names from admin field
valid_countries = set()
for feature in worldmap_data['features']:
    if 'properties' in feature and 'admin' in feature['properties']:
        valid_countries.add(feature['properties']['admin'])

# Load learning data
with open('data/full/learning_data.json', 'r') as f:
    data = json.load(f)

# Filter entries
filtered_data = {}
invalid_countries = set()
for entry_id, entry in data.items():
    if entry['country'] in valid_countries:
        filtered_data[entry_id] = entry
    else:
        invalid_countries.add(entry['country'])

# Save filtered data
with open('data/full/learning_data_after_cutoff.json', 'w') as f:
    json.dump(filtered_data, f, indent=2)

# Print summary
print(f"Original entries: {len(data)}")
print(f"Filtered entries: {len(filtered_data)}")
print(f"Removed entries: {len(data) - len(filtered_data)}")
print(f"Invalid countries: {sorted(invalid_countries)}") 