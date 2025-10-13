import pandas as pd

# Define file paths
fragments_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\fragments.csv"
pooling_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\pooling.csv"
reduced_fragments_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\reduced_fragments.csv"
reduced_pooling_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\reduced_pooling.csv"
reduced_fragments_ordered_path = r"C:\Users\raela\OneDrive\Documents\recycling_csv_files\reduced_fragments_ordered.csv"

# Step 1: Load fragments.csv
fragments_df = pd.read_csv(fragments_path)

# Ensure sequences are treated as text and consistent
fragments_df['Sequence'] = fragments_df['Sequence'].str.strip().str.upper()

# Check required columns
required_columns = {'Sequence', 'Plate', 'Well', 'Length'}
if not required_columns.issubset(fragments_df.columns):
    raise ValueError(f"Missing required columns in fragments.csv. Expected: {required_columns}")

# Step 2: Deduplicate based on Sequence and Length
# Create a mapping to track the first occurrence of each Sequence and Length
first_occurrence_mapping = {}

# Iterate through the fragments and map duplicates to the first occurrence
for idx, row in fragments_df.iterrows():
    key = (row['Sequence'], row['Length'])  # Use Sequence and Length as a unique identifier
    if key not in first_occurrence_mapping:
        # Record the first occurrence
        first_occurrence_mapping[key] = (row['Plate'], row['Well'])
    else:
        # Update Plate and Well for duplicates to point to the first occurrence
        first_plate, first_well = first_occurrence_mapping[key]
        fragments_df.at[idx, 'Plate'] = first_plate
        fragments_df.at[idx, 'Well'] = first_well

# Deduplicate the fragments DataFrame based on the updated Plate and Well columns
deduplicated_df = fragments_df.drop_duplicates(
    subset=['Sequence', 'Length', 'Plate', 'Well'],
    keep='first'
).reset_index(drop=True)

# Save reduced fragments to reduced_fragments.csv
deduplicated_df.to_csv(reduced_fragments_path, index=False)

# Step 3: Assign new Well IDs and Plate numbers for ordering
rows, cols = 8, 12  # Standard plate dimensions (8 rows, 12 columns)
max_wells_per_plate = rows * cols
total_fragments = len(deduplicated_df)

new_well_ids = []
new_plate_numbers = []

for i in range(total_fragments):
    plate_number = i // max_wells_per_plate + 1
    well_index = i % max_wells_per_plate
    col_number = (well_index // rows) + 1         # Column number (1-12)
    row_letter = chr(65 + (well_index % rows))    # Row letter (A-H)
    new_well_id = f"{row_letter}{col_number}"
    new_well_ids.append(new_well_id)
    new_plate_numbers.append(f"Plate_{plate_number}")

deduplicated_df['Ordered Source Well'] = new_well_ids
deduplicated_df['Order Plate Source'] = new_plate_numbers

# Create a mapping for Sequence and Plate to Ordered Source
sequence_plate_to_ordered_source = deduplicated_df.set_index(['Sequence', 'Plate'])[
    ['Order Plate Source', 'Ordered Source Well']
].to_dict('index')

# Save ordered reduced fragments
deduplicated_df.to_csv(reduced_fragments_ordered_path, index=False)

# Step 4: Map original fragments to their ordered counterparts
# Add mapping back to fragments_df
fragments_df[['Order Plate Source', 'Ordered Source Well']] = fragments_df.apply(
    lambda row: pd.Series(sequence_plate_to_ordered_source.get((row['Sequence'], row['Plate']), (None, None))),
    axis=1
)

# Step 5: Process pooling.csv and map to ordered sources
pooling_df = pd.read_csv(pooling_path)

# Ensure required columns exist in pooling_df
required_pooling_columns = {'Plate Source', 'Well Source', 'Sequence', 'Plate Destination', 'Well Destination'}
if not required_pooling_columns.issubset(pooling_df.columns):
    raise ValueError(f"Missing required columns in pooling.csv. Expected: {required_pooling_columns}")

# Function to map Plate Source and Well Source to Ordered Source
def map_ordered_source(row):
    plate, sequence = row['Plate Source'], row['Sequence']
    key = (sequence, plate)  # Use both Sequence and Plate
    if key in sequence_plate_to_ordered_source:
        source = sequence_plate_to_ordered_source[key]
        return source['Order Plate Source'], source['Ordered Source Well']
    return plate, row['Well Source']

# Map to ordered sources
pooling_df[['Ordered Plate Source', 'Ordered Well Source']] = pooling_df.apply(
    lambda row: pd.Series(map_ordered_source(row)), axis=1
)

# Deduplicate pooling data
reduced_pooling_df = pooling_df.drop_duplicates(
    subset=['Ordered Plate Source', 'Ordered Well Source', 'Plate Destination', 'Well Destination']
).reset_index(drop=True)

# Save reduced pooling data
reduced_pooling_df.to_csv(reduced_pooling_path, index=False)

# Debugging: Print outputs to verify
print("\nReduced fragments ordered:")
print(deduplicated_df)

print("\nReduced pooling data:")
print(reduced_pooling_df)
