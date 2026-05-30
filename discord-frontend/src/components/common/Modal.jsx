// src/components/common/Modal.jsx
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { IoClose } from 'react-icons/io5';

function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50" onClick={onClose} />
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className={`fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 ${sizes[size]} w-full bg-[#2f3136] rounded-lg shadow-xl z-50`}
          >
            <div className="flex justify-between items-center p-4 border-b border-[#202225]">
              <h2 className="text-xl font-semibold text-white">{title}</h2>
              <button
                onClick={onClose}
                className="text-[#b9bbbe] hover:text-white transition-colors"
              >
                <IoClose size={24} />
              </button>
            </div>
            <div className="p-6">{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default Modal;