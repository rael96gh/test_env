/**
 * Main application entry point
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App_new';
import reportWebVitals from './reportWebVitals';

// Create root and render app
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Performance measurement
reportWebVitals(console.log);

// Register service worker for PWA (optional)
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}