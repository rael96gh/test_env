import pandas as pd

# Define file paths
fragments_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\Test\fragments.csv"
pooling_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\Test\pooling.csv"
reduced_fragments_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\reduced_fragments.csv"
reduced_pooling_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\reduced_pooling.csv"
reduced_fragments_ordered_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\reduced_fragments_ordered.csv"
optimized_pooling_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\optimized_pooling.csv"

# Step 1: Load and validate fragments
fragments_df = pd.read_csv(fragments_path)
if 'Sequence' not in fragments_df.columns:
    raise ValueError("The input CSV must contain a 'Sequence' column.")
fragments_df['Sequence'] = fragments_df['Sequence'].astype(str).str.strip().str.upper()

required_columns = {'Sequence', 'Plate', 'Well', 'Length'}
if not required_columns.issubset(fragments_df.columns):
    raise ValueError(f"Missing required columns in fragments.csv. Expected: {required_columns}")

# Step 2: De-duplicate based on Sequence and Plate
deduplicated_df = fragments_df.drop_duplicates(subset=['Sequence', 'Plate'], keep='first').reset_index(drop=True)
deduplicated_df.to_csv(reduced_fragments_path, index=False)

# Step 3: Assign new Well IDs and Plate numbers for ordering (column-wise)
rows, cols = 8, 12  # 96-well plate
max_wells_per_plate = rows * cols
total_fragments = len(deduplicated_df)

def generate_column_wise_wells(rows=8, cols=12):
    row_letters = [chr(65 + i) for i in range(rows)]  # ['A', 'B', ..., 'H']
    col_numbers = list(range(1, cols + 1))           # [1, ..., 12]
    return [f"{r}{c}" for c in col_numbers for r in row_letters]

ordered_wells = []
ordered_plates = []

wells = generate_column_wise_wells(rows, cols)
for i in range(total_fragments):
    plate_number = i // max_wells_per_plate + 1
    well_index = i % max_wells_per_plate
    ordered_wells.append(wells[well_index])
    ordered_plates.append(f"Plate_{plate_number}")

deduplicated_df['Ordered Source Well'] = ordered_wells
deduplicated_df['Order Plate Source'] = ordered_plates
deduplicated_df.to_csv(reduced_fragments_ordered_path, index=False)

# Step 4: Create mapping from (Sequence, Plate) to new well/plate
sequence_plate_to_ordered = deduplicated_df.set_index(['Sequence', 'Plate'])[
    ['Order Plate Source', 'Ordered Source Well']
].to_dict('index')

# Step 5: Update original fragments with ordered location
fragments_df[['Order Plate Source', 'Ordered Source Well']] = fragments_df.apply(
    lambda row: pd.Series(sequence_plate_to_ordered.get((row['Sequence'], row['Plate']), (None, None))),
    axis=1
)

# Step 6: Load and validate pooling
pooling_df = pd.read_csv(pooling_path)
required_pooling_cols = {'Plate Source', 'Well Source', 'Sequence', 'Plate Destination', 'Well Destination'}
if not required_pooling_cols.issubset(pooling_df.columns):
    raise ValueError(f"Missing required columns in pooling.csv. Expected: {required_pooling_cols}")

# Step 7: Map pooling source info
def map_to_ordered(row):
    key = (row['Sequence'].strip().upper(), row['Plate Source'])
    if key in sequence_plate_to_ordered:
        return pd.Series([
            sequence_plate_to_ordered[key]['Order Plate Source'],
            sequence_plate_to_ordered[key]['Ordered Source Well']
        ])
    return pd.Series([row['Plate Source'], row['Well Source']])

pooling_df[['Ordered Plate Source', 'Ordered Well Source']] = pooling_df.apply(map_to_ordered, axis=1)

# Step 8: De-duplicate based on mapped values
reduced_pooling_df = pooling_df.drop_duplicates(
    subset=['Ordered Plate Source', 'Ordered Well Source', 'Plate Destination', 'Well Destination']
).reset_index(drop=True)

# Save reduced pooling
reduced_pooling_df.to_csv(reduced_pooling_path, index=False)

# Step 9: Generate optimized_pooling.csv
# Add default transfer volume if not present
if 'Volume Transfer' not in reduced_pooling_df.columns:
    reduced_pooling_df['Volume Transfer'] = 2.0  # µL, default

optimized_pooling_df = reduced_pooling_df[[
    'Ordered Plate Source',
    'Ordered Well Source',
    'Volume Transfer',
    'Well Destination'
]].copy()

# Optional: rename columns to match pooling robot requirements
optimized_pooling_df.columns = [
    'Source Plate',
    'Source Well',
    'Transfer Volume',
    'Destination Well'
]

optimized_pooling_df.to_csv(optimized_pooling_path, index=False)

# Step X: Create oligos_to_order.csv with updated Plate and Well for continuity
oligos_to_order_df = deduplicated_df.copy()
oligos_to_order_df['Plate'] = deduplicated_df['Order Plate Source']
oligos_to_order_df['Well'] = deduplicated_df['Ordered Source Well']
oligos_to_order_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\oligos_to_order.csv"
oligos_to_order_df.to_csv(oligos_to_order_path, index=False)



# Debug outputs
print("\n✔️ Reduced fragments ordered saved to:", reduced_fragments_ordered_path)
print(deduplicated_df.head())

print("\n✔️ Reduced pooling saved to:", reduced_pooling_path)
print(reduced_pooling_df.head())

print("\n✅ Optimized pooling saved to:", optimized_pooling_path)
print(optimized_pooling_df.head())

print("\n✔️ Oligos to order saved to:", oligos_to_order_path)
