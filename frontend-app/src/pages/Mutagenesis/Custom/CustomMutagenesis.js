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

function CustomMutagenesis({ setView, setSequencesForOligoMaker }) {
    const [fastaFile, setFastaFile] = useState(null);
    const [sequenceName, setSequenceName] = useState('');
    const [fastaInput, setFastaInput] = useState('');
    const [variantType, setVariantType] = useState('AA');
    const [position, setPosition] = useState('');
    const [newValue, setNewValue] = useState('');
    const [mutations, setMutations] = useState([]);
    const [generationMode, setGenerationMode] = useState('group');
    const [results, setResults] = useState('');
    const [currentValue, setCurrentValue] = useState('-');
    const [includeOriginal, setIncludeOriginal] = useState(false);

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
                    sequence = lines.slice(1).join('').replace(/\s/g, '');
                } else {
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
    if (!position || !newValue) {
      alert('Please enter a position and a new value.');
      return;
    }
    const newMutation = { type: variantType, pos: parseInt(position), new: newValue.split(',') };
    setMutations([...mutations, newMutation]);
    setPosition('');
    setNewValue('');
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
    a.download = 'custom_mutagenesis_variants.fasta';
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
    const payload = {
      original_sequence: fastaInput,
      original_name: sequenceName,
      mutations: mutations,
      generation_mode: generationMode,
      include_original: includeOriginal, // Add this line
    };

    try {
      const data = await mutagenesisService.generateCustomMutagenesis(payload);
      if (data.success && data.variants && data.variants.length > 0) {
        setResults(data.variants.join('\n'));
      } else {
        setResults('No variants were generated for the given parameters.');
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  return (
    <div className="module-section">
      <h2>Custom Mutagenesis</h2>
      <div className="form-group">
        <label htmlFor="fastaFileUploadCustom">Upload FASTA File:</label>
        <input type="file" id="fastaFileUploadCustom" accept=".fasta, .fa, .txt" onChange={(e) => setFastaFile(e.target.files[0])} />
      </div>
      <label style={{ textAlign: 'left', marginBottom: '20px' }}>Or</label>
      <div className="form-group">
        <label htmlFor="sequenceNameCustom">Insert Sequence Name:</label>
        <textarea id="sequenceNameCustom" placeholder="Enter DNA sequence Name here..." rows="2" value={sequenceName} onChange={(e) => setSequenceName(e.target.value)}></textarea>
      </div>
      <div className="form-group">
        <label htmlFor="fastaInputCustom">Insert DNA Sequence (FASTA format):</label>
        <textarea id="fastaInputCustom" placeholder="ATGCATG....." rows="6" value={fastaInput} onChange={(e) => setFastaInput(e.target.value)}></textarea>
      </div>

      <div className="input-row">
        <label>Add Mutation</label>
        <select id="customVariantType" name="customVariantType" className="form-select" value={variantType} onChange={(e) => setVariantType(e.target.value)}>
          <option value="AA">Amino Acid</option>
          <option value="N">Nucleotide</option>
        </select>
        <label>Position</label>
        <input type="number" id="customPositionInput" placeholder="#" value={position} onChange={(e) => setPosition(e.target.value)} />
        <span id="customCurrentValueDisplay">{currentValue}</span>
        <label>Change to</label>
        <input type="text" id="customNewValueInput" placeholder="AA/N" value={newValue} onChange={(e) => setNewValue(e.target.value)} />
        <button id="addMutationBtn" onClick={handleAddMutation}>Add</button>
      </div>

      <div id="customMutationList" className="mt-4">
        <h4 className="text-sm font-semibold text-gray-600 mb-2" style={{marginLeft: '4px'}}>Mutations to Apply:</h4>
        <div id="mutationChips" className="flex flex-wrap gap-2">
          {mutations.map((mut, index) => (
            <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              {mut.type}:{mut.pos}:{mut.new.join(',')}
              <button onClick={() => handleRemoveMutation(index)} className="remove-btn">X</button>
            </span>
          ))}
        </div>
      </div>
      <div className="input-row" style={{ marginTop: '40px' }}>
        <label htmlFor="generationMode">Generation Mode:</label>
        <select id="generationMode" name="generationMode" className="form-select" style={{ width: 'auto' }} value={generationMode} onChange={(e) => setGenerationMode(e.target.value)}>
          <option value="group">Group Variations (Single Sequence)</option>
          <option value="individual">Individual Variations (Multiple Sequences)</option>
        </select>
      </div>

      <div className="checkboxgroup">
        <label htmlFor="includeOriginalSeqCustom" style={{fontSize: '16px'}}>Include Original Sequence</label>
        <input type="checkbox" id="includeOriginalSeqCustom" checked={includeOriginal} onChange={(e) => setIncludeOriginal(e.target.checked)} />
      </div>

      <button id="generateCustomBtn" style={{ marginTop: '30px' }} onClick={handleGenerate}>Generate Custom Sequence(s)</button>
      <div className="form-group" style={{ marginTop: '1.5rem' }}>
        <label htmlFor="resultsOutputCustom">Mutated Sequence</label>
        <textarea id="resultsOutputCustom" readOnly rows="8" value={results}></textarea>
      </div>
      <div className="button-group">
        <button id="feedCustomToOligoMakerBtn" onClick={handleDesignOligos}>Design Oligos for Library</button>
        <button id="downloadCustomBtn" onClick={handleDownloadFASTA}>Download as FASTA</button>
      </div>
    </div>
  );
}

export default CustomMutagenesis;
