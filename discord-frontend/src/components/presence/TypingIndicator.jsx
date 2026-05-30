// src/components/presence/TypingIndicator.jsx
import React from 'react';

function TypingIndicator({ users }) {
  if (!users || users.length === 0) return null;

  let text = '';
  if (users.length === 1) {
    text = `${users[0].username} is typing...`;
  } else if (users.length === 2) {
    text = `${users[0].username} and ${users[1].username} are typing...`;
  } else if (users.length === 3) {
    text = `${users[0].username}, ${users[1].username} and 1 other are typing...`;
  } else {
    text = `${users.length} people are typing...`;
  }

  return (
    <div className="flex items-center space-x-2 text-[#b9bbbe] text-sm py-2">
      <div className="flex space-x-1">
        <div className="w-1 h-1 bg-[#b9bbbe] rounded-full animate-pulse"></div>
        <div className="w-1 h-1 bg-[#b9bbbe] rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-1 h-1 bg-[#b9bbbe] rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
      </div>
      <span>{text}</span>
    </div>
  );
}

export default TypingIndicator;