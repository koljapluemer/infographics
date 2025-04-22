import json
from datetime import datetime
from dateutil import parser

# Define the cutoff date (March 24, 2025 at 1 PM GMT+1 = 12:00 UTC)
CUTOFF_DATE = parser.parse("2025-03-24T12:00:00Z")

def filter_entries(input_file, output_file):
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Filter entries after the cutoff date
    filtered_data = {}
    for entry_id, entry in data.items():
        entry_date = parser.parse(entry['timestamp'])
        if entry_date > CUTOFF_DATE:
            filtered_data[entry_id] = entry
    
    # Write the filtered data to the output file
    with open(output_file, 'w') as f:
        json.dump(filtered_data, f, indent=2)
    
    print(f"Original entries: {len(data)}")
    print(f"Filtered entries: {len(filtered_data)}")

if __name__ == "__main__":
    input_file = "data/full/learning_data.json"
    output_file = "data/full/learning_data_after_cutoff.json"
    filter_entries(input_file, output_file) 