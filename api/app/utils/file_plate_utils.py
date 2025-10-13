import math

def get_well_position(index, format):
    wells = []
    plate_type = int(format.split('-')[0])
    order = format.split('-')[1]

    if plate_type == 96:
        rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        cols = list(range(1, 13))
        if order == 'column':
            for col in cols:
                for row in rows:
                    wells.append(f"{row}{col}")
        else: # row
            for row in rows:
                for col in cols:
                    wells.append(f"{row}{col}")
    elif plate_type == 384:
        rows = [chr(i) for i in range(ord('A'), ord('A') + 16)]
        cols = list(range(1, 25))
        if order == 'column':
            for col in cols:
                for row in rows:
                    wells.append(f"{row}{col}")
        else: # row
            for row in rows:
                for col in cols:
                    wells.append(f"{row}{col}")
    else:
        print("Invalid well format selected.")
        return ''
    return wells[index] if index < len(wells) else ''

def generate_list(oligos, well_format):
    formatted_oligos = []
    plate_number = 1
    oligo_index = 0

    def sort_key(oligo):
        index_num = lambda label: int(label.split('_')[1])
        orientation = lambda label: "FF" if label.startswith("FF") else "RC"
        a_num = index_num(oligo['label'])
        a_orient = orientation(oligo['label'])
        return (oligo['fragment'], a_num, 0 if a_orient == 'FF' else 1)

    flat_oligos = sorted(oligos, key=sort_key)

    plate_size = int(well_format.split('-')[0])

    for oligo in flat_oligos:
        if oligo_index >= plate_size:
            oligo_index = 0
            plate_number += 1
        formatted_oligos.append({
            'plate': plate_number,
            'well': get_well_position(oligo_index, well_format),
            'label': oligo['label'],
            'sequence': oligo['sequence'],
            'length': oligo['length'],
            'fragment': oligo['fragment']
        })
        oligo_index += 1

    return formatted_oligos

def get_fragment_destination_map(generated_oligos, dest_well_format):
    well_capacity = int(dest_well_format.split('-')[0])
    dest_plate_index = 1
    current_well_index = 0
    fragment_destination_map = {}

    fragments_by_sequence = {}
    for oligo in generated_oligos:
        sequence_id = oligo.get('fragment', 'unknown_sequence')
        if sequence_id not in fragments_by_sequence:
            fragments_by_sequence[sequence_id] = []
        fragments_by_sequence[sequence_id].append(oligo)

    for sequence_id in fragments_by_sequence.keys():
        if current_well_index >= well_capacity:
            dest_plate_index += 1
            current_well_index = 0
        dest_well = get_well_position(current_well_index, dest_well_format)
        dest_plate = f"Destination_Plate_{dest_plate_index}"
        fragment_destination_map[sequence_id] = {'plate': dest_plate, 'well': dest_well}
        current_well_index += 1

    return fragment_destination_map

def generate_primer_list(primers, well_format):
    formatted_primers = []
    plate_number = 1
    primer_index = 0

    plate_size = int(well_format.split('-')[0])

    for primer in primers:
        if primer_index >= plate_size:
            primer_index = 0
            plate_number += 1
        formatted_primers.append({
            'plate': f"Primer_Plate_{plate_number}",
            'well': get_well_position(primer_index, well_format),
            'label': primer['label'],
            'sequence': primer['sequence'],
            'length': primer['length'],
            'fragment': primer['fragment']
        })
        primer_index += 1

    return formatted_primers

def generate_dilution_plate_csv(fragments):
    headers = ["Plate Source", "Well Source", "Plate Destination", "Well Destination", "Volume Transfer"]
    rows = [headers]

    for fragment in fragments:
        plate_source = f"Plate_{fragment['plate']}"
        well_source = fragment['well']
        plate_destination = f"Working_Plate{fragment['plate']}"
        well_destination = well_source
        volume_transfer = 10

        rows.append([plate_source, well_source, plate_destination, well_destination, volume_transfer])

    return "\n".join([",".join(map(str, row)) for row in rows])

def download_csv(generated_oligos, well_format, sequence_name):
    if not generated_oligos:
        return "No oligos to download."
    
    list_data = generate_list(generated_oligos, well_format)
    
    header = ["Plate", "Well", "Name", "Sequence", "Length"]
    csv_rows = [",".join(header)]
    for item in list_data:
        csv_rows.append(",".join(map(str, [
            item['plate'],
            item['well'],
            item['label'],
            item['sequence'],
            item['length']
        ])))

    csv_string = "\n".join(csv_rows)
    return csv_string

def download_primers_csv(generated_primers, generated_oligos, well_format, dest_well_format, sequence_name):
    if not generated_primers or not any(generated_primers.values()):
        return "No primers to download."

    primers_to_pool = []
    for fragment, primers in generated_primers.items():
        forward_primer = primers.get('forward_primer')
        reverse_primer = primers.get('reverse_primer')
        if forward_primer:
            primers_to_pool.append({
                'label': f"{fragment}_FP",
                'sequence': forward_primer,
                'length': len(forward_primer),
                'fragment': fragment
            })
        if reverse_primer:
            primers_to_pool.append({
                'label': f"{fragment}_RP",
                'sequence': reverse_primer,
                'length': len(reverse_primer),
                'fragment': fragment
            })

    primer_source_list = generate_primer_list(primers_to_pool, well_format)
    fragment_destination_map = get_fragment_destination_map(generated_oligos, dest_well_format)

    header = ["Plate Source", "Well Source", "Name", "Sequence", "Plate Destination", "Well Destination"]
    csv_rows = [",".join(header)]

    for primer in primer_source_list:
        destination = fragment_destination_map.get(primer['fragment'])
        if destination:
            csv_rows.append(",".join(map(str, [
                primer['plate'],
                primer['well'],
                primer['label'],
                primer['sequence'],
                destination['plate'],
                destination['well']
            ])))

    csv_string = "\n".join(csv_rows)
    return csv_string

def download_pooling_and_dilution_plate_files(generated_oligos, well_format, dest_well_format):
    if not generated_oligos:
        return "No oligos to download."

    all_formatted_fragments = generate_list(generated_oligos, well_format)

    pooling_headers = ["Plate Source", "Well Source", "Sequence", "Plate Destination", "Well Destination", "Volume Transfer"]
    pooling_rows = []
    well_capacity = int(dest_well_format.split('-')[0])
    dest_plate_index = 1
    current_well_index = 0

    fragments_by_sequence = {}
    for fragment in all_formatted_fragments:
        sequence_id = fragment.get('fragment', 'unknown_sequence')
        if sequence_id not in fragments_by_sequence:
            fragments_by_sequence[sequence_id] = []
        fragments_by_sequence[sequence_id].append(fragment)

    for sequence_id, fragments in fragments_by_sequence.items():
        if current_well_index >= well_capacity:
            dest_plate_index += 1
            current_well_index = 0
        dest_well = get_well_position(current_well_index, dest_well_format)
        dest_plate = f"Destination_Plate_{dest_plate_index}"

        for fragment in fragments:
            pooling_rows.append([
                f"Plate_{fragment['plate']}",
                fragment['well'],
                fragment['sequence'],
                dest_plate,
                dest_well,
                2
            ])
        current_well_index += 1
    pooling_csv_content = "\n".join([",".join(map(str, row)) for row in ([pooling_headers] + pooling_rows)])

    dilution_plate_csv_content = generate_dilution_plate_csv(all_formatted_fragments)

    return {
        "pooling.csv": pooling_csv_content,
        "Dilution_Plate.csv": dilution_plate_csv_content
    }
