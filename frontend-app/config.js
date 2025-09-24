// API Configuration
const API_BASE_URL = window.location.protocol + '//' + window.location.hostname + ':5001';

// API endpoints
const API_ENDPOINTS = {
    generateOligos: `${API_BASE_URL}/api/generate_oligos`,
    generatePrimers: `${API_BASE_URL}/api/generate_primers`,
    downloadOligosCSV: `${API_BASE_URL}/api/download_oligos_csv`,
    downloadPrimersCSV: `${API_BASE_URL}/api/download_primers_csv`,
    downloadPoolingFiles: `${API_BASE_URL}/api/download_pooling_dilution_files`,
    customMutagenesis: `${API_BASE_URL}/api/custom_mutagenesis`,
    saturationMutagenesis: `${API_BASE_URL}/api/saturation_mutagenesis`,
    scanningLibrary: `${API_BASE_URL}/api/scanning_library`,
    recycle: `${API_BASE_URL}/api/recycle`
};