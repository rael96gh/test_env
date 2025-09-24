from app.config.constants import H_NN, S_NN, H_INIT, S_INIT, R, H_LOOP
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
    total_salt = na_conc + k_conc
    oligo_conc_m = oligo_conc * 1e-9
    
    seq_l = len(seq)
    delta_h = 0
    delta_s = 0

    for i in range(seq_l - 1):
        dimer = seq[i:i+2].upper()
        delta_h += H_NN.get(dimer, 0)
        delta_s += S_NN.get(dimer, 0)
        
    delta_h += H_INIT.get(seq[0].upper(), 0) + H_INIT.get(seq[-1].upper(), 0)
    delta_s += S_INIT.get(seq[0].upper(), 0) + S_INIT.get(seq[-1].upper(), 0)

    delta_h *= 1000
    
    salt_correction = 0.368 * (seq_l - 1) * math.log(total_salt / 1000)
    delta_s += salt_correction

    tm_kelvin = (delta_h) / (delta_s + R * math.log(oligo_conc_m / 2))
    
    return tm_kelvin - 273.15

def get_dg_intra_hairpin(seq):
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
                dimer = stem1[k] + stem2[k]
                delta_h += H_NN.get(dimer, 0)
                delta_s += S_NN.get(dimer, 0)
            
            loop_length = len(seq[i + stem_len:j])
            
            if loop_length < 3:
                continue

            dg = delta_h - ((delta_s * (273.15 + 37)) / 1000)
            
            dg += H_LOOP + R * (273.15 + 37) * math.log(loop_length) / 1000

            if dg < min_dg:
                min_dg = dg
    return min_dg

def get_dg_full_complementary(seq):
    seq_l = len(seq)
    delta_h = 0
    delta_s = 0

    for i in range(seq_l - 1):
        dimer = seq[i:i+2].upper()
        delta_h += H_NN.get(dimer, 0)
        delta_s += S_NN.get(dimer, 0)
    
    delta_h += H_INIT.get(seq[0].upper(), 0) + H_INIT.get(seq[-1].upper(), 0)
    delta_s += S_INIT.get(seq[0].upper(), 0) + S_INIT.get(seq[-1].upper(), 0)

    dg = delta_h - (delta_s * (273.15 + 37) / 1000)
    return dg

def get_dg_partial_complementary(oligos, target_oligo):
    target_seq = target_oligo['sequence']
    max_dg = 0

    for other_oligo in oligos:
        other_seq = other_oligo['sequence']
        other_rev_comp = get_reverse_complement(other_seq)

        for i in range(len(target_seq) + len(other_seq) -1):
            current_h = 0
            current_s = 0
            
            for j in range(len(target_seq)):
                if i-j < 0 or i-j >= len(other_rev_comp):
                    continue

                dimer = target_seq[j:j+2] + other_rev_comp[i-j:i-j+2]
                if dimer in H_NN and dimer in S_NN:
                    current_h += H_NN[dimer]
                    current_s += S_NN[dimer]
            
            if current_h != 0:
                dg = current_h - (current_s * (273.15 + 37) / 1000)
                if dg < max_dg:
                    max_dg = dg
    return max_dg

def parse_multi_fasta(text, sequence_name=''):
    text = text.strip()
    if not text:
        return []

    if not text.startswith('>'):
        return [{
            'name': sequence_name or 'fragment1',
            'seq': ''.join(filter(str.isalpha, text)).upper()
        }]

    fragments = []
    blocks = text.split('>')[1:]

    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue

        header = lines.pop(0).strip()
        seq = ''.join(filter(str.isalpha, ''.join(lines))).upper()

        if seq:
            fragments.append({
                'name': header or f'fragment{len(fragments) + 1}',
                'seq': seq
            })

    return fragments
