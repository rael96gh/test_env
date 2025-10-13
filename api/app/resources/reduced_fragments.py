import pandas as pd

def find_duplicate_sequences(sequences):
    # Dictionary to store unique sequences and their first occurrence index
    unique_sequences = {}
    duplicates_map = {}

    # Populate dictionary with unique sequences and map duplicate indices
    for index, seq in enumerate(sequences):
        if seq in unique_sequences:
            # If sequence is already seen, store its duplicate index
            duplicates_map[index] = unique_sequences[seq]
        else:
            # Record the first occurrence of the sequence
            unique_sequences[seq] = index

    return unique_sequences, duplicates_map

# Load the CSV file and extract the 'Sequence' column
file_path = "C:\\Users\\raela\\OneDrive\\Documents\\recycling_csv_files\\Test\\fragments.csv"
data = pd.read_csv(file_path)

# Extract sequences and find duplicates
sequences = data["Sequence"].tolist()
unique_sequences, duplicates_map = find_duplicate_sequences(sequences)

# Keep only rows with unique sequences
unique_indices = list(unique_sequences.values())
reduced_data = data.loc[unique_indices].reset_index(drop=True)

# Save reduced data to a new CSV file
reduced_file_path = "C:\\Users\\raela\\OneDrive\\Documents\\recycling_csv_files\\reduced_fragments.csv"
reduced_data.to_csv(reduced_file_path, index=False)

print(f"Reduced CSV file created at: {reduced_file_path}")
