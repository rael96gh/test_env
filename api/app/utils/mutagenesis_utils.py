import itertools

GENETIC_CODE = {
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A', 'AGA': 'R', 'AGG': 'R', 'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
    'AAC': 'N', 'AAT': 'N', 'GAC': 'D', 'GAT': 'D', 'TGC': 'C', 'TGT': 'C', 'GAA': 'E', 'GAG': 'E', 'CAA': 'Q', 'CAG': 'Q',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G', 'CAC': 'H', 'CAT': 'H', 'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'TTA': 'L',
    'TTG': 'L', 'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L', 'AAA': 'K', 'AAG': 'K', 'ATG': 'M', 'TTC': 'F', 'TTT': 'F',
    'CCC': 'P', 'CCT': 'P', 'CCA': 'P', 'CCG': 'P', 'AGC': 'S', 'AGT': 'S', 'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
    'ACC': 'T', 'ACG': 'T', 'ACT': 'T', 'ACA': 'T', 'TGG': 'W', 'TAC': 'Y', 'TAT': 'Y', 'GTA': 'V', 'GTC': 'V', 'GTG': 'V',
    'GTT': 'V', 'TAA': '*', 'TAG': '*', 'TGA': '*'
}

REVERSE_GENETIC_CODE = {}
for codon, aa in GENETIC_CODE.items():
    if aa not in REVERSE_GENETIC_CODE:
        REVERSE_GENETIC_CODE[aa] = []
    REVERSE_GENETIC_CODE[aa].append(codon)

def contains_stop_codon(sequence):
    for i in range(0, len(sequence), 3):
        codon = sequence[i:i+3]
        if GENETIC_CODE.get(codon) == '*':
            return True
    return False

def generate_custom_mutagenesis(original_sequence, original_name, mutations, generation_mode):
    if generation_mode == 'individual':
        all_generated_variants = set()
        for mut in mutations:
            if mut['type'] == 'N':
                index = mut['pos'] - 1
                if 0 <= index < len(original_sequence):
                    original_nucleotide = original_sequence[index]
                    for new_nuc in mut['new']:
                        new_sequence = original_sequence[:index] + new_nuc + original_sequence[index + 1:]
                        variant_name = f"{original_name}_{original_nucleotide}{mut['pos']}{new_nuc}"
                        all_generated_variants.add(f">{variant_name}\n{new_sequence}")
            elif mut['type'] == 'AA':
                start_index = (mut['pos'] - 1) * 3
                if 0 <= start_index + 3 <= len(original_sequence):
                    original_codon = original_sequence[start_index:start_index + 3]
                    original_aa = GENETIC_CODE.get(original_codon, '?')
                    for target_aa in mut['new']:
                        new_codons = REVERSE_GENETIC_CODE.get(target_aa)
                        if new_codons:
                            new_codon = new_codons[0]
                            new_sequence = original_sequence[:start_index] + new_codon + original_sequence[start_index + 3:]
                            variant_name = f"{original_name}_{original_aa}{mut['pos']}{target_aa}"
                            all_generated_variants.add(f">{variant_name}\n{new_sequence}")
        return list(all_generated_variants)
    else: # group
        current_sequence = original_sequence
        current_name = original_name
        sorted_mutations = sorted(mutations, key=lambda x: x['pos'])

        for mut in sorted_mutations:
            new_value = mut['new'][0]
            if not new_value:
                continue

            if mut['type'] == 'N':
                index = mut['pos'] - 1
                if 0 <= index < len(current_sequence):
                    original_nucleotide = current_sequence[index]
                    current_sequence = current_sequence[:index] + new_value + current_sequence[index + 1:]
                    current_name += f"{original_nucleotide}{mut['pos']}{new_value}"
            elif mut['type'] == 'AA':
                start_index = (mut['pos'] - 1) * 3
                if 0 <= start_index + 3 <= len(current_sequence):
                    original_codon = current_sequence[start_index:start_index + 3]
                    original_aa = GENETIC_CODE.get(original_codon, '?')
                    new_codons = REVERSE_GENETIC_CODE.get(new_value)
                    if new_codons:
                        new_codon = new_codons[0]
                        current_sequence = current_sequence[:start_index] + new_codon + current_sequence[start_index + 3:]
                        current_name += f"{original_aa}{mut['pos']}{new_value}"
        return [f">{current_name}\n{current_sequence}"]

def generate_saturation_mutagenesis(sequences, saturation_mutations, exclude_stops, generation_mode='individual'):
    if generation_mode == 'group':
        # Assuming one sequence for combinatorial generation
        original_sequence = sequences[0]['seq']
        original_name = sequences[0]['name']
        
        mutation_sites = []
        for mut in saturation_mutations:
            pos_index = mut['pos'] - 1
            if mut['type'] == 'N':
                substitutions = ['A', 'T', 'G', 'C']
                mutation_sites.append([(pos_index, sub) for sub in substitutions])
            elif mut['type'] == 'AA':
                amino_acids_to_use = 'ACDEFGHIKLMNPQRSTVWY' if exclude_stops else 'ACDEFGHIKLMNPQRSTVWY*'
                codons = []
                for aa in amino_acids_to_use:
                    codons.extend(REVERSE_GENETIC_CODE.get(aa, []))
                mutation_sites.append([(pos_index, sub) for sub in codons])

        all_combinations = list(itertools.product(*mutation_sites))
        
        all_generated_variants = set()
        for combination in all_combinations:
            new_sequence = list(original_sequence)
            name_parts = [original_name]
            for pos_index, sub in combination:
                if len(sub) == 1: # Nucleotide
                    original_char = original_sequence[pos_index]
                    new_sequence[pos_index] = sub
                    name_parts.append(f"{original_char}{pos_index + 1}{sub}")
                else: # Codon
                    original_codon = original_sequence[pos_index*3:pos_index*3+3]
                    original_aa = GENETIC_CODE.get(original_codon, '?')
                    new_aa = GENETIC_CODE.get(sub, '?')
                    new_sequence[pos_index*3:pos_index*3+3] = sub
                    name_parts.append(f"{original_aa}{pos_index + 1}{new_aa}")

            variant_name = "_".join(name_parts)
            all_generated_variants.add(f">{variant_name}\n{' '.join(new_sequence)}")
        
        return list(all_generated_variants)

    elif generation_mode == 'group_degenerate':
        # This mode is intended for AA saturation
        if not all(mut['type'] == 'AA' for mut in saturation_mutations):
            return [] # Return empty if not all mutations are AA type

        original_sequence = sequences[0]['seq']
        original_name = sequences[0]['name']
        new_sequence = list(original_sequence)
        
        position_names = []
        for mut in saturation_mutations:
            pos_index = mut['pos'] - 1
            start_index = pos_index * 3
            if 0 <= start_index + 3 <= len(new_sequence):
                new_sequence[start_index:start_index+3] = ['N', 'N', 'K']
                position_names.append(str(mut['pos']))

        variant_name = f">{original_name}_SAT-{','.join(position_names)}-NNK"
        return [f"{variant_name}\n{' '.join(new_sequence)}"]

    # Individual mode (default)
    all_generated_variants = set()
    amino_acids_with_stop = 'ACDEFGHIKLMNPQRSTVWY*'
    amino_acids_without_stop = 'ACDEFGHIKLMNPQRSTVWY'
    nucleotides = 'ATGC'

    amino_acids_to_use = amino_acids_without_stop if exclude_stops else amino_acids_with_stop

    for seq_obj in sequences:
        sequence = seq_obj.get('seq', '')
        name = seq_obj.get('name', 'sequence')

        if not sequence:
            continue

        for mut in saturation_mutations:
            if mut['type'] == 'N':
                index = mut['pos'] - 1
                if 0 <= index < len(sequence):
                    original_nucleotide = sequence[index]
                    for new_nuc in nucleotides:
                        if new_nuc != original_nucleotide:
                            new_sequence = sequence[:index] + new_nuc + sequence[index + 1:]
                            variant_name = f"{name}_N{mut['pos']}{new_nuc}"
                            all_generated_variants.add(f">{variant_name}\n{new_sequence}")

            elif mut['type'] == 'AA':
                complete_codons = len(sequence) // 3
                if mut['pos'] > complete_codons:
                    continue

                start_index = (mut['pos'] - 1) * 3
                if 0 <= start_index + 3 <= len(sequence):
                    original_codon = sequence[start_index:start_index + 3]
                    original_aa = GENETIC_CODE.get(original_codon, '?')

                    for target_aa in amino_acids_to_use:
                        if target_aa == original_aa:
                            continue
                        target_codons = REVERSE_GENETIC_CODE.get(target_aa, [])
                        for new_codon in target_codons:
                            new_sequence = sequence[:start_index] + new_codon + sequence[start_index + 3:]
                            variant_name = f"{name}_{original_aa}{mut['pos']}{target_aa}"
                            all_generated_variants.add(f">{variant_name}\n{new_sequence}")
                            break # Use first codon only for individual mode to avoid too many redundant sequences

    return list(all_generated_variants)

def generate_scanning_library(sequence, sequence_name, start_position, end_position, full_sequence, library_type):
    nucleotide_sequence = ''.join(filter(str.isalpha, sequence))
    sequence_length = len(nucleotide_sequence)
    triplet_replacement = 'NNN' if library_type == 'NNN' else 'NNK'
    final_variants = []

    if full_sequence:
        variants = []
        for i in range(0, sequence_length - 2, 3):
            mutated_sequence = list(nucleotide_sequence)
            mutated_sequence[i:i+3] = list(triplet_replacement)
            variants.append("".join(mutated_sequence))
        for i, variant in enumerate(variants):
            final_variants.append(f">{sequence_name}_{i+1}\n{variant}")
        return final_variants

    if not all([start_position, end_position]):
        return []

    if start_position < 1 or end_position > sequence_length or start_position > end_position:
        return []

    variants = []
    triplet_length = 3

    for i in range(start_position - 1, end_position - triplet_length + 1, triplet_length):
        mutated_sequence = list(nucleotide_sequence)
        mutated_sequence[i:i+triplet_length] = list(triplet_replacement)
        variants.append("".join(mutated_sequence))
    
    for i, variant in enumerate(variants):
        final_variants.append(f">{sequence_name}_{i+1}\n{variant}")

    return final_variants
