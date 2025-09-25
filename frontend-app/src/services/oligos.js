/**
 * Oligo generation services
 */
import apiService from './api.js';

export const oligoService = {
  async generateOligos(params) {
    return apiService.post('/oligos/generate', params);
  },

  async analyzeSequence(sequence) {
    return apiService.post('/sequences/analyze', { sequence });
  },

  async downloadOligosCSV(data) {
    return apiService.post('/downloads/oligos-csv', data);
  }
};

export default oligoService;