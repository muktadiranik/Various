// src/components/common/Button.jsx
import React from 'react';

function Button({ children, variant = 'primary', size = 'md', loading = false, disabled = false, onClick, type = 'button', className = '' }) {
  const variants = {
    primary: 'bg-[#5865f2] hover:bg-[#4752c4] text-white',
    secondary: 'bg-[#4f545c] hover:bg-[#5d6269] text-white',
    danger: 'bg-[#ed4245] hover:bg-[#c03537] text-white',
    success: 'bg-[#3ba55d] hover:bg-[#2d7a46] text-white',
    ghost: 'bg-transparent hover:bg-[#4f545c] text-[#b9bbbe]',
  };

  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${variants[variant]} ${sizes[size]} rounded font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {loading ? (
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          Loading...
        </div>
      ) : (
        children
      )}
    </button>
  );
}

export default Button;