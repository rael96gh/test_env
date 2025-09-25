/**
 * Main App component with new architecture
 */
import React, { useState, useEffect } from 'react';
import { AppProvider } from './context/AppContext';
import Layout from './components/common/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import Button from './components/common/Button/Button';

// Import existing components (to be migrated)
import OligoMaker from './OligoMaker';
import SaturationMutagenesis from './SaturationMutagenesis';
import CustomMutagenesis from './CustomMutagenesis';
import ScanningLibrary from './ScanningLibrary';

// Import global styles
import './styles/globals.css';

function AppContent() {
  const [currentView, setCurrentView] = useState('dashboard');

  // Apply theme to document element
  useEffect(() => {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
  }, []);

  const handleNavigation = (view) => {
    setCurrentView(view);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'oligo':
        return <OligoMaker />;
      case 'saturation':
        return <SaturationMutagenesis />;
      case 'custom':
        return <CustomMutagenesis />;
      case 'scanning':
        return <ScanningLibrary />;
      case 'primers':
        return (
          <div className="text-center p-5">
            <h2>Primer Generation</h2>
            <p>Coming soon...</p>
          </div>
        );
      case 'recycle':
        return (
          <div className="text-center p-5">
            <h2>Oligo Recycling</h2>
            <p>Coming soon...</p>
          </div>
        );
      case 'dashboard':
      default:
        return <Dashboard onNavigate={handleNavigation} />;
    }
  };

  return (
    <Layout>
      {currentView !== 'dashboard' && (
        <div className="mb-4">
          <Button
            variant="secondary"
            onClick={handleBackToDashboard}
          >
            ← Back to Dashboard
          </Button>
        </div>
      )}

      {renderCurrentView()}
    </Layout>
  );
}

function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

export default App;