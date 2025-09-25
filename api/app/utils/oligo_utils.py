from .sequence_utils import get_reverse_complement, get_gc_content, get_tm, get_dg_intra_hairpin, get_dg_full_complementary, get_dg_partial_complementary

def simple_oligo_maker(sequence, oligo_length=60, overlap_length=30):
    forward = []
    reverse = []
    result = []

    for pos in range(0, len(sequence), oligo_length):
        forward.append(sequence[pos:pos + oligo_length])

    if forward and len(forward[-1]) < overlap_length:
        forward.pop()

    for i in range(len(forward) - 1):
        bridge_start = i * oligo_length + (oligo_length - overlap_length)
        region = sequence[bridge_start:bridge_start + oligo_length]
        reverse.append(get_reverse_complement(region))

    last_fwd_end = len(forward) * oligo_length
    term_start = max(0, last_fwd_end - overlap_length)
    if term_start < len(sequence):
        terminal_region = sequence[term_start:]
        reverse.append(get_reverse_complement(terminal_region))

    filtered_reverse = [seq for seq in reverse if len(seq) >= overlap_length]

    for i, seq in enumerate(forward):
        result.append({
            'label': f'FF_{i+1}',
            'sequence': seq,
            'length': len(seq)
        })
    for i, seq in enumerate(filtered_reverse):
        result.append({
            'label': f'RC_{i+1}',
            'sequence': seq,
            'length': len(seq)
        })

    return result

def generate_gapped_oligos(sequence, oligo_length, overlap_length, gap_length):
    min_length_to_keep = 20
    oligos = []

    # Generate Forward Oligos
    fwd_oligo_start = 0
    fwd_oligo_index = 1
    while fwd_oligo_start < len(sequence):
        oligo = sequence[fwd_oligo_start:fwd_oligo_start + oligo_length]
        if len(oligo) >= min_length_to_keep:
            oligos.append({
                'label': f'FF_{fwd_oligo_index}',
                'sequence': oligo,
                'length': len(oligo)
            })
        fwd_oligo_start += oligo_length + gap_length
        fwd_oligo_index += 1

    # Generate Reverse Complement Oligos
    rev_comp_start = oligo_length - overlap_length
    rev_comp_index = 1
    while rev_comp_start + oligo_length <= len(sequence):
        segment = sequence[rev_comp_start:rev_comp_start + oligo_length]
        rev_comp = get_reverse_complement(segment)
        oligos.append({
            'label': f'RC_{rev_comp_index}',
            'sequence': rev_comp,
            'length': len(rev_comp)
        })
        rev_comp_start += oligo_length + gap_length
        rev_comp_index += 1

    return [oligo for oligo in oligos if len(oligo['sequence']) >= min_length_to_keep]

def clean_oligos(oligos, end_len=8, score_threshold=0.75, trim_limit=8):
    cleaned = []
    for obj in oligos:
        seq = obj['sequence']
        trimmed5 = 0
        trimmed3 = 0
        is_valid = False

        while len(seq) >= end_len * 2 and (trimmed5 < trim_limit or trimmed3 < trim_limit):
            start_seq = seq[:end_len]
            end_seq = seq[-end_len:]

            worst5 = score_end_match(start_seq, seq[end_len:])
            worst3 = score_end_match(end_seq, seq[:-end_len])

            for other in oligos:
                if other == obj or is_intended_partner(obj, other):
                    continue
                worst5 = max(worst5, score_end_match(start_seq, other['sequence']))
                worst3 = max(worst3, score_end_match(end_seq, other['sequence']))
                if worst5 == 1 or worst3 == 1:
                    break

            conflict5 = worst5 >= score_threshold
            conflict3 = worst3 >= score_threshold

            if not conflict5 and not conflict3:
                is_valid = True
                break
            
            if conflict3 and trimmed3 < trim_limit:
                seq = seq[:-1]
                trimmed3 += 1
            elif conflict5 and trimmed5 < trim_limit:
                seq = seq[1:]
                trimmed5 += 1
            else:
                break
        
        if is_valid:
            trimmed_homo = trim_terminal_homopolymers(seq, 5)
            cleaned.append({
                **obj,
                'sequence': trimmed_homo,
                'length': len(trimmed_homo),
                'invalid': False 
            })
        else:
            cleaned.append({
                **obj,
                'invalid': True,
                'sequence': obj['sequence'],
                'length': obj['length']
            })
    return cleaned

def score_end_match(end_seq, target_seq):
    end_len = len(end_seq)
    end_rc = get_reverse_complement(end_seq)
    worst_score = 0

    for i in range(len(target_seq) - end_len + 1):
        window = target_seq[i:i + end_len]
        mismatches = 0
        mismatch_pos = -1

        for p in range(end_len):
            if end_rc[p] != window[p]:
                mismatches += 1
                mismatch_pos = p + 1
                if mismatches > 1:
                    break
        
        if mismatches == 0:
            return 1
        if mismatches == 1:
            base = end_rc[mismatch_pos - 1]
            base_penalty = 1.0 if base in ['G', 'C'] else 0.5
            pos_weight = mismatch_pos / end_len
            score = (7 / 8) - pos_weight * base_penalty
            worst_score = max(worst_score, score)
    return worst_score

def is_intended_partner(a, b):
    orientation = lambda label: "FF" if label.startswith("FF") else "RC"
    index_num = lambda label: int(label.split('_')[1])
    if orientation(a['label']) == orientation(b['label']):
        return False
    i = index_num(a['label'])
    j = index_num(b['label'])
    if orientation(a['label']) == "FF":
        return j == i or j == i - 1
    else:
        return j == i or j == i + 1

def trim_terminal_homopolymers(seq, window=5):
    import re
    homo_regex = re.compile(r'(A{4,}|T{4,}|C{4,}|G{4,})')
    trimmed_seq = seq
    start_match = homo_regex.search(trimmed_seq[:window])
    if start_match and trimmed_seq.startswith(start_match.group(0)):
        trimmed_seq = trimmed_seq[len(start_match.group(0)) - 1:]
    end_match = homo_regex.search(trimmed_seq[-window:])
    if end_match and trimmed_seq.endswith(end_match.group(0)):
        trimmed_seq = trimmed_seq[:len(trimmed_seq) - len(end_match.group(0)) + 1]
    return trimmed_seq

def optimize_oligos(oligos, na_conc, k_conc, oligo_conc):
    optimized = []
    MIN_LENGTH = 20
    MAX_TRIM = 10

    for oligo in oligos:
        is_optimized = False
        
        for left_trim in range(MAX_TRIM + 1):
            for right_trim in range(MAX_TRIM + 1):
                new_length = len(oligo['sequence']) - left_trim - right_trim
                if new_length < MIN_LENGTH:
                    continue

                trimmed_seq = oligo['sequence'][left_trim:len(oligo['sequence']) - right_trim]
                temp_oligo = {**oligo, 'sequence': trimmed_seq}

                if is_oligo_acceptable(oligos, temp_oligo, na_conc, k_conc, oligo_conc):
                    optimized.append({
                        **oligo,
                        'sequence': trimmed_seq,
                        'length': new_length,
                        'invalid': False
                    })
                    is_optimized = True
                    break
            if is_optimized:
                break
        
        if not is_optimized:
            optimized.append({
                **oligo,
                'invalid': True
            })
    return optimized

def is_oligo_acceptable(oligos, target_oligo, na_conc, k_conc, oligo_conc):
    seq = target_oligo['sequence']
    gc = get_gc_content(seq)
    tm = get_tm(seq, na_conc, k_conc, oligo_conc)
    dg_intra = get_dg_intra_hairpin(seq)
    dg_full = get_dg_full_complementary(seq)
    dg_partial = get_dg_partial_complementary(oligos, target_oligo)
    
    gc_valid = 25 <= gc <= 75
    tm_valid = 50 <= tm <= 75
    dg_intra_valid = dg_intra >= -3
    dg_full_valid = dg_full <= -20
    dg_partial_valid = dg_partial >= -5

    return gc_valid and tm_valid and dg_intra_valid and dg_full_valid and dg_partial_valid
