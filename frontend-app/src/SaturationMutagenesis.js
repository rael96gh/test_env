import React, { useState, useEffect } from 'react';

const API_BASE_URL = window.location.protocol + '//' + window.location.hostname + ':5001';

function SaturationMutagenesis() {
  const [fastaFile, setFastaFile] = useState(null);
  const [sequenceName, setSequenceName] = useState('');
  const [fastaInput, setFastaInput] = useState('');
  const [variantType, setVariantType] = useState('AA');
  const [position, setPosition] = useState('');
  const [excludeStops, setExcludeStops] = useState(true);
  const [mutations, setMutations] = useState([]);
  const [results, setResults] = useState('');

  useEffect(() => {
    if (fastaFile) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setFastaInput(e.target.result);
      };
      reader.readAsText(fastaFile);
    }
  }, [fastaFile]);

  const handleAddMutation = () => {
    if (!position) {
      alert('Please enter a position.');
      return;
    }
    const newMutation = { type: variantType, pos: parseInt(position) };
    setMutations([...mutations, newMutation]);
    setPosition('');
  };

  const handleDownloadFASTA = () => {
    if (!results) {
      alert('No results to download. Please generate variants first.');
      return;
    }

    const blob = new Blob([results], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'saturation_mutagenesis_variants.fasta';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDesignOligos = async () => {
    if (!results) {
      alert('No variants available. Please generate variants first.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/oligos/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sequence: results,
          oligo_length: 60,
          overlap_length: 30,
          gap_length: 20,
          simple_oligo_maker: true,
          na_conc: 50,
          k_conc: 0,
          oligo_conc: 250
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Oligos designed:', data);
        // You could open a new tab or show results in a modal
        alert(`${data.oligos?.length || 0} oligos designed successfully!`);
      } else {
        const errorData = await response.json();
        alert(`Error designing oligos: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  const handleGenerate = async () => {
    const payload = {
      fasta_content: fastaInput,
      saturation_mutations: mutations,
      exclude_stops: excludeStops,
    };

    // DEBUG: Log what we're sending
    console.log('🚀 FRONTEND - Sending payload:');
    console.log('fastaInput:', fastaInput);
    console.log('mutations:', mutations);
    console.log('excludeStops:', excludeStops);
    console.log('Full payload:', JSON.stringify(payload, null, 2));

    try {
      const response = await fetch(`${API_BASE_URL}/api/mutagenesis/saturation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      // DEBUG: Log response status
      console.log('📡 FRONTEND - Response status:', response.status);
      console.log('📡 FRONTEND - Response OK:', response.ok);

      if (response.ok) {
        const data = await response.json();

        // DEBUG: Log successful response
        console.log('✅ FRONTEND - Success response:', data);
        console.log('✅ FRONTEND - Data type:', typeof data);
        console.log('✅ FRONTEND - Is array:', Array.isArray(data));

        // Handle new API response format
        if (data.success && data.variants) {
          console.log('✅ FRONTEND - Using new format, variants count:', data.variants.length);
          setResults(data.variants.join('\n'));
        } else if (Array.isArray(data)) {
          // Fallback for old format
          console.log('✅ FRONTEND - Using old format, data count:', data.length);
          setResults(data.join('\n'));
        } else {
          console.log('⚠️ FRONTEND - No variants found in response');
          setResults('No variants generated');
        }
      } else {
        const errorData = await response.json();

        // DEBUG: Log error response
        console.log('❌ FRONTEND - Error response:', errorData);

        const errorMessage = errorData.error || errorData.message || 'Unknown error occurred';
        alert(`Error: ${errorMessage}`);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div className="module-section">
      <h2>Saturation Mutagenesis</h2>
      <div className="form-group">
        <label htmlFor="fastaFileUploadSat">Upload FASTA File:</label>
        <input type="file" id="fastaFileUploadSat" accept=".fasta, .fa, .txt" onChange={(e) => setFastaFile(e.target.files[0])} />
      </div>
      <label style={{ textAlign: 'left', marginBottom: '20px' }}>Or</label>
      <div className="form-group">
        <label htmlFor="sequenceNameSat">Insert Sequence Name:</label>
        <textarea id="sequenceNameSat" placeholder="Enter DNA sequence Name here..." rows="2" value={sequenceName} onChange={(e) => setSequenceName(e.target.value)}></textarea>
      </div>
      <div className="form-group">
        <label htmlFor="fastaInputSat">Insert DNA Sequence (FASTA format):</label>
        <textarea id="fastaInputSat" placeholder="ATGCATG....." rows="6" value={fastaInput} onChange={(e) => setFastaInput(e.target.value)}></textarea>
      </div>

      <div className="input-row">
        <label>Add Variant</label>
        <select id="satVariantType" name="satVariantType" className="form-select" value={variantType} onChange={(e) => setVariantType(e.target.value)}>
          <option value="AA">Amino Acid</option>
          <option value="N">Nucleotide</option>
        </select>
        <label>Position</label>
        <input type="number" id="satPositionInput" placeholder="#" value={position} onChange={(e) => setPosition(e.target.value)} />
        <span id="satCurrentValueDisplay">-</span>

        <label htmlFor="excludeStopCodonsSat">Exclude STOP codons</label>
        <div className="form-group grid-item" style={{ marginTop: '10px' }}>
          <input type="checkbox" id="excludeStopCodonsSat" checked={excludeStops} onChange={(e) => setExcludeStops(e.target.checked)} />
        </div>

        <button id="addSaturationMutationBtn" onClick={handleAddMutation}>Add</button>
      </div>

      <div id="saturationMutationList" className="mt-4">
        <h4 className="text-sm font-semibold text-gray-600 mb-2">Variant Positions to Apply:</h4>
        <div id="saturationMutationChips" className="flex flex-wrap gap-2">
          {mutations.map((mut, index) => (
            <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              {mut.type}:{mut.pos}
            </span>
          ))}
        </div>
      </div>

      <button id="generateSatBtn" onClick={handleGenerate}>Generate Saturation Library</button>
      <div className="form-group" style={{ marginTop: '1.5rem' }}>
        <label htmlFor="resultsOutputSat">Generated Library</label>
        <textarea id="resultsOutputSat" readOnly rows="8" value={results}></textarea>
      </div>
      <div className="button-group">
        <button id="feedSatToOligoMakerBtn" onClick={handleDesignOligos}>Design Oligos for Library</button>
        <button id="downloadSatBtn" onClick={handleDownloadFASTA}>Download as FASTA</button>
      </div>
    </div>
  );
}

export default SaturationMutagenesis;
