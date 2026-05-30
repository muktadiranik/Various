// src/components/common/LoadingSpinner.jsx
import React from 'react';

function LoadingSpinner({ size = 'md' }) {
  const sizes = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12',
    lg: 'h-16 w-16',
  };

  return (
    <div className="flex items-center justify-center">
      <div className={`${sizes[size]} animate-spin rounded-full border-4 border-[#5865f2] border-t-transparent`} />
    </div>
  );
}

export default LoadingSpinner;