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

def generate_saturation_mutagenesis(sequences, saturation_mutations, exclude_stops):
    all_generated_variants = set()
    amino_acids_with_stop = 'ACDEFGHIKLMNPQRSTVWY*'
    amino_acids_without_stop = 'ACDEFGHIKLMNPQRSTVWY'
    nucleotides = 'ATGC'

    amino_acids_to_use = amino_acids_without_stop if exclude_stops else amino_acids_with_stop

    for seq_obj in sequences:
        for mut in saturation_mutations:
            if mut['type'] == 'N':
                index = mut['pos'] - 1
                if 0 <= index < len(seq_obj['sequence']):
                    original_nucleotide = seq_obj['sequence'][index]
                    for new_nuc in nucleotides:
                        if new_nuc != original_nucleotide:
                            new_sequence = seq_obj['sequence'][:index] + new_nuc + seq_obj['sequence'][index + 1:]
                            if exclude_stops and contains_stop_codon(new_sequence):
                                continue
                            variant_name = f"{seq_obj['name']}_N{mut['pos']}{new_nuc}"
                            all_generated_variants.add(f">{variant_name}\n{new_sequence}")
            elif mut['type'] == 'AA':
                if len(seq_obj['sequence']) % 3 != 0:
                    continue
                start_index = (mut['pos'] - 1) * 3
                if 0 <= start_index + 3 <= len(seq_obj['sequence']):
                    original_codon = seq_obj['sequence'][start_index:start_index + 3]
                    original_aa = GENETIC_CODE.get(original_codon, '?')

                    for target_aa in amino_acids_to_use:
                        if target_aa == original_aa:
                            continue
                        target_codons = REVERSE_GENETIC_CODE.get(target_aa, [])
                        for new_codon in target_codons:
                            new_sequence = seq_obj['sequence'][:start_index] + new_codon + seq_obj['sequence'][start_index + 3:]
                            variant_name = f"{seq_obj['name']}_{original_aa}{mut['pos']}{target_aa}"
                            all_generated_variants.add(f">{variant_name}\n{new_sequence}")
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
