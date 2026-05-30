// src/components/presence/OnlineStatus.jsx
import React from 'react';
import { useSelector } from 'react-redux';

function OnlineStatus({ userId }) {
  const { onlineUsers } = useSelector((state) => state.presence);
  const isOnline = onlineUsers[userId];

  return (
    <div className="relative">
      <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-[#3ba55d]' : 'bg-[#747f8d]'}`} />
    </div>
  );
}

export default OnlineStatus;