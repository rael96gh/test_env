from .sequence_utils import get_reverse_complement, get_gc_content

def calculate_primer_tm(sequence):
    gc_count = sequence.count('G') + sequence.count('C')
    at_count = sequence.count('A') + sequence.count('T')
    return (2 * at_count) + (4 * gc_count)

def generate_primers(sequence, options=None):
    if options is None:
        options = {}
    
    min_len = options.get('min_len', 20)
    max_len = options.get('max_len', 60)
    desired_gc_min = options.get('desired_gc_min', 40)
    desired_gc_max = options.get('desired_gc_max', 60)
    desired_tm_min = options.get('desired_tm_min', 55)
    desired_tm_max = options.get('desired_tm_max', 65)

    forward_primer = ''
    for i in range(min_len, max_len + 1):
        if i > len(sequence):
            break
        primer_candidate = sequence[0:i]
        tm = calculate_primer_tm(primer_candidate)
        gc_content = get_gc_content(primer_candidate)
        if desired_tm_min <= tm <= desired_tm_max and desired_gc_min <= gc_content <= desired_gc_max:
            forward_primer = primer_candidate
            break
    
    if not forward_primer:
        forward_primer = sequence[0:60]

    reverse_primer = ''
    reverse_complement_seq = get_reverse_complement(sequence)
    for i in range(min_len, max_len + 1):
        if i > len(reverse_complement_seq):
            break
        primer_candidate = reverse_complement_seq[0:i]
        tm = calculate_primer_tm(primer_candidate)
        gc_content = get_gc_content(primer_candidate)
        if desired_tm_min <= tm <= desired_tm_max and desired_gc_min <= gc_content <= desired_gc_max:
            reverse_primer = primer_candidate
            break

    if not reverse_primer:
        last_60 = sequence[len(sequence) - 60:]
        reverse_primer = get_reverse_complement(last_60)

    return {
        'forward_primer': forward_primer,
        'reverse_primer': reverse_primer
    }
