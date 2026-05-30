// src/components/channel/ChannelList.jsx
import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { selectChannel } from '../../store/slices/channelSlice';
import { fetchMessages, clearMessages } from '../../store/slices/messageSlice';
import CreateChannelModal from './CreateChannelModal';
import { IoAdd, IoChevronDown, IoChevronUp, IoVolumeHigh, IoChatbubbles } from 'react-icons/io5';

function ChannelList() {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const { list: channels, selectedChannel } = useSelector((state) => state.channels);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState({ text: true, voice: true });

  const handleSelectChannel = (channel) => {
    if (channel.type === 'text') {
      dispatch(selectChannel(channel));
      dispatch(clearMessages(channel.id));
      dispatch(fetchMessages({ channelId: channel.id, limit: 50 }));
    }
  };

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const textChannels = channels.filter(c => c.type === 'text');
  const voiceChannels = channels.filter(c => c.type === 'voice');

  if (!selectedGuild) {
    return (
      <div className="w-60 bg-[#2f3136] flex flex-col">
        <div className="h-12 flex items-center px-4 shadow-md">
          <button className="text-white font-semibold">No Server Selected</button>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <p className="text-[#b9bbbe] text-sm">Select a server</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="w-60 bg-[#2f3136] flex flex-col">
        <div className="h-12 flex items-center px-4 shadow-md">
          <button className="text-white font-semibold hover:text-[#b9bbbe] truncate">
            {selectedGuild?.name || 'No Server Selected'}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {/* Text Channels Section */}
          <div className="mb-4">
            <button
              onClick={() => toggleCategory('text')}
              className="flex items-center w-full text-[#8e9297] hover:text-[#b9bbbe] text-xs font-semibold uppercase mb-1"
            >
              {expandedCategories.text ? <IoChevronDown size={12} /> : <IoChevronUp size={12} />}
              <span className="ml-1">Text Channels</span>
            </button>
            
            {expandedCategories.text && (
              <div className="space-y-0.5">
                {textChannels.map((channel) => (
                  <button
                    key={channel.id}
                    onClick={() => handleSelectChannel(channel)}
                    className={`flex items-center w-full px-2 py-1 rounded text-sm transition-colors ${
                      selectedChannel?.id === channel.id
                        ? 'bg-[#4f545c] text-white'
                        : 'text-[#8e9297] hover:bg-[#4f545c] hover:text-[#dcddde]'
                    }`}
                  >
                    <IoChatbubbles size={18} className="mr-2" />
                    <span className="truncate">{channel.name}</span>
                  </button>
                ))}
                
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="flex items-center w-full px-2 py-1 rounded text-sm text-[#8e9297] hover:bg-[#4f545c] hover:text-[#dcddde] transition-colors"
                >
                  <IoAdd size={18} className="mr-2" />
                  <span>Create Channel</span>
                </button>
              </div>
            )}
          </div>

          {/* Voice Channels Section */}
          {voiceChannels.length > 0 && (
            <div>
              <button
                onClick={() => toggleCategory('voice')}
                className="flex items-center w-full text-[#8e9297] hover:text-[#b9bbbe] text-xs font-semibold uppercase mb-1"
              >
                {expandedCategories.voice ? <IoChevronDown size={12} /> : <IoChevronUp size={12} />}
                <span className="ml-1">Voice Channels</span>
              </button>
              
              {expandedCategories.voice && (
                <div className="space-y-0.5">
                  {voiceChannels.map((channel) => (
                    <div
                      key={channel.id}
                      className="flex items-center px-2 py-1 rounded text-sm text-[#8e9297]"
                    >
                      <IoVolumeHigh size={18} className="mr-2" />
                      <span className="truncate">{channel.name}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <CreateChannelModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />
    </>
  );
}

export default ChannelList;