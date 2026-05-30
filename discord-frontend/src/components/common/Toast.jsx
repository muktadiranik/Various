// src/components/common/Toast.jsx
import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { IoClose, IoCheckmarkCircle, IoWarning, IoInformation } from 'react-icons/io5';

function Toast({ message, type = 'info', onClose, duration = 3000 }) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: <IoCheckmarkCircle className="text-[#3ba55d]" size={20} />,
    error: <IoWarning className="text-[#ed4245]" size={20} />,
    info: <IoInformation className="text-[#5865f2]" size={20} />,
    warning: <IoWarning className="text-[#faa81a]" size={20} />,
  };

  const backgrounds = {
    success: 'bg-[#3ba55d]',
    error: 'bg-[#ed4245]',
    info: 'bg-[#5865f2]',
    warning: 'bg-[#faa81a]',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      className={`fixed bottom-4 right-4 z-50 flex items-center space-x-3 px-4 py-3 rounded-lg shadow-lg ${backgrounds[type]} text-white`}
    >
      {icons[type]}
      <span className="text-sm">{message}</span>
      <button onClick={onClose} className="hover:opacity-70">
        <IoClose size={16} />
      </button>
    </motion.div>
  );
}

export default Toast;