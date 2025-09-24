let generatedOligos = [];
let generatedPrimers = {};

// --- Utility Functions (adapted for backend interaction) ---

function showMessage(text, type) {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = text;
    messageBox.classList.remove('hidden', 'message-success', 'message-error');
    if (type === 'success') {
        messageBox.classList.add('message-success');
    } else if (type === 'error') {
        messageBox.classList.add('message-error');
    }
    setTimeout(() => {
        messageBox.classList.add('hidden');
    }, 5000);
}

async function parseFastaFrontend(text) {
    // This function will now primarily be used for initial parsing on the frontend
    // before sending to backend, or for displaying raw FASTA.
    text = text.trim();
    if (!text) return [];

    if (!text.startsWith('>')) {
        return [{
            name: document.getElementById('sequenceName').value.trim() || 'fragment1',
            sequence: text.replace(/[^A-Za-z]/g, '').toUpperCase()
        }];
    }

    const sequences = [];
    const blocks = text.split('>');
    
    blocks.forEach(block => {
        if (block.trim() === '') return;

        const lines = block.split(/\r?\n/);
        const header = lines.shift().trim();
        const seq = lines.join('').replace(/[^A-Za-z]/g, '').toUpperCase();

        if (seq) {
            sequences.push({
                name: header || `fragment${sequences.length + 1}`,
                sequence: seq
            });
        }
    });

    return sequences;
}

function downloadFile(content, filename, type) {
    const blob = new Blob([content], { type: type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    showMessage('Download successful!', 'success');
}

// --- Oligo Generation ---

async function generateOligos() {
    const oligoLength = +document.getElementById('oligoLength').value;
    const overlapLength = +document.getElementById('overlapLength').value;
    const gapLength = +document.getElementById('gapLength').value;
    const naConc = +document.getElementById('naConc').value;
    const kConc = +document.getElementById('kConc').value;
    const oligoConc = +document.getElementById('oligoConc').value;
                
    const simpleOligoMakerChecked = document.getElementById('simpleOligoMaker').checked;
    const gappedOligoMakerChecked = document.getElementById('gappedOligoMaker').checked;
    const cleanOligosChecked = document.getElementById('cleanOligos').checked;
    const optimizedOligosChecked = document.getElementById('optimizedOligos').checked;

    const sequenceInput = document.getElementById('sequence').value;
    if (!sequenceInput) {
        showMessage('Please paste or upload at least one sequence.', 'error');
        return;
    }

    if (gappedOligoMakerChecked && oligoLength <= gapLength) {
        showMessage('Oligo length must be greater than gap length.', 'error');
        return;
    }

    if (simpleOligoMakerChecked && overlapLength >= oligoLength) {
        showMessage('Overlap length must be less than oligo length for Simple Oligos.', 'error');
        return;
    }

    if (oligoLength <= 0) {
        showMessage("Oligo length must be a positive number.", 'error');
        return;
    }
    
    if (!simpleOligoMakerChecked && !gappedOligoMakerChecked) {
        showMessage("Please select either Simple Oligos or Gapped Oligos.", 'error');
        return;
    }

    try {
        const response = await fetch(API_ENDPOINTS.generateOligos, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sequence: sequenceInput,
                oligo_length: oligoLength,
                overlap_length: overlapLength,
                gap_length: gapLength,
                na_conc: naConc,
                k_conc: kConc,
                oligo_conc: oligoConc,
                simple_oligo_maker: simpleOligoMakerChecked,
                gapped_oligo_maker: gappedOligoMakerChecked,
                clean_oligos: cleanOligosChecked,
                optimized_oligos: optimizedOligosChecked,
            }),
        });

        const result = await response.json();

        if (response.ok) {
            generatedOligos = result;
            // Render oligos to results textarea
            const lines = [];
            const groups = {};
            generatedOligos.forEach(o => {
                if (!groups[o.fragment]) groups[o.fragment] = [];
                groups[o.fragment].push(o);
            });

            const indexNum = label => parseInt(label.split('_')[1], 10);
            const orientation = label => label.startsWith("FF") ? "FF" : "RC";

            for (const fragment in groups) {
                lines.push(`> ${fragment}`);
                const ff = groups[fragment]
                    .filter(o => orientation(o.label) === "FF")
                    .sort((a, b) => indexNum(a.label) - indexNum(b.label));
                const rc = groups[fragment]
                    .filter(o => orientation(o.label) === "RC")
                    .sort((a, b) => indexNum(a.label) - indexNum(b.label));

                const maxLen = Math.max(ff.length, rc.length);
                for (let i = 0; i < maxLen; i++) {
                    if (ff[i]) {
                        // Fetch GC, Tm, Dg values from backend if needed, or calculate on frontend if simple
                        // For now, just display sequence and length
                        lines.push(`${ff[i].invalid ? "INVALID_" : ""}${ff[i].label}\t${ff[i].sequence}\t${ff[i].length}`);
                    }
                    if (rc[i]) {
                        lines.push(`${rc[i].invalid ? "INVALID_" : ""}${rc[i].label}\t${rc[i].sequence}\t${rc[i].length}`);
                    }
                }
                lines.push("");
            }
            document.getElementById('results').textContent = lines.join('\n');
            document.getElementById('downloadButton').style.display = 'inline';
            document.getElementById('downloadPrimersButton').style.display = 'inline'; 
            document.getElementById('downloadPoolingButton').style.display = 'inline';

            // Generate primers as well
            const fragments = await parseFastaFrontend(sequenceInput);
            if (fragments.length > 0) {
                generatedPrimers = {};
                for (const fr of fragments) {
                    const primerResponse = await fetch(API_ENDPOINTS.generatePrimers, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ sequence: fr.sequence }),
                    });
                    if (primerResponse.ok) {
                        generatedPrimers[fr.name] = await primerResponse.json();
                    }
                }
            }

            showMessage('Oligos generated successfully!', 'success');
        } else {
            showMessage(`Error generating oligos: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An unexpected error occurred.', 'error');
    }
}

// --- Download Functions ---

async function downloadOligoList() {
    if (generatedOligos.length === 0) {
        showMessage("No oligos to download.", 'error');
        return;
    }
    const wellFormat = document.getElementById('wellFormat').value;
    const sequenceName = document.getElementById('sequenceName').value.trim() || 'sequence';

    try {
        const response = await fetch(API_ENDPOINTS.downloadOligosCSV, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                generated_oligos: generatedOligos,
                well_format: wellFormat,
                sequence_name: sequenceName
            }),
        });

        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, `${sequenceName}_oligos.csv`, 'text/csv');
        } else {
            const error = await response.json();
            showMessage(`Error downloading oligos: ${error.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An unexpected error occurred during download.', 'error');
    }
}

async function downloadPrimers() {
    if (Object.keys(generatedPrimers).length === 0) {
        showMessage("No primers to download.", 'error');
        return;
    }
    const wellFormat = document.getElementById('wellFormat').value;
    const destWellFormat = document.getElementById('destinationFormat').value;
    const sequenceName = document.getElementById('sequenceName').value.trim() || 'sequence';

    try {
        const response = await fetch(API_ENDPOINTS.downloadPrimersCSV, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                generated_primers: generatedPrimers,
                generated_oligos: generatedOligos, // Needed for destination map
                well_format: wellFormat,
                dest_well_format: destWellFormat,
                sequence_name: sequenceName
            }),
        });

        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, `${sequenceName}_primers.csv`, 'text/csv');
        } else {
            const error = await response.json();
            showMessage(`Error downloading primers: ${error.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An unexpected error occurred during download.', 'error');
    }
}

async function downloadPoolingAndDilutionFiles() {
    if (generatedOligos.length === 0) {
        showMessage('Please generate oligos first.', 'error');
        return;
    }
    const wellFormat = document.getElementById('wellFormat').value;
    const destWellFormat = document.getElementById('destinationFormat').value;

    try {
        const response = await fetch(API_ENDPOINTS.downloadPoolingFiles, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                generated_oligos: generatedOligos,
                well_format: wellFormat,
                dest_well_format: destWellFormat
            }),
        });

        if (response.ok) {
            const blob = await response.blob();
            downloadFile(blob, 'oligo_files.zip', 'application/zip');
        } else {
            const error = await response.json();
            showMessage(`Error downloading pooling/dilution files: ${error.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An unexpected error occurred during download.', 'error');
    }
}

// --- Mutagenesis Functions (adapted for backend interaction) ---

// Genetic Code Definitions (can be fetched from backend or kept here if static)
const geneticCode = {
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A', 'AGA': 'R', 'AGG': 'R', 'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
    'AAC': 'N', 'AAT': 'N', 'GAC': 'D', 'GAT': 'D', 'TGC': 'C', 'TGT': 'C', 'GAA': 'E', 'GAG': 'E', 'CAA': 'Q', 'CAG': 'Q',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G', 'CAC': 'H', 'CAT': 'H', 'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'TTA': 'L',
    'TTG': 'L', 'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L', 'AAA': 'K', 'AAG': 'K', 'ATG': 'M', 'TTC': 'F', 'TTT': 'F',
    'CCC': 'P', 'CCT': 'P', 'CCA': 'P', 'CCG': 'P', 'AGC': 'S', 'AGT': 'S', 'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
    'ACC': 'T', 'ACG': 'T', 'ACT': 'T', 'ACA': 'T', 'TGG': 'W', 'TAC': 'Y', 'TAT': 'Y', 'GTA': 'V', 'GTC': 'V', 'GTG': 'V',
    'GTT': 'V', 'TAA': '*', 'TAG': '*', 'TGA': '*'
};

const reverseGeneticCode = {};
for (const codon in geneticCode) {
    const aa = geneticCode[codon];
    if (!reverseGeneticCode[aa]) {
        reverseGeneticCode[aa] = [];
    }
    reverseGeneticCode[aa].push(codon);
}

// Custom Mutagenesis

let customMutations = [];

async function updateCustomCurrentValue() {
    const sequence = document.getElementById('fastaInputCustom').value.trim().toUpperCase();
    const position = parseInt(document.getElementById('customPositionInput').value, 10);
    const type = document.getElementById('customVariantType').value;

    const customCurrentValueDisplay = document.getElementById('customCurrentValueDisplay');
    const mutationRecap = document.getElementById('mutationRecap');

    if (!sequence || !position || position <= 0) {
        customCurrentValueDisplay.textContent = '-';
        customCurrentValueDisplay.dataset.value = '';
        mutationRecap.textContent = '';
        return;
    }

    let displayValue = '-';
    let dataValue = '';

    if (type === 'N') {
        if (position <= sequence.length) {
            displayValue = sequence[position - 1];
            dataValue = displayValue;
        }
    } else if (type === 'AA') {
        const codonStart = (position - 1) * 3;
        if (codonStart + 3 <= sequence.length) {
            const codon = sequence.substring(codonStart, codonStart + 3);
            const aa = geneticCode[codon] || '?';
            displayValue = `${codon} (${aa})`;
            dataValue = aa;
        }
    }
    customCurrentValueDisplay.textContent = displayValue;
    customCurrentValueDisplay.dataset.value = dataValue;
    updateCustomRecap();
}

function updateCustomRecap() {
    const type = document.getElementById('customVariantType').value;
    const position = document.getElementById('customPositionInput').value;
    const currentValue = document.getElementById('customCurrentValueDisplay').dataset.value || (document.getElementById('customCurrentValueDisplay').textContent !== '-' ? document.getElementById('customCurrentValueDisplay').textContent : '');
    const newValue = document.getElementById('customNewValueInput').value.toUpperCase();
    const mutationRecap = document.getElementById('mutationRecap');

    if (!position || !newValue || !currentValue) {
        mutationRecap.textContent = '';
        return;
    }

    mutationRecap.textContent = `Recapitulation: Change ${type === 'AA' ? 'amino acid' : 'nucleotide'} at position ${position} from ${currentValue} to ${newValue}.`;
}

function addCustomMutation() {
    const sequence = document.getElementById('fastaInputCustom').value.trim().toUpperCase();
    if (!sequence) {
        showMessage('Please provide a FASTA sequence first.', 'error');
        return;
    }

    const type = document.getElementById('customVariantType').value;
    const pos = parseInt(document.getElementById('customPositionInput').value, 10);
    const newValues = document.getElementById('customNewValueInput').value.trim().toUpperCase().split(',').filter(v => v);

    if (!pos || pos <= 0) {
        showMessage('Please enter a valid position.', 'error');
        return;
    }
    if (newValues.length === 0) {
        showMessage('Please enter the new Amino Acid(s) or Nucleotide(s).', 'error');
        return;
    }

    let validationPassed = false;
    if (type === 'AA') {
        const codonStart = (pos - 1) * 3;
        if (codonStart + 3 > sequence.length) {
            showMessage(`Position ${pos} is out of bounds for an amino acid mutation.`, 'error');
            return;
        }
        if (newValues.every(aa => aa.length === 1 && 'ACDEFGHIKLMNPQRSTVWY*'.includes(aa))) {
            validationPassed = true;
        } else {
            showMessage('Invalid amino acid character. Use single-letter codes.', 'error');
            return;
        }
    } else if (type === 'N') {
        if (pos > sequence.length) {
            showMessage(`Position ${pos} is out of bounds for a nucleotide mutation.`, 'error');
            return;
        }
        if (newValues.every(nuc => nuc.length === 1 && 'ATGC'.includes(nuc))) {
            validationPassed = true;
        }
    } else {
        showMessage('Invalid nucleotide character. Use A, T, G, or C.', 'error');
        return;
    }

    if (validationPassed) {
        customMutations.push({ type, pos, new: newValues });
        renderCustomMutationChips();
        document.getElementById('customPositionInput').value = '';
        document.getElementById('customCurrentValueDisplay').textContent = '-';
        document.getElementById('customCurrentValueDisplay').dataset.value = '';
        document.getElementById('customNewValueInput').value = '';
        document.getElementById('mutationRecap').textContent = '';
        showMessage('Mutation added successfully.', 'success');
    }
}

function renderCustomMutationChips() {
    const mutationChipsContainer = document.getElementById('mutationChips');
    const customMutationListContainer = document.getElementById('customMutationList');
    mutationChipsContainer.innerHTML = '';
    if (customMutations.length > 0) {
        customMutationListContainer.classList.remove('hidden');
        customMutations.forEach((mut, index) => {
            const chip = document.createElement('span');
            chip.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800';
            chip.innerHTML = `
                ${mut.type}:${mut.pos}:${mut.new.join(',')}
                <button type="button" data-index="${index}" class="remove-btn">
                    <svg stroke="currentColor" fill="none" viewBox="1 1 7 7" width="100" height="100">
                        <path stroke-linecap="round" stroke-width="2" d="M1 1 L8 8 M8 1 L1 8" />
                    </svg>
                </button>
            `;
            mutationChipsContainer.appendChild(chip);
        });
    } else {
        customMutationListContainer.classList.add('hidden');
    }
}

async function generateCustomSequences() {
    const originalSequence = document.getElementById('fastaInputCustom').value.trim().toUpperCase();
    if (!originalSequence) {
        showMessage('Please provide a FASTA sequence first.', 'error');
        return;
    }
    if (customMutations.length === 0) {
        showMessage('Please add at least one mutation.', 'error');
        return;
    }

    const originalName = (await parseFastaFrontend(document.getElementById('fastaInputCustom').value.trim()))[0].name;
    const generationMode = document.getElementById('generationMode').value;

    try {
        const response = await fetch(API_ENDPOINTS.customMutagenesis, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_sequence: originalSequence,
                original_name: originalName,
                mutations: customMutations,
                generation_mode: generationMode
            }),
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('resultsOutputCustom').value = result.join('\n');
            showMessage(`Successfully generated ${result.length} sequences.`, 'success');
        } else {
            showMessage(`Error generating custom sequences: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An unexpected error occurred.', 'error');
    }
}

// Saturation Mutagenesis

let saturationMutations = [];

async function updateSatCurrentValueDisplay() {
    const sequence = document.getElementById('fastaInputSat').value.trim().toUpperCase();
    const position = parseInt(document.getElementById('satPositionInput').value);
    const variantType = document.getElementById('satVariantType').value;

    const satCurrentValueDisplay = document.getElementById('satCurrentValueDisplay');

    if (!sequence || isNaN(position) || position <= 0) {
        satCurrentValueDisplay.textContent = '-';
        return;
    }

    if (variantType === 'N') {
        const index = position - 1;
        if (index >= 0 && index < sequence.length) {
            satCurrentValueDisplay.textContent = sequence[index];
        } else {
            satCurrentValueDisplay.textContent = '-';
        }
    } else { // AA mode
        if (sequence.length % 3 !== 0) {
            satCurrentValueDisplay.textContent = 'Error: DNA length must be a multiple of 3 for Amino Acid variants.';
            return;
        }
        const startIndex = (position - 1) * 3;
        if (startIndex >= 0 && startIndex + 3 <= sequence.length) {
            const codon = sequence.substring(startIndex, startIndex + 3);
            const aminoAcid = geneticCode[codon] || '?';
            satCurrentValueDisplay.textContent = `${codon} (${aminoAcid})`;
        }
    }
}

function renderSaturationMutationChips() {
    const saturationMutationChipsContainer = document.getElementById('saturationMutationChips');
    const saturationMutationListContainer = document.getElementById('saturationMutationList');
    saturationMutationChipsContainer.innerHTML = '';
    if (saturationMutations.length > 0) {
        saturationMutationListContainer.classList.remove('hidden');
        saturationMutations.forEach((mut, index) => {
            const chip = document.createElement('span');
            chip.className = 'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800';
            chip.innerHTML = `
                ${mut.type}:${mut.pos}
                <button type="button" class="remove-btn" data-index="${index}">
                    <svg stroke="currentColor" fill="none" viewBox="1 1 7 7" width="100" height="100">
                        <path stroke-linecap="round" stroke-width="2" d="M1 1 L8 8 M8 1 L1 8" />
                    </svg>
                </button>
            `;
            saturationMutationChipsContainer.appendChild(chip);
        });
    } else {
        saturationMutationListContainer.classList.add('hidden');
    }
}

function addSaturationMutation() {
    if (!document.getElementById('fastaInputSat').value.trim()) {
        showMessage('No sequence uploaded. Please provide a FASTA sequence first.', 'error');
        return;
    }

    const variantType = document.getElementById('satVariantType').value;
    const position = parseInt(document.getElementById('satPositionInput').value);

    if (isNaN(position) || position <= 0) {
        showMessage('Please enter a valid position.', 'error');
        return;
    }

    let parsedMutation = { type: variantType, pos: position };

    const isDuplicate = saturationMutations.some(mut => mut.type === parsedMutation.type && mut.pos === parsedMutation.pos);
    if (isDuplicate) {
        showMessage('This variant position has already been added.', 'error');
        return;
    }

    saturationMutations.push(parsedMutation);
    renderSaturationMutationChips();
    document.getElementById('satPositionInput').value = '';
    document.getElementById('satCurrentValueDisplay').textContent = '-';
    showMessage('Variant position added.', 'success');
}

async function generateSaturationLibrary() {
    const fastaContent = document.getElementById('fastaInputSat').value;
    const excludeStops = document.getElementById('excludeStopCodonsSat').checked;

    if (!fastaContent || saturationMutations.length === 0) {
        showMessage('Please provide FASTA sequences and add at least one variant position.', 'error');
        return;
    }

    try {
        const response = await fetch(API_ENDPOINTS.saturationMutagenesis, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fasta_content: fastaContent,
                saturation_mutations: saturationMutations,
                exclude_stops: excludeStops
            }),
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById('resultsOutputSat').value = result.join('\n');
            showMessage(`Successfully generated ${result.length} unique mutant sequences.`, 'success');
        } else {
            showMessage(`Error generating saturation library: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An unexpected error occurred.', 'error');
    }
}

// Scanning Library

async function processScanningSequence() {
    const sequenceScanningInput = document.getElementById('sequenceScanning');
    const outputScanningTextarea = document.getElementById('outputScanning');
    const errorMessageScanningDiv = document.getElementById('errorMessageScanning');
    const sequenceLengthScanningDiv = document.getElementById('sequenceLengthScanning');

    outputScanningTextarea.innerHTML = '';
    errorMessageScanningDiv.innerHTML = '';
    sequenceLengthScanningDiv.innerHTML = '';

    let sequenceInput = sequenceScanningInput.value.trim();
    
    if (!sequenceInput) {
        errorMessageScanningDiv.innerText = 'Please enter a sequence.';
        return;
    }
    
    try {
        let nucleotideSequence = sequenceInput.replace(/[^ATGC]/gi, '');
        let sequenceLength = nucleotideSequence.length;

        outputScanningTextarea.innerHTML = 'You entered: ' + nucleotideSequence;
        sequenceLengthScanningDiv.innerHTML = 'Sequence Length: ' + sequenceLength + ' nucleotides';
    } catch (error) {
        errorMessageScanningDiv.innerText = 'Invalid input. Please enter a valid nucleotide sequence.';
    }
}

async function transformToScanningLibrary() {
    const sequenceScanningInput = document.getElementById('sequenceScanning');
    const sequenceNameScanningInput = document.getElementById('sequenceNameScanning');
    const startPositionScanningInput = document.getElementById('startPositionScanning');
    const endPositionScanningInput = document.getElementById('endPositionScanning');
    const fullSequenceScanningCheckbox = document.getElementById('fullSequenceScanning');
    const outputScanningTextarea = document.getElementById('outputScanning');
    const errorMessageScanningDiv = document.getElementById('errorMessageScanning');

    outputScanningTextarea.innerHTML = '';
    errorMessageScanningDiv.innerHTML = '';

    let sequenceInput = sequenceScanningInput.value.trim();
    let sequenceName = sequenceNameScanningInput.value.trim();
    let startPosition = parseInt(startPositionScanningInput.value);
    let endPosition = parseInt(endPositionScanningInput.value);
    let fullSequenceChecked = fullSequenceScanningCheckbox.checked;

    let libraryType = document.querySelector('input[name="libraryTypeScanning"]:checked').value;
    
    if (!sequenceInput) {
        errorMessageScanningDiv.innerText = 'Please enter a sequence.';
        return;
    }
    
    if (!sequenceName) {
        errorMessageScanningDiv.innerText = 'Please enter a sequence name.';
        return;
    }

    if (!fullSequenceChecked && (isNaN(startPosition) || isNaN(endPosition))) {
        errorMessageScanningDiv.innerText = 'Please enter valid start and end positions, or select full sequence.';
        return;
    }

    try {
        const response = await fetch(API_ENDPOINTS.scanningLibrary, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sequence: sequenceInput,
                sequence_name: sequenceName,
                start_position: fullSequenceChecked ? null : startPosition,
                end_position: fullSequenceChecked ? null : endPosition,
                full_sequence: fullSequenceChecked,
                library_type: libraryType
            }),
        });

        const result = await response.json();

        if (response.ok) {
            outputScanningTextarea.value = result.join('\n');
            showMessage(`Successfully generated ${result.length} scanning library variants.`, 'success');
        } else {
            showMessage(`Error generating scanning library: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('An unexpected error occurred.', 'error');
    }
}

function downloadScanningResults() {
    const fastaContent = document.getElementById('outputScanning').value;
    if (!fastaContent) {
        showMessage('No sequences to download.', 'error');
        return;
    }
    downloadFile(fastaContent, 'scanning_library_variants.fasta', 'text/fasta');
}

// --- General UI Logic ---

document.addEventListener('DOMContentLoaded', function() {
    // DOM element references
    const dashboardView = document.getElementById('dashboardView');
    const satCard = document.getElementById('satCard');
    const customCard = document.getElementById('customCard');
    const scanningCard = document.getElementById('scanningCard');
    const saturationMutagenesisSection = document.getElementById('saturationMutagenesisSection');
    const customMutagenesisSection = document.getElementById('customMutagenesisSection');
    const scanningLibrarySection = document.getElementById('scanningLibrarySection');
    const oligoMakerSection = document.getElementById('oligoMakerSection');
    
    const backToDashboardSat = document.getElementById('backToDashboardSat');
    const backToDashboardCustom = document.getElementById('backToDashboardCustom');
    const backToDashboardScanning = document.getElementById('backToDashboardScanning');
    const backToDashboardOligo = document.getElementById('backToDashboardOligo');
    
    const feedSatToOligoMakerBtn = document.getElementById('feedSatToOligoMakerBtn');
    const feedCustomToOligoMakerBtn = document.getElementById('feedCustomToOligoMakerBtn');
    const feedScanningToOligoMakerBtn = document.getElementById('feedScanningToOligoMakerBtn');

    function showView(viewId) {
        dashboardView.classList.add('hidden');
        saturationMutagenesisSection.classList.add('hidden');
        customMutagenesisSection.classList.add('hidden');
        scanningLibrarySection.classList.add('hidden');
        oligoMakerSection.classList.add('hidden');
        
        const viewToShow = document.getElementById(viewId);
        if (viewToShow) {
            viewToShow.classList.remove('hidden');
        }
    }

    function feedToOligoMaker(sourceTextareaId) {
        const sourceTextarea = document.getElementById(sourceTextareaId);
        if (!sourceTextarea || !sourceTextarea.value) {
            showMessage('No data to feed. Please generate a sequence first.', 'error');
            return;
        }
        
        document.getElementById('sequence').value = sourceTextarea.value;
        showView('oligoMakerSection');
        showMessage('Library loaded into Oligo Designer. Configure and generate your oligos.', 'success');
    }

    function setupFastaUploadAndPaste(fileInputId, nameAreaId, seqAreaId) {
        const fileInput = document.getElementById(fileInputId);
        if (fileInput) {
            fileInput.addEventListener('change', (event) => {
                const file = event.target.files[0];
                if (!file) return;

                const reader = new FileReader();
                reader.onload = async (e) => {
                    const content = e.target.result;
                    const sequences = await parseFastaFrontend(content);
                    if (sequences.length > 0) {
                        const firstSeq = sequences[0];
                        document.getElementById(nameAreaId).value = firstSeq.name;
                        document.getElementById(seqAreaId).value = sequences.map(
                            s => `>${s.name}\n${s.sequence}`
                        ).join('\n');
                        showMessage(`${sequences.length} sequence(s) loaded from file.`, 'success');
                    } else {
                        document.getElementById(seqAreaId).value = content;
                        showMessage('Could not parse FASTA file, content loaded as plain text.', 'error');
                    }
                };
                reader.readAsText(file);
            });
        }
    }

    // Event Listeners
    satCard.addEventListener('click', () => showView('saturationMutagenesisSection'));
    customCard.addEventListener('click', () => showView('customMutagenesisSection'));
    scanningCard.addEventListener('click', () => showView('scanningLibrarySection'));
    
    backToDashboardSat.addEventListener('click', () => showView('dashboardView'));
    backToDashboardCustom.addEventListener('click', () => showView('dashboardView'));
    backToDashboardScanning.addEventListener('click', () => showView('dashboardView'));
    backToDashboardOligo.addEventListener('click', () => showView('dashboardView'));

    feedSatToOligoMakerBtn.addEventListener('click', () => feedToOligoMaker('resultsOutputSat'));
    feedCustomToOligoMakerBtn.addEventListener('click', () => feedToOligoMaker('resultsOutputCustom'));
    feedScanningToOligoMakerBtn.addEventListener('click', () => feedToOligoMaker('outputScanning'));

    // Oligo Maker Event Listeners
    document.getElementById('generateOligosBtn').addEventListener('click', generateOligos);
    document.getElementById('downloadButton').addEventListener('click', downloadOligoList);
    document.getElementById('downloadPrimersButton').addEventListener('click', downloadPrimers);
    document.getElementById('downloadPoolingButton').addEventListener('click', downloadPoolingAndDilutionFiles);

    // Custom Mutagenesis Event Listeners
    document.getElementById('customVariantType').addEventListener('change', updateCustomCurrentValue);
    document.getElementById('fastaInputCustom').addEventListener('input', updateCustomCurrentValue);
    document.getElementById('customPositionInput').addEventListener('input', updateCustomCurrentValue);
    document.getElementById('customNewValueInput').addEventListener('input', updateCustomRecap);
    document.getElementById('addMutationBtn').addEventListener('click', addCustomMutation);
    document.getElementById('mutationChips').addEventListener('click', (event) => {
        const removeButton = event.target.closest('.remove-btn');
        if (removeButton) {
            const indexToRemove = parseInt(removeButton.dataset.index, 10);
            customMutations.splice(indexToRemove, 1);
            renderCustomMutationChips();
        }
    });
    document.getElementById('generateCustomBtn').addEventListener('click', generateCustomSequences);
    document.getElementById('downloadCustomBtn').addEventListener('click', () => {
        const fastaContent = document.getElementById('resultsOutputCustom').value;
        if (!fastaContent) {
            showMessage('No sequences to download.', 'error');
            return;
        }
        downloadFile(fastaContent, 'custom_mutagenesis_library.fasta', 'text/fasta');
    });

    // Saturation Mutagenesis Event Listeners
    document.getElementById('satPositionInput').addEventListener('input', updateSatCurrentValueDisplay);
    document.getElementById('satVariantType').addEventListener('change', updateSatCurrentValueDisplay);
    document.getElementById('fastaInputSat').addEventListener('input', updateSatCurrentValueDisplay);
    document.getElementById('addSaturationMutationBtn').addEventListener('click', addSaturationMutation);
    document.getElementById('saturationMutationChips').addEventListener('click', (event) => {
        const removeButton = event.target.closest('.remove-btn');
        if (removeButton) {
            const indexToRemove = parseInt(removeButton.dataset.index, 10);
            saturationMutations.splice(indexToRemove, 1);
            renderSaturationMutationChips();
        }
    });
    document.getElementById('generateSatBtn').addEventListener('click', generateSaturationLibrary);
    document.getElementById('downloadSatBtn').addEventListener('click', () => {
        const fastaContent = document.getElementById('resultsOutputSat').value;
        if (!fastaContent) {
            showMessage('No sequences to download.', 'error');
            return;
        }
        downloadFile(fastaContent, 'saturation_library.fasta', 'text/fasta');
    });

    // Scanning Library Event Listeners
    document.getElementById('submitScanning').addEventListener('click', processScanningSequence);
    document.getElementById('transformToScanningLibraryBtn').addEventListener('click', transformToScanningLibrary);
    document.getElementById('downloadScanningResultsBtn').addEventListener('click', downloadScanningResults);

    // Setup file upload listeners
    setupFastaUploadAndPaste('fastaFileUploadSat', 'sequenceNameSat', 'fastaInputSat');
    setupFastaUploadAndPaste('fastaFileUploadCustom', 'sequenceNameCustom', 'fastaInputCustom');
    setupFastaUploadAndPaste('fastaFileScanning', 'sequenceNameScanning', 'sequenceScanning');

    // Initial checks for gapped oligo maker
    const gappedOligoMakerCheckbox = document.getElementById('gappedOligoMaker');
    const oligoLengthInput = document.getElementById('oligoLength');
    const overlapLengthInput = document.getElementById('overlapLength');
    const gapLengthGroup = document.getElementById('gapLength-group');
    const gapLengthInput = document.getElementById('gapLength');
    const simpleOligoMakerCheckbox = document.getElementById('simpleOligoMaker');
    const optimizedCheckbox = document.getElementById('optimizedOligos');
    const parameterGroup = document.getElementById('parameter-group');

    function updateGappedInputs() {
        if (gappedOligoMakerCheckbox.checked) {
            gapLengthGroup.style.display = 'flex';
            overlapLengthInput.readOnly = true;
            const oligoLength = parseInt(oligoLengthInput.value, 10);
            const gapLength = parseInt(gapLengthInput.value, 10);
            if (oligoLength > gapLength) {
                const calculatedOverlap = (oligoLength - gapLength) / 2;
                overlapLengthInput.value = Math.max(15, calculatedOverlap);
            } else {
                overlapLengthInput.value = 0;
            }
        } else {
            gapLengthGroup.style.display = 'none';
            overlapLengthInput.readOnly = false;
            overlapLengthInput.value = 30; // Restore default
        }
    }

    if (simpleOligoMakerCheckbox) {
        simpleOligoMakerCheckbox.addEventListener('change', function() {
            if (this.checked) {
                gappedOligoMakerCheckbox.checked = false;
            }
            updateGappedInputs();
        });
    }

    if (gappedOligoMakerCheckbox) {
        gappedOligoMakerCheckbox.addEventListener('change', function() {
            if (this.checked) {
                simpleOligoMakerCheckbox.checked = false;
            }
            updateGappedInputs();
        });
    }

    if (oligoLengthInput) {
        oligoLengthInput.addEventListener('input', updateGappedInputs);
    }
    if (gapLengthInput) {
        gapLengthInput.addEventListener('input', updateGappedInputs);
    }

    if (optimizedCheckbox) {
        optimizedCheckbox.addEventListener('change', function() {
            parameterGroup.style.display = this.checked ? 'flex' : 'none';
        });
    }

    if (gappedOligoMakerCheckbox) {
        updateGappedInputs();
    }
});