/**
 * Card UI component
 */
import React from 'react';
import './Card.css';

const Card = ({
  children,
  title,
  subtitle,
  icon,
  onClick,
  hoverable = false,
  className = '',
  headerActions,
  ...props
}) => {
  const cardClass = [
    'card',
    hoverable && 'card--hoverable',
    onClick && 'card--clickable',
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClass} onClick={onClick} {...props}>
      {(title || subtitle || icon || headerActions) && (
        <div className="card__header">
          <div className="card__header-content">
            {icon && <div className="card__icon">{icon}</div>}
            <div className="card__title-group">
              {title && <h3 className="card__title">{title}</h3>}
              {subtitle && <p className="card__subtitle">{subtitle}</p>}
            </div>
          </div>
          {headerActions && (
            <div className="card__header-actions">
              {headerActions}
            </div>
          )}
        </div>
      )}
      <div className="card__body">
        {children}
      </div>
    </div>
  );
};

export default Card;