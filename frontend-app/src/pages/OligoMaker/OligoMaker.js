import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';

function OligoMaker({ sequencesForOligoMaker }) {
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
  const [oligoData, setOligoData] = useState([]);
  const [primerData, setPrimerData] = useState([]);
  const [generatedPrimersDict, setGeneratedPrimersDict] = useState({});
  const [showOligoDownload, setShowOligoDownload] = useState(false);
  const [showPrimerDownload, setShowPrimerDownload] = useState(false);
  const [showPoolingDownload, setShowPoolingDownload] = useState(false);
  const [groupedOligos, setGroupedOligos] = useState({});
  const [recycledPoolingData, setRecycledPoolingData] = useState(null);

  useEffect(() => {
    if (sequencesForOligoMaker) {
      setSequence(sequencesForOligoMaker);
    }
  }, [sequencesForOligoMaker]);

  const handleSimpleOligoMakerChange = (e) => {
    setSimpleOligoMaker(e.target.checked);
    if (e.target.checked) {
      setGappedOligoMaker(false);
    }
  };

  const handleGappedOligoMakerChange = (e) => {
    setGappedOligoMaker(e.target.checked);
    if (e.target.checked) {
      setSimpleOligoMaker(false);
    }
  };

  const handleCleanOligosChange = (e) => {
    setCleanOligos(e.target.checked);
    if (e.target.checked) {
      setOptimizedOligos(false);
    }
  };

  const handleOptimizedOligosChange = (e) => {
    setOptimizedOligos(e.target.checked);
    if (e.target.checked) {
      setCleanOligos(false);
    }
  };

  const downloadFile = (data, filename, type) => {
    const blob = new Blob([data], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadCSV = (data, filename) => {
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');

    downloadFile(csvContent, filename, 'text/csv;charset=utf-8;');
  };

  const handleDownloadOligos = () => {
    const flattenedOligos = Object.entries(groupedOligos).flatMap(([fragment, oligos]) => 
      oligos.map(oligo => ({
        Fragment: fragment,
        label: oligo.label,
        sequence: oligo.sequence,
        length: oligo.length,
      }))
    );
    downloadCSV(flattenedOligos, 'oligo_list.csv');
  };

  const handleDownloadPrimers = async () => {
    const generated_primers = primerData.reduce((acc, primer) => {
      if (!acc[primer.fragment]) {
        acc[primer.fragment] = {};
      }
      if (primer.name === 'forward_primer') {
        acc[primer.fragment].forward_primer = primer.sequence;
      } else if (primer.name === 'reverse_primer') {
        acc[primer.fragment].reverse_primer = primer.sequence;
      }
      return acc;
    }, {});

    const payload = {
      generated_primers: generated_primers,
      generated_oligos: oligoData,
      well_format: wellFormat,
      dest_well_format: destinationFormat,
      sequence_name: 'sequence',
    };

    try {
      await apiService.postAndDownloadFile('/downloads/download_primers_csv', payload, 'primer_pooling_file.csv');
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

  const handleDownloadPooling = async () => {
    if (recycledPoolingData) {
        downloadFile(recycledPoolingData, 'recycled_oligo_pooling_files.zip', 'application/zip');
        return;
    }

    const payload = {
      generated_oligos: oligoData,
      well_format: wellFormat,
      dest_well_format: destinationFormat,
    };

    try {
      await apiService.postAndDownloadFile('/downloads/pooling_files', payload, 'oligo_pooling_files.zip');
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  };

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
      const data = await apiService.post('/oligos/generate', payload);
      
      if (data.oligos && data.oligos.length > 0) {
        setOligoData(data.oligos);

        const indexNum = label => parseInt(label.split('_')[1], 10);
        const orientation = label => label.startsWith("FF") ? "FF" : "RC";

        const groups = {};
        data.oligos.forEach(o => {
            if (o.fragment) {
                if (!groups[o.fragment]) groups[o.fragment] = [];
                groups[o.fragment].push(o);
            }
        });

        const sortedGroups = {};
        Object.keys(groups).forEach(fragment => {
            const ff = groups[fragment]
                .filter(o => o.label && orientation(o.label) === "FF")
                .sort((a, b) => indexNum(a.label) - indexNum(b.label));
            const rc = groups[fragment]
                .filter(o => o.label && orientation(o.label) === "RC")
                .sort((a, b) => indexNum(a.label) - indexNum(b.label));
            
            const interlaced = [];
            const maxLength = Math.max(ff.length, rc.length);
            for (let i = 0; i < maxLength; i++) {
                if (ff[i]) {
                    interlaced.push(ff[i]);
                }
                if (rc[i]) {
                    interlaced.push(rc[i]);
                }
            }
            
            sortedGroups[fragment] = interlaced;
        });

        setGroupedOligos(sortedGroups);
        setShowOligoDownload(true);
        setShowPoolingDownload(true);
        setResults('');
      } else {
        setOligoData([]);
        setGroupedOligos({});
        setResults('No oligos were generated.');
        setShowOligoDownload(false);
        setShowPoolingDownload(false);
      }

      if (data.primers && data.primers.length > 0) {
        setPrimerData(data.primers);
        setShowPrimerDownload(true);
      } else {
        setShowPrimerDownload(false);
      }

      if (data.recycled_pooling_data) {
        setRecycledPoolingData(data.recycled_pooling_data);
      } else {
        setRecycledPoolingData(null);
      }

    } catch (error) {
      alert(`Error: ${error.message}`);
      setShowOligoDownload(false);
      setShowPrimerDownload(false);
      setShowPoolingDownload(false);
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
          <div className="grid-item"><label htmlFor="simpleOligoMaker">Simple Oligos</label><input type="checkbox" id="simpleOligoMaker" checked={simpleOligoMaker} onChange={handleSimpleOligoMakerChange} /></div>
          <div className="grid-item"><label htmlFor="gappedOligoMaker">Gapped Oligos</label><input type="checkbox" id="gappedOligoMaker" checked={gappedOligoMaker} onChange={handleGappedOligoMakerChange} /></div>
          <div className="grid-item"><label htmlFor="cleanOligos">Trim Oligos</label><input type="checkbox" id="cleanOligos" checked={cleanOligos} onChange={handleCleanOligosChange} /></div>
          <div className="grid-item"><label htmlFor="optimizedOligos">Optimize Oligos</label><input type="checkbox" id="optimizedOligos" checked={optimizedOligos} onChange={handleOptimizedOligosChange} /></div>
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
        {Object.keys(groupedOligos).length > 0 ? (
          <div className="results-container" style={{ border: '1px solid #ccc', padding: '10px', borderRadius: '5px', maxHeight: '300px', overflowY: 'auto' }}>
            {Object.entries(groupedOligos).map(([fragment, oligos]) => (
              <div key={fragment} className="sequence-group" style={{ marginBottom: '15px' }}>
                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '5px', marginBottom: '5px' }}> {fragment}</h4>
                <ul style={{ listStyleType: 'none', paddingLeft: '0' }}>
                  {oligos.map((oligo) => (
                    <li key={oligo.label} style={{ marginBottom: '5px' }}>
                      <strong style={{ minWidth: '100px', display: 'inline-block' }}>{oligo.label}:</strong>
                      <span>{oligo.sequence}</span>
                      <span style={{ color: '#888', marginLeft: '10px' }}>({oligo.length}nt)</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (

          <textarea id="results" placeholder="Output..." readOnly rows="8" value={results}></textarea>
        )}
      </div>
      <div className="button-group">
        <button id="downloadButton" style={{ display: showOligoDownload ? 'inline-block' : 'none' }} onClick={handleDownloadOligos}>Download Oligo List</button>
        <button id="downloadPrimersButton" style={{ display: showPrimerDownload ? 'inline-block' : 'none' }} onClick={handleDownloadPrimers}>Download Primers</button>
        <button id="downloadPoolingButton" style={{ display: showPoolingDownload ? 'inline-block' : 'none' }} onClick={handleDownloadPooling}>Download Pooling & Dilution Files</button>
      </div>
    </div>
  );
}

export default OligoMaker; 