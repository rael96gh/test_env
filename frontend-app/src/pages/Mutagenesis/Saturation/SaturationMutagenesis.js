import React, { useState, useEffect } from 'react';
import { mutagenesisService } from '../../../services/mutagenesis';
import '../Mutagenesis.css';

const codonTable = {
  'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
  'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
  'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
  'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
  'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
  'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
  'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
  'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
  'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
  'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
  'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
  'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
  'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
  'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
  'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
  'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
};

function SaturationMutagenesis({ setView, setSequencesForOligoMaker }) {
  const [fastaFile, setFastaFile] = useState(null);
  const [sequenceName, setSequenceName] = useState('');
  const [fastaInput, setFastaInput] = useState('');
  const [variantType, setVariantType] = useState('AA');
  const [position, setPosition] = useState('');
  const [excludeStops, setExcludeStops] = useState(true);
  const [includeOriginal, setIncludeOriginal] = useState(false);
  const [generationMode, setGenerationMode] = useState('individual');
  const [mutations, setMutations] = useState([]);
  const [results, setResults] = useState('');
  const [currentValue, setCurrentValue] = useState('-');

  useEffect(() => {
    if (fastaFile) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target.result;
        const lines = content.split('\n');
        let name = '';
        let sequence = '';

        if (lines.length > 0 && lines[0].startsWith('>')) {
          name = lines[0].substring(1).trim();
          sequence = lines.slice(1).join('').replace(/\s/g, ''); // Join lines and remove all whitespace
        } else {
          // Not a FASTA file or no header, treat the whole content as sequence
          sequence = content.replace(/\s/g, '');
        }

        setSequenceName(name);
        setFastaInput(sequence);
      };
      reader.readAsText(fastaFile);
    }
  }, [fastaFile]);

  useEffect(() => {
    if (position > 0 && fastaInput) {
      const sequence = fastaInput.replace(/\s/g, '');
      if (variantType === 'N') {
        if (position <= sequence.length) {
          setCurrentValue(sequence[position - 1]);
        } else {
          setCurrentValue('-');
        }
      } else if (variantType === 'AA') {
        const codonStart = (position - 1) * 3;
        if (codonStart + 3 <= sequence.length) {
          const codon = sequence.substring(codonStart, codonStart + 3).toUpperCase();
          setCurrentValue(codonTable[codon] || '-');
        } else {
          setCurrentValue('-');
        }
      }
    } else {
      setCurrentValue('-');
    }
  }, [position, variantType, fastaInput]);

  const handleAddMutation = () => {
    if (!position) {
      alert('Please enter a position.');
      return;
    }
    const newMutation = { type: variantType, pos: parseInt(position) };
    setMutations([...mutations, newMutation]);
    setPosition('');
  };

  const handleRemoveMutation = (indexToRemove) => {
    setMutations(mutations.filter((_, index) => index !== indexToRemove));
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

  const handleDesignOligos = () => {
    if (!results) {
      alert('No variants available. Please generate variants first.');
      return;
    }
    setSequencesForOligoMaker(results);
    setView('oligo');
  };

  const handleGenerate = async () => {
    let finalFastaContent = fastaInput;
    if (!fastaInput.trim().startsWith('>') && sequenceName) {
      finalFastaContent = `>${sequenceName}\n${fastaInput}`;
    }

    const payload = {
      fasta_content: finalFastaContent,
      saturation_mutations: mutations,
      exclude_stops: excludeStops,
      include_original: includeOriginal,
      generation_mode: generationMode,
    };

    // DEBUG: Log what we're sending
    console.log('🚀 FRONTEND - Sending payload:');
    console.log('fastaInput:', fastaInput);
    console.log('mutations:', mutations);
    console.log('excludeStops:', excludeStops);
    console.log('Full payload:', JSON.stringify(payload, null, 2));

    try {
      const data = await mutagenesisService.generateSaturationMutagenesis(payload);

      // DEBUG: Log successful response
      console.log('✅ FRONTEND - Success response:', data);
      console.log('✅ FRONTEND - Data type:', typeof data);
      console.log('✅ FRONTEND - Is array:', Array.isArray(data));

      // Handle API response
      if (data.success && data.variants && data.variants.length > 0) {
        console.log('✅ FRONTEND - Using new format, variants count:', data.variants.length);
        setResults(data.variants.join('\n'));
      } else {
        console.log('⚠️ FRONTEND - No variants found in response');
        setResults('No variants were generated for the given parameters.');
      }
    } catch (error) {
        const errorMessage = error.message || 'Unknown error occurred';
        alert(`Error: ${errorMessage}`);
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
        <span id="satCurrentValueDisplay">{currentValue}</span>

        {variantType === 'AA' && (
          <div className="form-group grid-item" style={{ marginTop: '20px'}}>
            <label htmlFor="excludeStopCodonsSat" style={{ fontSize: '15px', marginLeft: '10px', marginRight: '10px'}}>Exclude STOP codons</label>
            <input type="checkbox" id="excludeStopCodonsSat" checked={excludeStops} onChange={(e) => setExcludeStops(e.target.checked)} />
          </div>
        )}

        <button id="addSaturationMutationBtn" onClick={handleAddMutation}>Add</button>
      </div>

      <div id="saturationMutationList" className="mt-4">
        <h4 className="text-sm font-semibold text-gray-600 mb-2" style={{marginLeft: '4px'}}>Variant Positions to Apply:</h4>
        <div id="saturationMutationChips" className="flex flex-wrap gap-2">
          {mutations.map((mut, index) => (
            <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              {mut.type}:{mut.pos}
              <button onClick={() => handleRemoveMutation(index)} className="remove-btn">X</button>
            </span>
          ))}
        </div>
      </div>

      <div className="input-row" style={{ marginTop: '60px' }}>
        <label htmlFor="generationMode">Generation Mode:</label>
        <select id="generationMode" name="generationMode" className="form-select" style={{ width: 'auto' }} value={generationMode} onChange={(e) => setGenerationMode(e.target.value)}>
          <option value="individual">Individual Variations</option>
          <option value="group">Combinatorial (Full Library)</option>
          <option value="group_degenerate">Combinatorial (NNK Template)</option>
        </select>
      </div>

      <div className="checkboxgroup">
        <label htmlFor="includeOriginalSeq" style={{fontSize: '16px'}}>Include Original Sequence</label>
        <input type="checkbox" id="includeOriginalSeq" checked={includeOriginal} onChange={(e) => setIncludeOriginal(e.target.checked)} />
      </div>

      <button id="generateSatBtn" onClick={handleGenerate} style={{ marginTop: '60px' }}>Generate Saturation Library</button>
      <div className="form-group" style={{ marginTop: '40px' }}>
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
