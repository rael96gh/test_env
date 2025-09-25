import React, { useState, useEffect } from 'react';

const API_BASE_URL = window.location.protocol + '//' + window.location.hostname + ':5001';

function ScanningLibrary() {
  const [fastaFile, setFastaFile] = useState(null);
  const [sequenceName, setSequenceName] = useState('');
  const [sequence, setSequence] = useState('');
  const [startPosition, setStartPosition] = useState('');
  const [endPosition, setEndPosition] = useState('');
  const [fullSequence, setFullSequence] = useState(false);
  const [libraryType, setLibraryType] = useState('NNN');
  const [results, setResults] = useState('');

  useEffect(() => {
    if (fastaFile) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSequence(e.target.result);
      };
      reader.readAsText(fastaFile);
    }
  }, [fastaFile]);

  const handleTransform = async () => {
    const payload = {
      sequence: sequence,
      sequence_name: sequenceName,
      start_position: startPosition,
      end_position: endPosition,
      full_sequence: fullSequence,
      library_type: libraryType,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/mutagenesis/scanning`, {
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
      <h2>Generate a Scanning Library</h2>

      <div className="fastauploadbutton">
        <label htmlFor="fastaFileScanning">Upload FASTA File:</label>
        <input type="file" id="fastaFileScanning" accept=".fasta, .fa, .txt" onChange={(e) => setFastaFile(e.target.files[0])} />
      </div>

      <label style={{ marginTop: '20px', marginBottom: '20px' }}>Or</label>

      <label htmlFor="sequenceNameScanning">Insert Sequence Name:</label>
      <textarea type="text" id="sequenceNameScanning" placeholder="Sequence Name" style={{ marginBottom: '20px' }} value={sequenceName} onChange={(e) => setSequenceName(e.target.value)}></textarea>

      <label htmlFor="sequenceScanning">Insert DNA Sequence (Fasta Format):</label>
      <textarea id="sequenceScanning" rows="4" placeholder="ATGCAG....." value={sequence} onChange={(e) => setSequence(e.target.value)}></textarea>

      <div className="grid-container" style={{ width: '800px' }}>
        <div className="input-group">
          <div className="grid-item">
            <label htmlFor="startPositionScanning">Start position:</label>
            <input type="number" id="startPositionScanning" placeholder="e.g. 2" value={startPosition} onChange={(e) => setStartPosition(e.target.value)} />
          </div>
          <div className="grid-item">
            <label htmlFor="endPositionScanning">Final position:</label>
            <input type="number" id="endPositionScanning" placeholder="e.g. 8" value={endPosition} onChange={(e) => setEndPosition(e.target.value)} />
          </div>
        </div>
        <div className="format-group" style={{ marginTop: '15px' }}>
          <div className="grid-item">
            <label htmlFor="fullSequenceScanning">Full Sequence</label>
            <input type="checkbox" id="fullSequenceScanning" checked={fullSequence} onChange={(e) => setFullSequence(e.target.checked)} />
          </div>
        </div>
        <div className="engine-group" style={{ marginTop: '5px' }}>
          <div className="grid-item">
            <label>
              <input type="radio" id="NNNScanning" name="libraryTypeScanning" value="NNN" checked={libraryType === 'NNN'} onChange={(e) => setLibraryType(e.target.value)} />
              NNN Library
            </label>
          </div>
          <div className="grid-item">
            <label>
              <input type="radio" id="NNKScanning" name="libraryTypeScanning" value="NNK" checked={libraryType === 'NNK'} onChange={(e) => setLibraryType(e.target.value)} />
              NNK Library
            </label>
          </div>
        </div>
      </div>

      <div className="flex-box-button">
        <button id="transformToScanningLibraryBtn" onClick={handleTransform}>Transform to Scanning Library</button>
        <button id="downloadScanningResultsBtn">Download Results</button>
      </div>

      <div className="sequence-length" id="sequenceLengthScanning" style={{ textAlign: 'center', marginBottom: '15px' }}></div>

      <label htmlFor="outputScanning">Results:</label>
      <textarea id="outputScanning" className="output" readOnly value={results}></textarea>
      <div id="errorMessageScanning" className="error"></div>
      <div className="button-group">
        <button id="feedScanningToOligoMakerBtn">Design Oligos for Library</button>
      </div>
    </div>
  );
}

export default ScanningLibrary;
