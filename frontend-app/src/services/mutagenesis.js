/**
 * Mutagenesis services
 */
import apiService from './api.js';

export const mutagenesisService = {
  async generateCustomMutagenesis(params) {
    return apiService.post('/mutagenesis/custom', params);
  },

  async generateSaturationMutagenesis(params) {
    return apiService.post('/mutagenesis/saturation', params);
  },

  async generateScanningLibrary(params) {
    return apiService.post('/mutagenesis/scanning', params);
  },

  async generatePrimers(params) {
    return apiService.post('/primers/generate', params);
  }
};

export default mutagenesisService;