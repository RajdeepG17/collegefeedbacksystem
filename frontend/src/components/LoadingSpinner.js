import React from 'react';
import PropTypes from 'prop-types';
import './LoadingSpinner.css';

const LoadingSpinner = ({ size = 'medium', fullScreen = false }) => {
  const sizeClasses = {
    small: 'spinner-small',
    medium: 'spinner-medium',
    large: 'spinner-large'
  };

  const spinner = (
    <div className={`spinner-container ${sizeClasses[size]}`}>
      <div className="spinner">
        <div className="spinner-inner"></div>
      </div>
      <div className="spinner-text">Loading...</div>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fullscreen-spinner">
        {spinner}
      </div>
    );
  }

  return spinner;
};

LoadingSpinner.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  fullScreen: PropTypes.bool
};

export default LoadingSpinner; 