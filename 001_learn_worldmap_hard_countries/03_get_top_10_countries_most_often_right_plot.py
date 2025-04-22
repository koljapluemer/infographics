import json
from collections import defaultdict
import os

# Load the learning data
with open('data/full/learning_data_after_cutoff.json', 'r') as f:
    data = json.load(f)

# Initialize data structure to store all attempts for each country
country_attempts = defaultdict(list)

# Process each entry
for entry in data.values():
    country = entry['country']
    # Store 1 for right (single click), 0 for wrong (multiple clicks)
    is_right = 1 if entry['numberOfClicksNeeded'] == 1 else 0
    country_attempts[country].append(is_right)

# Calculate statistics for each country
results = []
for country, attempts in country_attempts.items():
    if len(attempts) >= 5:  # Only consider countries with at least 5 attempts
        percentage_right = (sum(attempts) / len(attempts)) * 100
        results.append({
            'country': country,
            'percentage_right': percentage_right,
            'total_attempts': len(attempts),
            'right_attempts': sum(attempts)
        })

# Sort by percentage right (descending) and get top 10
top_10 = sorted(results, key=lambda x: x['percentage_right'], reverse=True)[:10]

# Generate LaTeX table
latex_table = """\\begin{table}[htbp]
\\centering
\\caption{Top 10 Countries Most Often Guessed Right}
\\label{tab:right-guesses}
\\begin{tabular}{lrrr}
\\toprule
Country & \\% of guesses right & N & Right \\\\
\\midrule
"""

# Add data rows
for entry in top_10:
    latex_table += f"{entry['country']} & {entry['percentage_right']:.1f} & {entry['total_attempts']} & {entry['right_attempts']} \\\\\n"

# Close the table
latex_table += """\\bottomrule
\\end{tabular}
\\end{table}"""

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)

# Save the LaTeX table to a file
with open('plots/top_10_right_guesses_table.tex', 'w') as f:
    f.write(latex_table)
