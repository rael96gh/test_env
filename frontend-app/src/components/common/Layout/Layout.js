/**
 * Main layout component
 */
import React from 'react';
import Header from '../Header/Header';
import './Layout.css';

const Layout = ({ children }) => {
  return (
    <div className="layout">
      <Header />
      <main className="layout__main">
        <div className="layout__container">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;