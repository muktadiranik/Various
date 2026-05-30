// src/components/channel/ChannelHeader.jsx
import React from 'react';
import { useSelector } from 'react-redux';
import { IoMdSettings, IoMdPeople } from 'react-icons/io';

function ChannelHeader({ onOpenGuildSettings }) {
  const { selectedChannel } = useSelector((state) => state.channels);

  if (!selectedChannel) return null;

  return (
    <div className="h-12 flex items-center justify-between px-4 shadow-md border-b border-[#202225]">
      <div className="flex items-center">
        <span className="text-white font-semibold"># {selectedChannel.name}</span>
        {selectedChannel.topic && (
          <span className="ml-4 text-[#b9bbbe] text-sm truncate max-w-md">
            {selectedChannel.topic}
          </span>
        )}
      </div>
      
      <div className="flex items-center space-x-3">
        <button className="p-1 text-[#b9bbbe] hover:text-white transition-colors">
          <IoMdPeople size={20} />
        </button>
        <button 
          onClick={onOpenGuildSettings}
          className="p-1 text-[#b9bbbe] hover:text-white transition-colors"
        >
          <IoMdSettings size={20} />
        </button>
      </div>
    </div>
  );
}

export default ChannelHeader;