import React, { useState, useEffect } from 'react';

const API_BASE_URL = window.location.protocol + '//' + window.location.hostname + ':5001';

function CustomMutagenesis() {
  const [fastaFile, setFastaFile] = useState(null);
  const [sequenceName, setSequenceName] = useState('');
  const [fastaInput, setFastaInput] = useState('');
  const [variantType, setVariantType] = useState('AA');
  const [position, setPosition] = useState('');
  const [newValue, setNewValue] = useState('');
  const [mutations, setMutations] = useState([]);
  const [generationMode, setGenerationMode] = useState('group');
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
    if (!position || !newValue) {
      alert('Please enter a position and a new value.');
      return;
    }
    const newMutation = { type: variantType, pos: parseInt(position), new: newValue.split(',') };
    setMutations([...mutations, newMutation]);
    setPosition('');
    setNewValue('');
  };

  const handleGenerate = async () => {
    const payload = {
      original_sequence: fastaInput,
      original_name: sequenceName,
      mutations: mutations,
      generation_mode: generationMode,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/mutagenesis/custom`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data.join('\n'));
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
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
        <label>Change to</label>
        <input type="text" id="customNewValueInput" placeholder="AA/N" value={newValue} onChange={(e) => setNewValue(e.target.value)} />
        <button id="addMutationBtn" onClick={handleAddMutation}>Add</button>
      </div>

      <div id="customMutationList" className="mt-4">
        <h4 className="text-sm font-semibold text-gray-600 mb-2">Mutations to Apply:</h4>
        <div id="mutationChips" className="flex flex-wrap gap-2">
          {mutations.map((mut, index) => (
            <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              {mut.type}:{mut.pos}:{mut.new.join(',')}
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
      <button id="generateCustomBtn" style={{ marginTop: '30px' }} onClick={handleGenerate}>Generate Custom Sequence(s)</button>
      <div className="form-group" style={{ marginTop: '1.5rem' }}>
        <label htmlFor="resultsOutputCustom">Mutated Sequence</label>
        <textarea id="resultsOutputCustom" readOnly rows="8" value={results}></textarea>
      </div>
      <div className="button-group">
        <button id="feedCustomToOligoMakerBtn">Design Oligos for Library</button>
        <button id="downloadCustomBtn">Download as FASTA</button>
      </div>
    </div>
  );
}

export default CustomMutagenesis;
