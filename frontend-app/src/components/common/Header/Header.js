/**
 * Application header component
 */
import React from 'react';
import { useApp } from '../../../context/AppContext';
import './Header.css';

const Header = () => {
  const { theme, setTheme } = useApp();

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <header className="header">
      <div className="header__container">
        <div className="header__brand">
          <a href="https://www.oligotk.com" className="header__logo">
            <img src="/logo.png" alt="Oligo Toolkit" className="header__logo-img" />
          </a>
          <h1 className="header__title">Ramon ADN - Oligo Toolkit</h1>
        </div>

        <div className="header__actions">
          <button
            className="header__theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;