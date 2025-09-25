/**
 * Loading component
 */
import React from 'react';
import './Loading.css';

const Loading = ({
  size = 'medium',
  text = 'Loading...',
  overlay = false,
  className = ''
}) => {
  const loadingClass = [
    'loading',
    `loading--${size}`,
    overlay && 'loading--overlay',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={loadingClass}>
      <div className="loading__spinner"></div>
      {text && <div className="loading__text">{text}</div>}
    </div>
  );
};

export default Loading;