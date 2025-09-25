import React, { useState } from 'react';
import SaturationMutagenesis from './SaturationMutagenesis';
import CustomMutagenesis from './CustomMutagenesis';
import ScanningLibrary from './ScanningLibrary';
import OligoMaker from './OligoMaker';
import './App.css';

function App() {
  const [view, setView] = useState('dashboard');

  const renderView = () => {
    switch (view) {
      case 'saturation':
        return <SaturationMutagenesis />;
      case 'custom':
        return <CustomMutagenesis />;
      case 'scanning':
        return <ScanningLibrary />;
      case 'oligo':
        return <OligoMaker />;
      default:
        return (
          <div id="dashboardView">
            <h2 style={{ textAlign: 'center', paddingBottom: '10px' }}>Select a tool to get started.</h2>
            <div className="dashboard-cards">
              <div id="satCard" className="card" onClick={() => setView('saturation')}>
                <div className="emoji">🧬</div>
                <h2>Saturation Mutagenesis</h2>
                <p>Create a library of every possible codon variant.</p>
              </div>
              <div id="customCard" className="card" onClick={() => setView('custom')}>
                <div className="emoji">✍️</div>
                <h2>Custom Mutagenesis</h2>
                <p>Generate specific point mutations.</p>
              </div>
              <div id="scanningCard" className="card" onClick={() => setView('scanning')}>
                <div className="emoji">𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃</div>
                <h2>Scanning Mutagenesis</h2>
                <p>Generate codon scanning mutations.</p>
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="container" style={{ maxWidth: '2500px' }}>
      <a href="https://www.oligotk.com"><img src="/logo.png" width="15%" height="15%" alt="Your Logo" /></a>
      <h1>Variant DNA Library Modules</h1>
      {view !== 'dashboard' && <button onClick={() => setView('dashboard')}>&lt; Back to Dashboard</button>}
      {renderView()}
    </div>
  );
}

export default App;
