
import pandas as pd

def recycle_oligos(fragments_df, pooling_df):
    """
    Recycles oligos by deduplicating and re-ordering them, then generates a new pooling file.

    Args:
        fragments_df (pd.DataFrame): DataFrame with fragment data, including 'Sequence', 'Plate', 'Well', 'Length'.
        pooling_df (pd.DataFrame): DataFrame with pooling data, including 'Plate Source', 'Well Source', 'Sequence', 'Plate Destination', 'Well Destination'.

    Returns:
        tuple: A tuple containing:
            - oligos_to_order_df (pd.DataFrame): The final list of unique oligos with their new plate and well locations.
            - reduced_pooling_df (pd.DataFrame): The new, reduced pooling file.
    """
    if 'Sequence' not in fragments_df.columns:
        raise ValueError("The fragments DataFrame must contain a 'Sequence' column.")
    fragments_df['Sequence'] = fragments_df['Sequence'].astype(str).str.strip().str.upper()

    required_columns = {'Sequence', 'Plate', 'Well', 'Length'}
    if not required_columns.issubset(fragments_df.columns):
        raise ValueError(f"Missing required columns in fragments_df. Expected: {required_columns}")

    # De-duplicate based on Sequence and Plate
    deduplicated_df = fragments_df.drop_duplicates(subset=['Sequence', 'Plate'], keep='first').reset_index(drop=True)

    # Assign new Well IDs and Plate numbers for ordering (column-wise)
    rows, cols = 8, 12  # 96-well plate
    max_wells_per_plate = rows * cols
    total_fragments = len(deduplicated_df)

    def generate_column_wise_wells(rows=8, cols=12):
        row_letters = [chr(65 + i) for i in range(rows)]
        col_numbers = list(range(1, cols + 1))
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

    # Create mapping from (Sequence, Plate) to new well/plate
    sequence_plate_to_ordered = deduplicated_df.set_index(['Sequence', 'Plate'])[
        ['Order Plate Source', 'Ordered Source Well']
    ].to_dict('index')

    # Update original fragments with ordered location
    fragments_df[['Order Plate Source', 'Ordered Source Well']] = fragments_df.apply(
        lambda row: pd.Series(sequence_plate_to_ordered.get((row['Sequence'], row['Plate']), (None, None))),
        axis=1
    )

    # Load and validate pooling
    required_pooling_cols = {'Plate Source', 'Well Source', 'Sequence', 'Plate Destination', 'Well Destination'}
    if not required_pooling_cols.issubset(pooling_df.columns):
        raise ValueError(f"Missing required columns in pooling_df. Expected: {required_pooling_cols}")

    # Map pooling source info
    def map_to_ordered(row):
        key = (row['Sequence'].strip().upper(), row['Plate Source'])
        if key in sequence_plate_to_ordered:
            return pd.Series([
                sequence_plate_to_ordered[key]['Order Plate Source'],
                sequence_plate_to_ordered[key]['Ordered Source Well']
            ])
        return pd.Series([row['Plate Source'], row['Well Source']])

    pooling_df[['Ordered Plate Source', 'Ordered Well Source']] = pooling_df.apply(map_to_ordered, axis=1)

    # De-duplicate based on mapped values
    reduced_pooling_df = pooling_df.drop_duplicates(
        subset=['Ordered Plate Source', 'Ordered Well Source', 'Plate Destination', 'Well Destination']
    ).reset_index(drop=True)

    # Create oligos_to_order.csv with updated Plate and Well for continuity
    oligos_to_order_df = deduplicated_df.copy()
    oligos_to_order_df['Plate'] = deduplicated_df['Order Plate Source']
    oligos_to_order_df['Well'] = deduplicated_df['Ordered Source Well']
    
    return oligos_to_order_df, reduced_pooling_df
