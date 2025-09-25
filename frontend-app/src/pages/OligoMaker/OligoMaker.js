import React, { useState } from 'react';

const API_BASE_URL = window.location.protocol + '//' + window.location.hostname + ':5001';

function OligoMaker() {
  const [sequence, setSequence] = useState('');
  const [oligoLength, setOligoLength] = useState(60);
  const [overlapLength, setOverlapLength] = useState(30);
  const [gapLength, setGapLength] = useState(20);
  const [wellFormat, setWellFormat] = useState('96-column');
  const [destinationFormat, setDestinationFormat] = useState('96-column');
  const [simpleOligoMaker, setSimpleOligoMaker] = useState(true);
  const [gappedOligoMaker, setGappedOligoMaker] = useState(false);
  const [cleanOligos, setCleanOligos] = useState(false);
  const [optimizedOligos, setOptimizedOligos] = useState(false);
  const [recycleOligos, setRecycleOligos] = useState(false);
  const [naConc, setNaConc] = useState(50);
  const [kConc, setKConc] = useState(0);
  const [oligoConc, setOligoConc] = useState(250);
  const [results, setResults] = useState('');

  const handleGenerateOligos = async () => {
    const payload = {
      sequence: sequence,
      oligo_length: oligoLength,
      overlap_length: overlapLength,
      gap_length: gapLength,
      na_conc: naConc,
      k_conc: kConc,
      oligo_conc: oligoConc,
      simple_oligo_maker: simpleOligoMaker,
      gapped_oligo_maker: gappedOligoMaker,
      clean_oligos: cleanOligos,
      optimized_oligos: optimizedOligos,
      recycle_oligos: recycleOligos,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/oligos/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(JSON.stringify(data, null, 2));
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
      <h2>Oligo Designer</h2>
      <div className="form-group">
        <label htmlFor="sequence">Sequences to Process:</label>
        <textarea id="sequence" placeholder="Your generated sequences are loaded here..." rows="6" value={sequence} onChange={(e) => setSequence(e.target.value)}></textarea>
      </div>
      <div className="grid-container">
        <div className="input-group">
          <div className="grid-item"><label htmlFor="oligoLength">Oligo Length:</label><input type="number" id="oligoLength" value={oligoLength} onChange={(e) => setOligoLength(e.target.value)} /></div>
          <div className="grid-item"><label htmlFor="overlapLength">Overlap Length:</label><input type="number" id="overlapLength" value={overlapLength} onChange={(e) => setOverlapLength(e.target.value)} /></div>
          <div className="grid-item" id="gapLength-group" style={{ display: gappedOligoMaker ? 'flex' : 'none' }}><label htmlFor="gapLength">Gap Length:</label><input type="number" id="gapLength" value={gapLength} onChange={(e) => setGapLength(e.target.value)} /></div>
        </div>
        <div className="format-group">
          <div className="grid-item"><label htmlFor="wellFormat">Source Plate:</label><select id="wellFormat" value={wellFormat} onChange={(e) => setWellFormat(e.target.value)}><optgroup label="Column-first"><option value="96-column">96-well</option><option value="384-column">384-well</option></optgroup><optgroup label="Row-first"><option value="96-row">96-well</option><option value="384-row">384-well</option></optgroup></select></div>
          <div className="grid-item"><label htmlFor="destinationFormat">Pooling To:</label><select id="destinationFormat" value={destinationFormat} onChange={(e) => setDestinationFormat(e.target.value)}><optgroup label="Column-first"><option value="96-column">96-well</option><option value="384-column">384-well</option></optgroup><optgroup label="Row-first"><option value="96-row">96-well</option><option value="384-row">384-well</option></optgroup></select></div>
        </div>
        <div className="engine-group">
          <div className="grid-item"><label htmlFor="simpleOligoMaker">Simple Oligos</label><input type="checkbox" id="simpleOligoMaker" checked={simpleOligoMaker} onChange={(e) => setSimpleOligoMaker(e.target.checked)} /></div>
          <div className="grid-item"><label htmlFor="gappedOligoMaker">Gapped Oligos</label><input type="checkbox" id="gappedOligoMaker" checked={gappedOligoMaker} onChange={(e) => setGappedOligoMaker(e.target.checked)} /></div>
          <div className="grid-item"><label htmlFor="cleanOligos">Trim Oligos</label><input type="checkbox" id="cleanOligos" checked={cleanOligos} onChange={(e) => setCleanOligos(e.target.checked)} /></div>
          <div className="grid-item"><label htmlFor="optimizedOligos">Optimize Oligos</label><input type="checkbox" id="optimizedOligos" checked={optimizedOligos} onChange={(e) => setOptimizedOligos(e.target.checked)} /></div>
          <div className="grid-item"><label htmlFor="recycleOligos">Recycle Oligos</label><input type="checkbox" id="recycleOligos" checked={recycleOligos} onChange={(e) => setRecycleOligos(e.target.checked)} /></div>
        </div>
      </div>
      <div id="parameter-group" className="flex-boxes_parameter-group" style={{ display: optimizedOligos ? 'flex' : 'none' }}>
        <label htmlFor="naConc">Na+ (mM):</label><input type="number" id="naConc" value={naConc} onChange={(e) => setNaConc(e.target.value)} />
        <label htmlFor="kConc">K+ (mM):</label><input type="number" id="kConc" value={kConc} onChange={(e) => setKConc(e.target.value)} />
        <label htmlFor="oligoConc">Oligo (nM):</label><input type="number" id="oligoConc" value={oligoConc} onChange={(e) => setOligoConc(e.target.value)} />
      </div>
      <div className="flex-box-button">
        <button id="generateOligosBtn" onClick={handleGenerateOligos}>Generate Oligos</button>
      </div>
      <div className="form-group" style={{ marginTop: '1.5rem' }}>
        <label htmlFor="results">Results:</label>
        <textarea id="results" placeholder="Output..." readOnly rows="8" value={results}></textarea>
      </div>
      <div className="button-group">
        <button id="downloadButton" style={{ display: 'none' }}>Download Oligo List</button>
        <button id="downloadPrimersButton" style={{ display: 'none' }}>Download Primers</button>
        <button id="downloadPoolingButton" style={{ display: 'none' }}>Download Pooling & Dilution Files</button>
      </div>
    </div>
  );
}

export default OligoMaker;
