import React, { useState, useEffect } from 'react';
import { mutagenesisService } from '../../../services/mutagenesis';
import '../Mutagenesis.css';

function ScanningLibrary({ setView, setSequencesForOligoMaker }) {
  const [fastaFile, setFastaFile] = useState(null);
  const [sequenceName, setSequenceName] = useState('');
  const [sequence, setSequence] = useState('');
  const [startPosition, setStartPosition] = useState('');
  const [endPosition, setEndPosition] = useState('');
  const [fullSequence, setFullSequence] = useState(false);
  const [libraryType, setLibraryType] = useState('NNN');
  const [results, setResults] = useState('');
  const [includeOriginal, setIncludeOriginal] = useState(false);

  useEffect(() => {
    if (fastaFile) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target.result;
        const lines = content.split('\n');
        let name = '';
        let seq = '';

        if (lines.length > 0 && lines[0].startsWith('>')) {
          name = lines[0].substring(1).trim();
          seq = lines.slice(1).join('').replace(/\s/g, '');
        } else {
          seq = content.replace(/\s/g, '');
        }

        setSequenceName(name);
        setSequence(seq);
      };
      reader.readAsText(fastaFile);
    }
  }, [fastaFile]);

  const handleGenerate = async () => {
    let finalFastaContent = sequence;
    if (!sequence.trim().startsWith('>') && sequenceName) {
        finalFastaContent = `>${sequenceName}\n${sequence}`;
    }

    const payload = {
      fasta_content: finalFastaContent,
      start_position: startPosition,
      end_position: endPosition,
      full_sequence: fullSequence,
      library_type: libraryType,
      include_original: includeOriginal,
    };

    try {
      const data = await mutagenesisService.generateScanningLibrary(payload);
      if (data.success && data.variants && data.variants.length > 0) {
          setResults(data.variants.join('\n'));
      } else {
          setResults('No variants were generated for the given parameters.');
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
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
    a.download = 'scanning_library.fasta';
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

      <div className="checkboxgroup">
        <label htmlFor="includeOriginalSeqScanning" style={{fontSize: '16px'}}>Include Original Sequence</label>
        <input type="checkbox" id="includeOriginalSeqScanning" checked={includeOriginal} onChange={(e) => setIncludeOriginal(e.target.checked)} />
      </div>

      <div className="flex-box-button">
        <button id="transformToScanningLibraryBtn" onClick={handleGenerate}>Generate Scanning Library</button>
        <button id="downloadScanningResultsBtn" onClick={handleDownloadFASTA}>Download Results</button>
      </div>

      <div className="sequence-length" id="sequenceLengthScanning" style={{ textAlign: 'center', marginBottom: '15px' }}></div>

      <label htmlFor="outputScanning">Results:</label>
      <textarea id="outputScanning" className="output" readOnly value={results}></textarea>
      <div id="errorMessageScanning" className="error"></div>
      <div className="button-group">
        <button id="feedScanningToOligoMakerBtn" onClick={handleDesignOligos}>Design Oligos for Library</button>
      </div>
    </div>
  );
}

export default ScanningLibrary;
