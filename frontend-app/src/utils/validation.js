/**
 * Form validation utilities
 */
import { VALIDATION_RULES } from './constants.js';

export const validateSequence = (sequence) => {
  const errors = [];

  if (!sequence || sequence.trim().length === 0) {
    errors.push('Sequence is required');
    return errors;
  }

  const cleanSeq = sequence.trim().toUpperCase();

  if (cleanSeq.length < VALIDATION_RULES.sequence.minLength) {
    errors.push(`Sequence must be at least ${VALIDATION_RULES.sequence.minLength} character(s)`);
  }

  if (cleanSeq.length > VALIDATION_RULES.sequence.maxLength) {
    errors.push(`Sequence must be less than ${VALIDATION_RULES.sequence.maxLength} characters`);
  }

  if (!VALIDATION_RULES.sequence.validChars.test(cleanSeq)) {
    const invalidChars = [...new Set(cleanSeq.match(/[^ATCGWSMKRYBDHVN]/gi) || [])];
    errors.push(`Invalid characters found: ${invalidChars.join(', ')}`);
  }

  return errors;
};

export const validateOligoParams = (params) => {
  const errors = {};

  // Validate oligo length
  if (params.oligo_length < VALIDATION_RULES.oligoLength.min ||
      params.oligo_length > VALIDATION_RULES.oligoLength.max) {
    errors.oligo_length = `Oligo length must be between ${VALIDATION_RULES.oligoLength.min}-${VALIDATION_RULES.oligoLength.max}`;
  }

  // Validate overlap length
  if (params.overlap_length < VALIDATION_RULES.overlapLength.min ||
      params.overlap_length > VALIDATION_RULES.overlapLength.max) {
    errors.overlap_length = `Overlap length must be between ${VALIDATION_RULES.overlapLength.min}-${VALIDATION_RULES.overlapLength.max}`;
  }

  // Validate concentrations
  ['na_conc', 'k_conc', 'oligo_conc'].forEach(field => {
    const value = params[field];
    if (value < VALIDATION_RULES.concentrations.min || value > VALIDATION_RULES.concentrations.max) {
      errors[field] = `${field} must be between ${VALIDATION_RULES.concentrations.min}-${VALIDATION_RULES.concentrations.max}`;
    }
  });

  // Validate at least one method is selected
  if (!params.simple_oligo_maker && !params.gapped_oligo_maker) {
    errors.method = 'Please select either Simple or Gapped oligo maker';
  }

  return errors;
};

export const validateMutations = (mutations) => {
  const errors = [];

  mutations.forEach((mutation, index) => {
    const mutationRegex = /^[A-Z]\d+[A-Z]$/;
    if (!mutationRegex.test(mutation.trim())) {
      errors.push(`Invalid mutation format at position ${index + 1}: ${mutation}. Use format like "A123C"`);
    }
  });

  return errors;
};