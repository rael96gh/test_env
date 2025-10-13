from ..config.constants import H_NN, S_NN, H_INIT, S_INIT, R, H_LOOP
import math

def get_reverse_complement(sequence):
    complement = {
        'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'W': 'W', 'S': 'S',
        'M': 'K', 'K': 'M', 'R': 'Y', 'Y': 'R', 'B': 'V', 'D': 'H',
        'H': 'D', 'V': 'B', 'N': 'N'
    }
    return "".join(complement.get(base, base) for base in reversed(sequence))

def get_gc_content(seq):
    if not seq:
        return 0
    gc_count = seq.count('G') + seq.count('C')
    return (gc_count / len(seq)) * 100

def get_tm(seq, na_conc=50, k_conc=0, oligo_conc=250):
    try:
        if not seq or len(seq) < 2:
            return 0.0

        total_salt = max(1, na_conc + k_conc)  # Prevent division by zero
        oligo_conc_m = max(1e-12, oligo_conc * 1e-9)  # Prevent log of zero

        seq = seq.upper()
        seq_l = len(seq)
        delta_h = 0
        delta_s = 0

        for i in range(seq_l - 1):
            dimer = seq[i:i+2]
            if all(c in 'ATCG' for c in dimer):  # Only process valid nucleotides
                delta_h += H_NN.get(dimer, 0)
                delta_s += S_NN.get(dimer, 0)

        if seq_l > 0:
            delta_h += H_INIT.get(seq[0], 0) + H_INIT.get(seq[-1], 0)
            delta_s += S_INIT.get(seq[0], 0) + S_INIT.get(seq[-1], 0)

        delta_h *= 1000

        if total_salt > 0:
            salt_correction = 0.368 * (seq_l - 1) * math.log(total_salt / 1000)
            delta_s += salt_correction

        denominator = delta_s + R * math.log(oligo_conc_m / 2)
        if abs(denominator) < 1e-10:  # Prevent division by zero
            return 0.0

        tm_kelvin = delta_h / denominator

        return max(0.0, tm_kelvin - 273.15)  # Ensure positive temperature
    except Exception as e:
        print(f"Error calculating Tm for sequence {seq}: {e}")
        return 0.0

def get_dg_intra_hairpin(seq):
    try:
        if not seq:
            return 0.0

        seq = seq.upper()
        seq_l = len(seq)
        min_dg = 0
        if seq_l < 8:
            return 0

        for i in range(seq_l - 4):
            for j in range(i + 4, seq_l):
                stem1 = seq[i:j]
                stem2 = get_reverse_complement(seq[j:])

                stem_len = min(len(stem1), len(stem2))
                if stem_len < 4:
                    continue

                delta_h = 0
                delta_s = 0

                for k in range(stem_len):
                    if k < len(stem1) and k < len(stem2):
                        dimer = stem1[k] + stem2[k]
                        if all(c in 'ATCG' for c in dimer):
                            delta_h += H_NN.get(dimer, 0)
                            delta_s += S_NN.get(dimer, 0)

                loop_length = len(seq[i + stem_len:j])

                if loop_length < 3:
                    continue

                dg = delta_h - ((delta_s * (273.15 + 37)) / 1000)

                if loop_length > 0:
                    dg += H_LOOP + R * (273.15 + 37) * math.log(max(1, loop_length)) / 1000

                if dg < min_dg:
                    min_dg = dg
        return min_dg
    except Exception as e:
        print(f"Error calculating dG intra hairpin for sequence {seq}: {e}")
        return 0.0

def get_dg_full_complementary(seq):
    try:
        if not seq:
            return 0.0

        seq = seq.upper()
        seq_l = len(seq)
        delta_h = 0
        delta_s = 0

        for i in range(seq_l - 1):
            dimer = seq[i:i+2]
            if all(c in 'ATCG' for c in dimer):
                delta_h += H_NN.get(dimer, 0)
                delta_s += S_NN.get(dimer, 0)

        if seq_l > 0:
            delta_h += H_INIT.get(seq[0], 0) + H_INIT.get(seq[-1], 0)
            delta_s += S_INIT.get(seq[0], 0) + S_INIT.get(seq[-1], 0)

        dg = delta_h - (delta_s * (273.15 + 37) / 1000)
        return dg
    except Exception as e:
        print(f"Error calculating dG full complementary for sequence {seq}: {e}")
        return 0.0

def get_dg_partial_complementary(oligos, target_oligo):
    try:
        if not oligos or not target_oligo or 'sequence' not in target_oligo:
            return 0.0

        target_seq = target_oligo['sequence'].upper()
        max_dg = 0

        for other_oligo in oligos:
            if not other_oligo or 'sequence' not in other_oligo:
                continue

            other_seq = other_oligo['sequence'].upper()
            if not other_seq:
                continue

            other_rev_comp = get_reverse_complement(other_seq)

            for i in range(len(target_seq) + len(other_seq) - 1):
                current_h = 0
                current_s = 0

                for j in range(len(target_seq) - 1):
                    if i - j < 0 or i - j >= len(other_rev_comp) - 1:
                        continue

                    if j + 1 < len(target_seq) and i - j + 1 < len(other_rev_comp):
                        dimer = target_seq[j:j+2] + other_rev_comp[i-j:i-j+2]
                        if len(dimer) == 4 and all(c in 'ATCG' for c in dimer):
                            if dimer in H_NN and dimer in S_NN:
                                current_h += H_NN[dimer]
                                current_s += S_NN[dimer]

                if current_h != 0:
                    dg = current_h - (current_s * (273.15 + 37) / 1000)
                    if dg < max_dg:
                        max_dg = dg
        return max_dg
    except Exception as e:
        print(f"Error calculating dG partial complementary: {e}")
        return 0.0

def parse_multi_fasta(text, sequence_name=''):
    text = text.strip()
    if not text:
        return []

    # If it doesn't start with '>', treat it as a raw sequence
    if not text.startswith('>'):
        # Clean the sequence (remove non-alphabetic characters)
        clean_seq = ''.join(filter(str.isalpha, text)).upper()
        if clean_seq:
            return [{
                'name': sequence_name or 'sequence1',
                'seq': clean_seq
            }]
        else:
            return []

    # Parse FASTA format
    fragments = []
    blocks = text.split('>')[1:]  # Remove empty first element

    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue

        header = lines[0].strip()
        seq = ''.join(filter(str.isalpha, ''.join(lines[1:]))).upper()

        if seq:
            fragments.append({
                'name': header or f'fragment{len(fragments) + 1}',
                'seq': seq
            })

    return fragments
