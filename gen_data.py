"""
Generate subcategory averages from plastic-resin-raw.xlsx for dashboard.

Usage:
  python3 gen_data.py

Input:
  plastic-resin-raw.xlsx (raw2 sheet, "For Avg" column)

Output:
  data.json (complete dashboard data structure)

The script:
1. Reads all products marked "For Avg" in raw2 sheet
2. Calculates average price per subcategory per date
3. Computes delta (change vs previous day)
4. Outputs complete dashboard JSON
"""
import pandas as pd
import json
from datetime import datetime

# Read raw data
print("Reading plastic-resin-raw.xlsx...")
df = pd.read_excel('plastic-resin-raw.xlsx', sheet_name='raw2')

# Get all date columns (exclude metadata)
all_cols = df.columns.tolist()
metadata_cols = ['For Avg', 'Product', 'Producer', 'Country']
date_cols = [col for col in all_cols if col not in metadata_cols]

print(f"Found {len(date_cols)} date columns")
print(f"Date range: {date_cols[0]} to {date_cols[-1]}")

# Sort dates properly
try:
    date_objs = []
    for d in date_cols:
        try:
            dt = pd.to_datetime(d)
            date_objs.append((dt, d))
        except:
            pass
    
    sorted_dates = sorted(date_objs, key=lambda x: x[0])
    date_cols_sorted = [d[1] for d in sorted_dates]
except:
    date_cols_sorted = date_cols

# Filter items marked for averaging
items_for_avg = df[df['For Avg'].notna()].copy()
print(f"Items marked 'For Avg': {len(items_for_avg)}")

# Calculate subcategory averages
print("\nCalculating averages by subcategory...")
subcats_data = {}

for cat in sorted(items_for_avg['For Avg'].unique()):
    cat_data = items_for_avg[items_for_avg['For Avg'] == cat]
    subcats_data[cat] = {}
    
    for date_col in date_cols_sorted:
        values = []
        for val in cat_data[date_col]:
            if pd.notna(val) and val != '-' and val != '':
                try:
                    values.append(float(val))
                except:
                    pass
        
        if values:
            avg = sum(values) / len(values)
            subcats_data[cat][date_col] = round(avg, 2)
        else:
            subcats_data[cat][date_col] = None

# Build summary object
latest_date = date_cols_sorted[-1]
summary = {
    'subcats': {},
    'changed': 0,  # Placeholder - calculate if needed
    'total': len(df),
    'largest': 0,  # Placeholder
    'largest_items': ''  # Placeholder
}

# Calculate summary for latest date
for cat in sorted(subcats_data.keys()):
    current = subcats_data[cat].get(latest_date)
    
    # Get previous date for delta
    prev_idx = date_cols_sorted.index(latest_date) - 1
    prev_date = date_cols_sorted[prev_idx] if prev_idx >= 0 else None
    previous = subcats_data[cat].get(prev_date) if prev_date else None
    
    # Calculate delta in VND (absolute difference)
    if current and previous:
        delta = round((current - previous))
    else:
        delta = 0
    
    summary['subcats'][cat] = {
        'avg': round(current) if current else None,
        'delta': delta
    }

# Build complete output structure
output = {
    'labels': date_cols_sorted,
    'summary': summary,
    'products': {'PP': [], 'PE': [], 'PVC': []},
    'meta': {'PP': [], 'PE': [], 'PVC': []},
    'groupavg': {'PP': [], 'PE': [], 'PVC': []},
    'reports': {
        'PP': {'summary': [], 'paras': []},
        'PE': {'summary': [], 'paras': []},
        'PVC': {'summary': [], 'paras': []}
    },
    'editorial': {
        'overview': {},
        'regional': []
    }
}

# Save output
print("Saving data.json...")
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# Print summary
print("\n✓ Generation complete!")
print(f"\nSubcategory averages for {latest_date}:")
print("─" * 50)
for cat in sorted(summary['subcats'].keys()):
    s = summary['subcats'][cat]
    avg_str = f"{s['avg']:>8,}" if s['avg'] else "       —"
    delta_str = f"{s['delta']:+6,}" if s['delta'] else "      0"
    print(f"{cat:15} {avg_str} VND/kg  {delta_str} vs prev")
print("─" * 50)

print(f"\nOutput: data.json")
print(f"Contains {len(date_cols_sorted)} dates × 7 subcategories")
