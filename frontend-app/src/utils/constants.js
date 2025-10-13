/**
 * Application constants
 */

export const DEFAULT_OLIGO_PARAMS = {
  oligo_length: 60,
  overlap_length: 30,
  gap_length: 20,
  na_conc: 50,
  k_conc: 0,
  oligo_conc: 250,
  simple_oligo_maker: false,
  gapped_oligo_maker: false,
  clean_oligos: false,
  optimized_oligos: false,
};

export const WELL_FORMATS = [
  { value: '96-column', label: '96-well (Column)' },
  { value: '96-row', label: '96-well (Row)' },
  { value: '384-column', label: '384-well (Column)' },
  { value: '384-row', label: '384-well (Row)' },
];

export const CODON_LIBRARIES = [
  { value: 'NNN', label: 'NNN (All 64 codons)' },
  { value: 'NNK', label: 'NNK (32 codons)' },
  { value: 'NNS', label: 'NNS (32 codons)' },
  { value: 'NDT', label: 'NDT (12 codons)' },
];

export const GENERATION_MODES = [
  { value: 'group', label: 'Group mutations' },
  { value: 'individual', label: 'Individual mutations' },
];

export const VALIDATION_RULES = {
  sequence: {
    minLength: 1,
    maxLength: 50000,
    validChars: /^[ATCGWSMKRYBDHVN]+$/i,
  },
  oligoLength: {
    min: 20,
    max: 200,
  },
  overlapLength: {
    min: 15,
    max: 80,
  },
  concentrations: {
    min: 0,
    max: 10000,
  },
};